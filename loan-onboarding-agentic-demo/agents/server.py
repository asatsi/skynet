import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json, asyncio, uuid, httpx, traceback
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
try:
    from agents.coordinator import coordinator, build_graph
except Exception as _coord_err:
    import traceback as _tb
    print("\n[FATAL] Could not import coordinator:")
    print(_tb.format_exc())
    raise
from agents.config import (CUSTOMER_SERVICE, KYC_SERVICE, DOCUMENT_SERVICE,
                             RISK_SERVICE, WORKFLOW_SERVICE, LOAN_SERVICE,
                             OLLAMA_URL, OLLAMA_MODEL, AGENT_SERVER_PORT,
                             MCP_GATEWAY)
import uvicorn

api = FastAPI(title="BFSI Loan Onboarding Copilot", version="1.0.0")

UI_DIR = Path(__file__).parent.parent / "ui"

@api.get("/", response_class=HTMLResponse)
async def serve_ui():
    html_file = UI_DIR / "index.html"
    return HTMLResponse(content=html_file.read_text())

# ── Health check ───────────────────────────────────────────────────────────────
@api.get("/api/health")
async def health():
    # Explicit paths — avoids wrong pluralisation (e.g. /api/v1/kycs, /api/v1/risks)
    services = {
        "customer": (CUSTOMER_SERVICE, "/api/v1/customers"),
        "kyc":      (KYC_SERVICE,       "/api/v1/kyc"),
        "document": (DOCUMENT_SERVICE,  "/api/v1/documents"),
        "risk":     (RISK_SERVICE,      "/api/v1/risk"),
        "workflow": (WORKFLOW_SERVICE,  "/api/v1/workflows"),
        "loan":     (LOAN_SERVICE,      "/api/v1/loans"),
    }
    results = {}
    async with httpx.AsyncClient() as http:
        for name, (url, path) in services.items():
            try:
                r = await http.get(f"{url}{path}", timeout=5)
                results[name] = {"status": "UP" if r.is_success else "DEGRADED",
                                 "code": r.status_code}
            except Exception as e:
                results[name] = {"status": "DOWN", "error": str(e)[:80]}
        # MCP Gateway
        try:
            r = await http.get(f"{MCP_GATEWAY}/tools", timeout=5)
            tools = r.json().get("tools", []) if r.is_success else []
            results["mcp_gateway"] = {"status": "UP", "tools_registered": len(tools)}
        except Exception as e:
            results["mcp_gateway"] = {"status": "DOWN", "error": str(e)[:80]}
        # Ollama
        try:
            r = await http.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            models = [m["name"] for m in r.json().get("models", [])]
            results["ollama"] = {"status": "UP", "models": models}
        except Exception as e:
            results["ollama"] = {"status": "DOWN", "error": str(e)[:80]}
    return results

# ── Loan dashboard data ────────────────────────────────────────────────────────
@api.get("/api/loans")
async def get_loans():
    async with httpx.AsyncClient() as http:
        r = await http.get(f"{LOAN_SERVICE}/api/v1/loans", timeout=10)
        return r.json() if r.is_success else []

@api.get("/api/customers")
async def get_customers():
    async with httpx.AsyncClient() as http:
        r = await http.get(f"{CUSTOMER_SERVICE}/api/v1/customers", timeout=10)
        return r.json() if r.is_success else []

@api.get("/api/workflows")
async def get_workflows():
    async with httpx.AsyncClient() as http:
        r = await http.get(f"{WORKFLOW_SERVICE}/api/v1/workflows", timeout=10)
        return r.json() if r.is_success else []

@api.get("/api/approvals")
async def get_pending_approvals():
    async with httpx.AsyncClient() as http:
        r = await http.get(f"{WORKFLOW_SERVICE}/api/v1/workflows", timeout=10)
        if not r.is_success:
            return []
        return [w for w in r.json() if w.get("status") == "AWAITING_APPROVAL"]

# ── HITL approve / reject ──────────────────────────────────────────────────────
@api.post("/api/approve/{step_id}")
async def approve_step(step_id: int, request: Request):
    body = await request.json()
    approver = body.get("approver", "LOAN_OFFICER")
    notes    = body.get("notes", "Approved via AI Copilot")
    async with httpx.AsyncClient() as http:
        r = await http.put(f"{WORKFLOW_SERVICE}/api/v1/workflows/steps/{step_id}/approve",
                           json={"approver": approver, "notes": notes}, timeout=15)
        # Also update loan status
        loan_id = body.get("loan_id")
        if loan_id:
            await http.put(f"{LOAN_SERVICE}/api/v1/loans/{loan_id}/approve",
                           json={"approver": approver, "notes": notes}, timeout=15)
    return {"status": "approved", "step_id": step_id}

@api.post("/api/reject/{step_id}")
async def reject_step(step_id: int, request: Request):
    body   = await request.json()
    reason = body.get("reason", "Rejected via AI Copilot")
    async with httpx.AsyncClient() as http:
        r = await http.put(f"{WORKFLOW_SERVICE}/api/v1/workflows/steps/{step_id}/reject",
                           json={"rejector": body.get("rejector","LOAN_OFFICER"), "reason": reason}, timeout=15)
        loan_id = body.get("loan_id")
        if loan_id:
            await http.put(f"{LOAN_SERVICE}/api/v1/loans/{loan_id}/reject",
                           json={"reason": reason}, timeout=15)
    return {"status": "rejected", "step_id": step_id}

# ── Chat SSE endpoint ──────────────────────────────────────────────────────────
@api.post("/api/chat")
async def chat(request: Request):
    body     = await request.json()
    messages = body.get("messages", [])
    thread   = body.get("thread_id", str(uuid.uuid4()))
    config   = {"configurable": {"thread_id": thread}}

    async def stream_events():
        # Initial state
        init_state = {
            "messages":        messages,
            "intent":          "",
            "entities":        {},
            "selected_agents": [],
            "tool_calls":      [],
            "tool_results":    {},
            "requires_hitl":   False,
            "hitl_step_id":    None,
            "hitl_context":    None,
            "hitl_decision":   None,
            "final_response":  "",
        }
        try:
            async for event in coordinator.astream(init_state, config, stream_mode="updates"):
                for node_name, node_output in event.items():
                    # Status updates
                    yield {"data": json.dumps({"type":"status","node":node_name,"text":f"Agent: {node_name}…"})}

                    # Intent classified
                    if node_name == "classify" and "intent" in node_output:
                        yield {"data": json.dumps({"type":"intent","intent":node_output["intent"],
                                                   "entities":node_output.get("entities",{})})}

                    # Agents selected
                    if node_name == "select" and "selected_agents" in node_output:
                        yield {"data": json.dumps({"type":"agents_selected",
                                                   "agents":node_output["selected_agents"]})}

                    # Tool calls
                    if node_name == "execute":
                        # ── Gateway connection info ──────────────────────────
                        yield {"data": json.dumps({
                            "type":        "gateway_connected",
                            "url":         MCP_GATEWAY,
                            "tools_count": node_output.get("gateway_tools_count", 0),
                        })}
                        # ── Tools selected by Ollama / fallback ──────────────
                        sel = node_output.get("selected_tool_names", [])
                        if sel:
                            yield {"data": json.dumps({
                                "type":  "tools_available",
                                "tools": sel,
                            })}
                        # ── Per-tool call events ─────────────────────────────
                        for tc in node_output.get("tool_calls", []):
                            yield {"data": json.dumps({
                                "type":    "tool_call",
                                "agent":   tc.get("agent", ""),
                                "tool":    tc.get("tool", ""),
                                "args":    tc.get("args", {}),
                                "server":  tc.get("server", tc.get("agent", "")),
                                "gateway": MCP_GATEWAY,
                            })}
                        # ── Per-tool result events ───────────────────────────
                        for tool_name, result in node_output.get("tool_results", {}).items():
                            if tool_name in {"all_customers","loan_applications","kyc_records",
                                             "risk_assessments","workflows","workflow_summary",
                                             "loan_application","customer_profile",
                                             "document_checklist","error"}:
                                continue   # skip aliased keys — emit only raw tool outputs
                            yield {"data": json.dumps({
                                "type":   "tool_result",
                                "tool":   tool_name,
                                "output": result[:600] if isinstance(result,str) else str(result)[:600],
                            })}
                        # ── HITL ─────────────────────────────────────────────
                        if node_output.get("requires_hitl"):
                            yield {"data": json.dumps({"type":"hitl_required",
                                                       "step_id":node_output.get("hitl_step_id"),
                                                       "context":node_output.get("hitl_context"),
                                                       "thread_id":thread})}

                    # Final response
                    if node_name == "synthesize" and "final_response" in node_output:
                        yield {"data": json.dumps({"type":"final",
                                                   "text":node_output["final_response"],
                                                   "thread_id":thread})}

        except Exception as e:
            tb = traceback.format_exc()
            yield {"data": json.dumps({"type":"error","text": f"{type(e).__name__}: {e} | {tb[-300:]}"})}

    return EventSourceResponse(stream_events())

# ── Resume after HITL ──────────────────────────────────────────────────────────
@api.post("/api/resume/{thread_id}")
async def resume(thread_id: str, request: Request):
    body     = await request.json()
    decision = body.get("decision", "APPROVE")
    config   = {"configurable": {"thread_id": thread_id}}

    async def stream_resume():
        async for event in coordinator.astream(
            {"hitl_decision": decision}, config, stream_mode="updates"
        ):
            for node_name, node_output in event.items():
                yield {"data": json.dumps({"type":"status","node":node_name,"text":f"Resuming: {node_name}…"})}
                if node_name == "synthesize" and "final_response" in node_output:
                    yield {"data": json.dumps({"type":"final","text":node_output["final_response"]})}

    return EventSourceResponse(stream_resume())

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=AGENT_SERVER_PORT, log_level="info")
