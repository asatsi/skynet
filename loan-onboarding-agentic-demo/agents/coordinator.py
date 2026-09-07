"""
BFSI Loan Onboarding Copilot — LangGraph Coordinator
Correct architecture: UI → Agent Server → LangGraph Nodes → MCP Servers (SSE) → Spring Boot
"""
import re, json, httpx
from typing import Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from mcp.client.sse import sse_client
from mcp import ClientSession

from agents.state import LoanState
from agents.config import (
    OLLAMA_URL, OLLAMA_MODEL, INTENT_AGENT_MAP,
    MCP_CUSTOMER, MCP_KYC, MCP_DOCUMENT,
    MCP_RISK, MCP_WORKFLOW, MCP_KNOWLEDGE,
    LOAN_SERVICE,
)

# ── MCP SSE tool caller ────────────────────────────────────────────────────────
async def call_mcp_tool(mcp_url: str, tool_name: str, arguments: dict) -> Any:
    """Call a tool on an MCP server via the SSE/MCP protocol."""
    try:
        async with sse_client(mcp_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                if result.content:
                    text = result.content[0].text
                    try:
                        return json.loads(text)
                    except Exception:
                        return text
                return None
    except Exception as e:
        return {"error": f"MCP call failed ({mcp_url} → {tool_name}): {e}"}

MCP_URL_MAP = {
    "customer":  MCP_CUSTOMER,
    "kyc":       MCP_KYC,
    "document":  MCP_DOCUMENT,
    "risk":      MCP_RISK,
    "workflow":  MCP_WORKFLOW,
    "knowledge": MCP_KNOWLEDGE,
}

# ── Error-detection helpers ───────────────────────────────────────────────────
def _is_error(val) -> bool:
    """True when a tool result signals an error, 404, or not-found.

    IMPORTANT: checks must NOT produce false-positives on valid entity data.
    e.g. annualRevenue=8500000 contains "500", loanId=404 contains "404" —
    so we never substring-search the whole dict string for these patterns.
    """
    if val is None:
        return True

    # ── Dict: check HTTP status code and Spring Boot error shape only ──────────
    if isinstance(val, dict):
        # Spring Boot error response: {"status": 5xx/4xx, "error":"...", "timestamp":"..."}
        # Valid entities also have "status" but as a string e.g. "ACTIVE"
        raw_status = val.get("status", 0)
        try:
            http_status = int(raw_status)   # "ACTIVE" → ValueError → 0
        except (ValueError, TypeError):
            http_status = 0
        if http_status >= 400:
            return True
        # Spring Boot error shape always has "error" AND "timestamp" together
        if "error" in val and "timestamp" in val:
            return True
        # Error in the "message" field (e.g. "Loan not found: 99")
        msg = str(val.get("message") or "").lower()
        if "not found" in msg or "does not exist" in msg or "no such" in msg:
            return True
        # Explicit error wrapper from call_mcp_tool exception handler
        if list(val.keys()) == ["error"]:   # {"error": "MCP call failed..."}
            return True
        return False   # valid entity dict — NOT an error

    # ── String: MCP server returns "ERROR <code>: ..." on failure ─────────────
    if isinstance(val, str):
        s = val.strip().lower()
        return (
            s.startswith("error")          # "ERROR 500: ..."
            or "error 404" in s
            or "error 500" in s
            or "not found" in s
        )

    return False

def _has_valid_data(results: dict) -> bool:
    """True when at least one tool returned meaningful (non-error) data."""
    skip = {"hitl_required", "hitl_step"}
    return any(
        not _is_error(v) and v is not None
        for k, v in results.items()
        if k not in skip
    )

# ── Ollama helpers ─────────────────────────────────────────────────────────────
async def ollama(http: httpx.AsyncClient, messages: list,
                 json_mode: bool = False) -> str:
    payload: dict[str, Any] = {
        "model": OLLAMA_MODEL, "messages": messages,
        "stream": False, "options": {"temperature": 0.0},
    }
    if json_mode:
        payload["format"] = "json"
    # fast connect timeout so a missing Ollama fails in 5 s, not 60 s
    r = await http.post(
        f"{OLLAMA_URL}/api/chat", json=payload,
        timeout=httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=5.0),
    )
    return r.json()["message"]["content"]

async def ollama_stream(http: httpx.AsyncClient, messages: list) -> str:
    payload = {"model": OLLAMA_MODEL, "messages": messages, "stream": True,
               "options": {"temperature": 0.1, "num_predict": 800}}
    chunks: list[str] = []
    try:
        async with http.stream(
            "POST", f"{OLLAMA_URL}/api/chat", json=payload,
            timeout=httpx.Timeout(connect=10.0, read=90.0, write=10.0, pool=10.0)
        ) as r:
            async for line in r.aiter_lines():
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    chunks.append(data.get("message", {}).get("content", ""))
                    if data.get("done"):
                        break
                except Exception:
                    pass
    except Exception:
        pass
    return "".join(chunks)


# ── Keyword-based fallback classifier (used when Ollama is unreachable) ──────
def _keyword_classify(msg: str) -> dict:
    m = msg.lower()
    entities: dict = {}
    cid = re.search(r'customer\s*(?:id)?\s*[:#]?\s*(\d+)', m)
    lid = re.search(r'loan\s*(?:id)?\s*[:#]?\s*(\d+)', m)
    if cid: entities["customer_id"] = int(cid.group(1))
    if lid: entities["loan_id"]     = int(lid.group(1))
    name = re.search(r'(?:for|of|customer)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', msg)
    if name and not cid: entities["customer_name"] = name.group(1)
    if any(w in m for w in ("health","services up","ping")):
        return {"intent": "system_health",    "entities": entities}
    if any(w in m for w in ("policy","regulation","rule","guideline","compliance")):
        return {"intent": "policy_question",  "entities": entities}
    if any(w in m for w in ("approve","approval","reject","decision")):
        return {"intent": "approval_request", "entities": entities}
    if any(w in m for w in ("onboard","new loan","apply")):
        return {"intent": "full_onboarding",  "entities": entities}
    if any(w in m for w in ("risk","credit risk")):
        return {"intent": "risk_assessment",  "entities": entities}
    if any(w in m for w in ("document","doc","upload","checklist")):
        return {"intent": "document_check",   "entities": entities}
    if any(w in m for w in ("kyc","know your customer","verify")):
        return {"intent": "kyc_status",       "entities": entities}
    if any(w in m for w in ("loan","loans","borrow","emi","disburse")):
        return {"intent": "loan_status",      "entities": entities}
    if any(w in m for w in ("customer","client","customers")):
        return {"intent": "customer_inquiry", "entities": entities}
    return {"intent": "general", "entities": entities}

# ── Node 1 — classify intent ───────────────────────────────────────────────────
async def classify_intent(state: LoanState) -> dict:
    user_msg = next(
        (m["content"] for m in reversed(state["messages"]) if m["role"] == "user"), ""
    )
    # ── Try Ollama; fall back to keyword classifier if unreachable ───────
    try:
        async with httpx.AsyncClient() as http:
            resp = await ollama(http, [
                {"role": "system", "content": (
                    "You are a BFSI loan onboarding intent classifier. "
                    "Return JSON: {intent, entities}. "
                    "intent must be one of: customer_inquiry, loan_status, kyc_status, "
                    "document_check, risk_assessment, policy_question, approval_request, "
                    "full_onboarding, system_health, general. "
                    "entities keys: customer_id(int), loan_id(int), "
                    "customer_name(str), loan_type(str). "
                    "If user asks for ALL records → entities={}. "
                    "NEVER use wildcards. Return valid JSON only."
                )},
                {"role": "user", "content": user_msg},
            ], json_mode=True)
        parsed   = json.loads(resp)
        entities = dict(parsed.get("entities") or {})
        for fld in ("customer_id", "loan_id"):
            val = entities.get(fld)
            if val is not None:
                try:    entities[fld] = int(val)
                except (ValueError, TypeError): entities.pop(fld, None)
        return {"intent": parsed.get("intent", "general"), "entities": entities}
    except Exception:
        # Ollama unreachable or bad JSON — use keyword fallback
        return _keyword_classify(user_msg)

# ── Node 2 — select agents ─────────────────────────────────────────────────────
def select_agents(state: LoanState) -> dict:
    intent   = state["intent"]
    user_msg = next(
        (m["content"].lower() for m in reversed(state["messages"]) if m["role"] == "user"), ""
    )
    agents = list(INTENT_AGENT_MAP.get(intent, ["loan"]))

    kw_map = {
        "loan":      ["loan", "application", "borrow", "finance", "amount", "lending"],
        "customer":  ["customer", "client", "borrower", "company", "business"],
        "kyc":       ["kyc", "identity", "verification", "aml", "compliance"],
        "document":  ["document", "doc", "file", "checklist", "upload"],
        "risk":      ["risk", "credit score", "assessment", "dti", "ltv", "rating"],
        "workflow":  ["workflow", "step", "approval", "process", "onboard", "pipeline"],
        "knowledge": ["policy", "rule", "eligib", "criteria", "guideline", "sop"],
    }
    for agent, keywords in kw_map.items():
        if agent not in agents and any(k in user_msg for k in keywords):
            agents.append(agent)

    return {"selected_agents": agents, "tool_calls": [], "tool_results": {}}

# ── Node 3 — execute via MCP servers ──────────────────────────────────────────
async def execute_agents(state: LoanState) -> dict:
    agents   = state["selected_agents"]
    entities = state["entities"]
    cid      = entities.get("customer_id")
    lid      = entities.get("loan_id")
    cname    = entities.get("customer_name", "")

    calls:   list = []
    results: dict = {}

    async def mcp(agent: str, tool: str, args: dict, key: str):
        url = MCP_URL_MAP.get(agent)
        if not url:
            return
        calls.append({"agent": agent, "tool": tool, "args": args})
        results[key] = await call_mcp_tool(url, tool, args)

    # ── Customer agent via Customer MCP (:9001) ────────────────────────────
    if "customer" in agents:
        if cid:
            await mcp("customer", "get_customer_by_id",
                      {"customer_id": cid}, "customer_profile")
            await mcp("customer", "get_customer_credit_profile",
                      {"customer_id": cid}, "credit_profile")
        elif cname:
            await mcp("customer", "search_customers",
                      {"name": cname}, "customer_search")
            sr = results.get("customer_search")
            if isinstance(sr, list) and sr:
                cid = sr[0].get("id")
                results["customer_profile"] = sr[0]
        else:
            await mcp("customer", "get_all_customers", {}, "all_customers")

    # ── KYC agent via KYC MCP (:9002) ─────────────────────────────────────
    if "kyc" in agents and cid:
        await mcp("kyc", "get_kyc_status", {"customer_id": cid}, "kyc_records")

    # ── Document agent via Document MCP (:9003) ────────────────────────────
    if "document" in agents:
        if lid:
            await mcp("document", "get_document_checklist",
                      {"loan_id": lid}, "document_checklist")
            await mcp("document", "get_documents_by_loan",
                      {"loan_id": lid}, "documents")
        elif cid:
            await mcp("document", "get_documents_by_customer",
                      {"customer_id": cid}, "documents")

    # ── Risk agent via Risk MCP (:9004) ────────────────────────────────────
    if "risk" in agents:
        if lid:
            await mcp("risk", "get_risk_assessment_by_loan",
                      {"loan_id": lid}, "risk_assessments")
        elif cid:
            await mcp("risk", "get_risk_assessments_by_customer",
                      {"customer_id": cid}, "risk_assessments")

    # ── Workflow agent via Workflow MCP (:9005) ────────────────────────────
    if "workflow" in agents:
        if lid:
            await mcp("workflow", "get_workflow_summary",
                      {"loan_id": lid}, "workflow_summary")
            ws = results.get("workflow_summary", {})
            if isinstance(ws, dict) and ws.get("status") == "AWAITING_APPROVAL":
                steps   = ws.get("steps", [])
                pending = next(
                    (s for s in steps if s.get("status") == "AWAITING_APPROVAL"), None
                )
                if pending:
                    results["hitl_required"] = True
                    results["hitl_step"]     = pending
        else:
            await mcp("workflow", "get_all_workflows", {}, "workflows")

    # ── Loan agent via Loan MCP (:9007) ───────────────────────────────────
    if "loan" in agents:
        from agents.config import MCP_LOAN
        if lid:
            calls.append({"agent": "loan", "tool": "get_loan_by_id",
                          "args": {"loan_id": lid}})
            results["loan_application"] = await call_mcp_tool(
                MCP_LOAN, "get_loan_by_id", {"loan_id": lid})
        else:
            calls.append({"agent": "loan", "tool": "get_all_loans", "args": {}})
            results["loan_applications"] = await call_mcp_tool(
                MCP_LOAN, "get_all_loans", {})

    # ── Knowledge agent via Knowledge MCP (:9006) ─────────────────────────
    if "knowledge" in agents:
        user_q = next(
            (m["content"] for m in reversed(state["messages"]) if m["role"] == "user"), ""
        )
        await mcp("knowledge", "search_loan_policies",
                  {"query": user_q}, "policy_context")

    # ── Platform health (direct) ───────────────────────────────────────────
    if "platform" in agents:
        from agents.config import (CUSTOMER_SERVICE, KYC_SERVICE,
                                    DOCUMENT_SERVICE, RISK_SERVICE,
                                    WORKFLOW_SERVICE, LOAN_SERVICE)
        health = {}
        async with httpx.AsyncClient() as http:
            for name, url in [
                ("customer", CUSTOMER_SERVICE), ("kyc", KYC_SERVICE),
                ("document", DOCUMENT_SERVICE), ("risk", RISK_SERVICE),
                ("workflow", WORKFLOW_SERVICE), ("loan", LOAN_SERVICE),
            ]:
                try:
                    r = await http.get(f"{url}/actuator/health", timeout=5)
                    health[name] = "UP" if r.is_success else "DOWN"
                except Exception:
                    health[name] = "DOWN"
        calls.append({"agent": "platform", "tool": "check_service_health", "args": {}})
        results["service_health"] = health

    requires_hitl = bool(results.get("hitl_required"))
    hitl_step     = results.get("hitl_step") if requires_hitl else None
    return {
        "tool_calls":    calls,
        "tool_results":  results,
        "requires_hitl": requires_hitl,
        "hitl_step_id":  hitl_step.get("id") if hitl_step else None,
        "hitl_context":  {"step": hitl_step, "loan_id": lid, "customer_id": cid}
                         if requires_hitl else None,
    }

# ── HITL routing ───────────────────────────────────────────────────────────────
def check_hitl_needed(state: LoanState) -> str:
    if state.get("requires_hitl") and not state.get("hitl_decision"):
        return "needs_approval"
    return "synthesize"

def hitl_node(state: LoanState) -> dict:
    decision = interrupt({
        "type": "loan_approval_required",
        "step_id": state.get("hitl_step_id"),
        "context": state.get("hitl_context"),
    })
    return {"hitl_decision": decision}

# ── Query filter parser ───────────────────────────────────────────────────────
def _parse_filters(user_msg: str) -> dict:
    """Extract numeric filter conditions from user message.

    Returns a dict with optional keys:
      credit_score_op  : 'gt' | 'gte' | 'lt' | 'lte' | 'eq'
      credit_score_val : int
      amount_op        : 'gt' | 'gte' | 'lt' | 'lte' | 'eq'
      amount_val       : float
    """
    filters: dict = {}
    um = user_msg.lower()

    # ── Credit score filter ────────────────────────────────────────────────────
    # Patterns: "above 700", "credit score > 700", "greater than 750", etc.
    cs_patterns = [
        (r"credit\s*score\s*(?:of\s*)?(?:above|over|>|greater\s*than)\s*(\d+)",  "gt"),
        (r"credit\s*score\s*(?:of\s*)?(?:below|under|<|less\s*than)\s*(\d+)",    "lt"),
        (r"credit\s*score\s*(?:of\s*)?(?:at\s*least|>=)\s*(\d+)",                "gte"),
        (r"credit\s*score\s*(?:of\s*)?(?:at\s*most|<=)\s*(\d+)",                 "lte"),
        (r"credit\s*score\s*(?:of\s*)?(\d+)\s*(?:and\s*above|\+|or\s*more)",   "gte"),
        (r"credit\s*score\s*(?:of\s*)?(\d+)\s*(?:and\s*below|or\s*less)",       "lte"),
        (r"(?:above|over|>|greater\s*than)\s*(\d+)\s*credit\s*score",             "gt"),
        (r"(?:below|under|<|less\s*than)\s*(\d+)\s*credit\s*score",               "lt"),
        (r"(?:above|over|>|greater\s*than)\s*(?:a\s*)?credit\s*score\s*(?:of\s*)?(\d+)", "gt"),
        (r"(?:below|under|<|less\s*than)\s*(?:a\s*)?credit\s*score\s*(?:of\s*)?(\d+)",   "lt"),
    ]
    for pattern, op in cs_patterns:
        m = re.search(pattern, um)
        if m:
            filters["credit_score_op"]  = op
            filters["credit_score_val"] = int(m.group(1))
            break

    return filters


def _apply_credit_filter(customers: list, filters: dict) -> list:
    """Filter customer list by credit score condition."""
    op  = filters.get("credit_score_op")
    val = filters.get("credit_score_val")
    if not op or val is None:
        return customers
    ops = {
        "gt":  lambda s: s >  val,
        "gte": lambda s: s >= val,
        "lt":  lambda s: s <  val,
        "lte": lambda s: s <= val,
        "eq":  lambda s: s == val,
    }
    fn = ops.get(op, lambda s: True)
    return [c for c in customers if fn(c.get("creditScore") or 0)]


# ── Direct Markdown formatter (instant fallback) ───────────────────────────────
def _fmt(results: dict, user_msg: str) -> str:
    parts = [f"**Query:** {user_msg}\n"]

    if loans := (results.get("loan_applications") or results.get("all_loans")):
        if isinstance(loans, list) and loans:
            # Apply status filter if user said "active", "pending", "approved" etc.
            um = user_msg.lower()
            TERMINAL = {"rejected", "disbursed", "closed"}
            if "active" in um or "pending" in um or "open" in um:
                loans = [l for l in loans if l.get("status","").upper()
                         not in ("REJECTED","DISBURSED","CLOSED","DRAFT")]
            elif "approved" in um:
                loans = [l for l in loans if l.get("status","").upper() == "APPROVED"]
            elif "rejected" in um:
                loans = [l for l in loans if l.get("status","").upper() == "REJECTED"]
            elif "draft" in um:
                loans = [l for l in loans if l.get("status","").upper() == "DRAFT"]
            elif "review" in um or "under review" in um:
                loans = [l for l in loans if l.get("status","").upper() == "UNDER_REVIEW"]

            count = len(loans)
            parts += [f"\n### 💰 Loan Applications ({count} found)\n",
                      "| Loan ID | Customer ID | Type | Amount | Status | Priority | Officer |",
                      "|---|---|---|---|---|---|---|"]
            for l in loans:
                amt = f"${l.get('amount', 0):,.0f}" if l.get("amount") else "—"
                parts.append(
                    f"| #{l.get('id','?')} | #{l.get('customerId','?')} "
                    f"| {l.get('loanType','—')} | {amt} "
                    f"| **{l.get('status','—')}** | {l.get('priority','—')} "
                    f"| {l.get('assignedOfficer') or 'Unassigned'} |")
            if not loans:
                parts.append("_No loans match the filter criteria._")

    if loan := results.get("loan_application"):
        if _is_error(loan):
            err_txt = (loan.get("message") or loan.get("error") or str(loan)
                       if isinstance(loan, dict) else str(loan))
            parts.append(f"\n⚠️ **Loan application not found**\n> {err_txt[:200]}")
        elif isinstance(loan, dict):
            amt = f"${loan.get('amount', 0):,.0f}" if loan.get("amount") else "—"
            parts += [f"\n### 💰 Loan #{loan.get('id')} — {loan.get('loanType','—')}",
                      f"- **Amount:** {amt}  · **Status:** **{loan.get('status','—')}**",
                      f"- **Purpose:** {loan.get('purpose','—')}",
                      f"- **Tenure:** {loan.get('tenureMonths','—')} months"
                      f"  · **Rate:** {loan.get('interestRate','—')}%",
                      f"- **Officer:** {loan.get('assignedOfficer') or 'Unassigned'}"]

    if custs := results.get("all_customers"):
        if isinstance(custs, list) and custs:
            # Apply credit score filter if user specified one
            filters      = _parse_filters(user_msg)
            custs_filtered = _apply_credit_filter(custs, filters)
            op  = filters.get("credit_score_op")
            val = filters.get("credit_score_val")

            op_label = {"gt":"above","gte":"at least","lt":"below","lte":"at most","eq":"equal to"}.get(op,"")
            filter_note = f" (credit score {op_label} {val})" if op and val else ""
            count = len(custs_filtered)

            parts += [f"\n### 👥 Customers ({count} found{filter_note})\n",
                      "| Customer ID | First Name | Last Name | Company | Address | Credit Score | Rating | Revenue | Status |",
                      "|---|---|---|---|---|---|---|---|---|"]
            for c in custs_filtered:
                rev  = f"${c.get('annualRevenue', 0):,.0f}" if c.get("annualRevenue") else "—"
                cs   = c.get("creditScore") or 0
                rating = ("EXCELLENT" if cs >= 780 else "GOOD" if cs >= 720
                          else "FAIR" if cs >= 650 else "POOR")
                parts.append(
                    f"| #{c.get('id','?')} "
                    f"| {c.get('firstName') or '—'} "
                    f"| {c.get('lastName') or '—'} "
                    f"| {c.get('companyName') or '—'} "
                    f"| {c.get('address') or '—'} "
                    f"| {cs} | {rating} | {rev} | {c.get('status') or '—'} |")
            if not custs_filtered:
                parts.append(f"_No customers match: credit score {op_label} {val}._")

    if cust := results.get("customer_profile"):
        if isinstance(cust, dict) and "companyName" in cust:
            first  = cust.get('firstName') or ''
            last   = cust.get('lastName')  or ''
            parts += [f"\n### 👤 {first} {last} — {cust.get('companyName') or '—'}",
                      f"- **Address:** {cust.get('address') or '—'}",
                      f"- **Email:** {cust.get('email') or '—'}",
                      f"- **Credit Score:** **{cust.get('creditScore') or '—'}**"
                      f"  · Revenue: ${cust.get('annualRevenue') or 0:,.0f}",
                      f"- **Status:** {cust.get('status') or '—'}"]

    if kyc_list := results.get("kyc_records"):
        if isinstance(kyc_list, list) and kyc_list:
            k = kyc_list[-1]
            parts += [f"\n### 🔐 KYC: **{k.get('status','—')}**",
                      f"- PAN ✓:{k.get('panVerified')}  Address ✓:{k.get('addressVerified')}"
                      f"  AML:{k.get('amlCleared')}"]

    if risks := results.get("risk_assessments"):
        if isinstance(risks, list) and risks:
            r = risks[-1]
            parts += [f"\n### ⚠️ Risk: **{r.get('riskCategory','—')}**",
                      f"- Score:{r.get('riskScore','—')}/100"
                      f"  Recommendation:**{r.get('recommendation','—')}**"]

    if wf := results.get("workflow_summary"):
        if isinstance(wf, dict):
            parts += [f"\n### 🔄 Workflow: **{wf.get('status','—')}**",
                      f"- Step: {wf.get('currentStep','—')}",
                      f"- Progress: {wf.get('completedSteps',0)}/{wf.get('totalSteps',0)}"]

    if chk := results.get("document_checklist"):
        if isinstance(chk, dict):
            ok = "✅ Complete" if chk.get("complete") else "⏳ Incomplete"
            parts.append(f"\n### 📄 Documents: {ok} — "
                         f"Verified:{chk.get('verified',0)} "
                         f"Pending:{chk.get('pending',0)}")

    if health := results.get("service_health"):
        if isinstance(health, dict):
            parts.append("\n### 🔧 Service Health")
            for svc, st in health.items():
                parts.append(f"- {'🟢' if st=='UP' else '🔴'} **{svc}**: {st}")

    if policy := results.get("policy_context"):
        if isinstance(policy, list) and policy:
            parts.append("\n### 📖 Policy Matches")
            for p in policy[:3]:
                parts.append(f"- **{p.get('document','—')}**: {p.get('excerpt','')[:200]}")

    if len(parts) <= 1:
        for key, val in results.items():
            if isinstance(val, (dict, list)):
                parts.append(f"\n**{key}:**\n```json\n"
                              + json.dumps(val, indent=2)[:1500] + "\n```")
    return "\n".join(parts)

# ── Node 5 — synthesize response ───────────────────────────────────────────────
async def synthesize_response(state: LoanState) -> dict:
    user_msg  = next(
        (m["content"] for m in reversed(state["messages"]) if m["role"] == "user"), ""
    )
    results   = state.get("tool_results", {})
    entities  = state.get("entities", {})
    hitl_note = (f"\n\nHuman decision: {state['hitl_decision']}"
                 if state.get("hitl_decision") else "")

    # ── Guard: primary requested entity not found → never call Ollama ───────────
    lid = entities.get("loan_id")
    cid = entities.get("customer_id")

    # When a specific ID was requested, check that primary result is valid
    primary_error = False
    if lid and _is_error(results.get("loan_application")):
        primary_error = True
    if cid and not lid and _is_error(results.get("customer_profile")):
        primary_error = True

    # When ALL tool results are errors, also trigger not-found
    if not _has_valid_data(results) or primary_error:
        subject = (f"Loan Application ID **{lid}**" if lid
                   else f"Customer ID **{cid}**" if cid
                   else "the requested record")
        err_details = "; ".join(
            str(v.get("error", v) if isinstance(v, dict) else v)[:120]
            for k, v in results.items()
            if _is_error(v) and k not in ("hitl_required", "hitl_step")
        )
        not_found = (
            f"⚠️ **Record Not Found**\n\n"
            f"{subject} does not exist in the system.\n\n"
            f"**System response:** {err_details or 'No matching record returned by the API.'}\n\n"
            f"Please verify the ID is correct. "
            f"The demo system contains loan IDs **1–5** and customer IDs **1–5**."
        )
        return {"final_response": not_found,
                "messages": [{"role": "assistant", "content": not_found}]}

    # ── Direct Markdown formatter (instant, always correct) ───────────────────
    direct = _fmt(results, user_msg)

    # ── Decide whether Ollama is needed ──────────────────────────────────────
    # Structured data (loans, customers, KYC, risk, workflow): use _fmt() ONLY.
    # Policy / knowledge queries: use Ollama to interpret search results.
    selected_agents = state.get("selected_agents", [])
    is_knowledge_query = "knowledge" in selected_agents and "policy_context" in results

    if not is_knowledge_query:
        # Always use the direct formatter for structured data — zero hallucination risk
        return {"final_response": direct,
                "messages": [{"role": "assistant", "content": direct}]}

    # ── Knowledge/policy query: use Ollama to explain the policy excerpt ──────
    results_str = json.dumps(results.get("policy_context", []), indent=2)[:3000]
    system = (
        "You are SASVA, a BFSI Loan Onboarding Copilot. "
        "The user asked a question about banking policy. "
        "Answer using ONLY the policy excerpts provided below. "
        "Quote the relevant policy text directly. Be concise and clear."
    )
    prompt = (
        f"User question: {user_msg}\n\n"
        f"Policy excerpts from knowledge base:\n{results_str}\n\n"
        "Answer based solely on the policy excerpts above."
    )
    response = ""
    try:
        async with httpx.AsyncClient() as http:
            response = await ollama_stream(http, [
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ])
    except Exception:
        pass

    final = response.strip() if len(response.strip()) > 80 else direct
    return {"final_response": final,
            "messages": [{"role": "assistant", "content": final}]}

# ── Build LangGraph ────────────────────────────────────────────────────────────
memory = MemorySaver()

def build_graph():
    g = StateGraph(LoanState)
    g.add_node("classify",   classify_intent)
    g.add_node("select",     select_agents)
    g.add_node("execute",    execute_agents)
    g.add_node("hitl",       hitl_node)
    g.add_node("synthesize", synthesize_response)
    g.add_edge(START,       "classify")
    g.add_edge("classify",  "select")
    g.add_edge("select",    "execute")
    g.add_conditional_edges(
        "execute", check_hitl_needed,
        {"needs_approval": "hitl", "synthesize": "synthesize"},
    )
    g.add_edge("hitl",      "synthesize")
    g.add_edge("synthesize", END)
    return g.compile(checkpointer=memory, interrupt_before=["hitl"])

coordinator = build_graph()
