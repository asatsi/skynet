import os, json, uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Mount

app = Server("knowledge-mcp-server")
sse = SseServerTransport("/messages/")

# ── In-memory policy store (ChromaDB optional) ────────────────────────────────
POLICIES: dict[str, str] = {}

def load_policies():
    policy_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge", "policies")
    if not os.path.exists(policy_dir):
        return
    for fname in os.listdir(policy_dir):
        if fname.endswith((".md", ".txt")):
            with open(os.path.join(policy_dir, fname)) as f:
                POLICIES[fname.replace(".md","").replace(".txt","")] = f.read()
    print(f"[KnowledgeMCP] Loaded {len(POLICIES)} policy documents")

load_policies()

def search_policies(query: str, top_k: int = 3) -> list[dict]:
    q = query.lower()
    results = []
    for name, content in POLICIES.items():
        score = sum(1 for word in q.split() if word in content.lower())
        if score > 0:
            excerpt = ""
            for line in content.split("\n"):
                if any(w in line.lower() for w in q.split()):
                    excerpt += line.strip() + "\n"
            results.append({"document": name, "score": score, "excerpt": excerpt[:800]})
    return sorted(results, key=lambda x: -x["score"])[:top_k]

@app.list_tools()
async def list_tools():
    return [
        Tool(name="search_loan_policies",     description="Search banking loan policies and SOPs by keyword or question.",
             inputSchema={"type":"object","properties":{"query":{"type":"string","description":"Policy question or keyword"}},"required":["query"]}),
        Tool(name="get_policy_document",      description="Retrieve the full content of a specific policy document.",
             inputSchema={"type":"object","properties":{"document_name":{"type":"string","description":"Policy document name e.g. loan_policy, kyc_policy, risk_policy"}},"required":["document_name"]}),
        Tool(name="list_policy_documents",    description="List all available policy documents.",
             inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="get_eligibility_criteria", description="Get loan eligibility criteria and thresholds.",
             inputSchema={"type":"object","properties":{"loan_type":{"type":"string","description":"Loan type e.g. WORKING_CAPITAL, TERM_LOAN"}},"required":[]}),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        if name == "search_loan_policies":
            results = search_policies(arguments["query"])
            if not results:
                return [TextContent(type="text", text="No matching policy documents found.")]
            return [TextContent(type="text", text=json.dumps(results, indent=2))]
        elif name == "get_policy_document":
            doc = arguments["document_name"].replace(".md","")
            content = POLICIES.get(doc)
            if not content:
                return [TextContent(type="text", text=f"Document '{doc}' not found. Available: {list(POLICIES.keys())}")]
            return [TextContent(type="text", text=content)]
        elif name == "list_policy_documents":
            docs = [{"name": k, "size_chars": len(v)} for k, v in POLICIES.items()]
            return [TextContent(type="text", text=json.dumps(docs, indent=2))]
        elif name == "get_eligibility_criteria":
            criteria = {
                "min_credit_score": 650,
                "min_years_in_operation": 3,
                "max_debt_to_income_ratio": 55.0,
                "max_loan_to_value_ratio": 85.0,
                "min_annual_revenue_for_working_capital": 1000000,
                "required_documents": ["FINANCIAL_STATEMENT","BANK_STATEMENT","TAX_RETURN","BUSINESS_LICENSE"],
                "kyc_required": True,
                "loan_types": ["WORKING_CAPITAL","TERM_LOAN","EQUIPMENT_FINANCE","TRADE_FINANCE"]
            }
            return [TextContent(type="text", text=json.dumps(criteria, indent=2))]
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"ERROR: {e}")]

async def handle_sse(scope, receive, send):
    async with sse.connect_sse(scope, receive, send) as streams:
        await app.run(streams[0], streams[1], app.create_initialization_options())

_msg_app = Starlette(debug=False, routes=[Mount("/messages/", app=sse.handle_post_message)])

async def starlette_app(scope, receive, send):
    if scope["type"] == "http" and scope.get("path", "").rstrip("/") == "/sse":
        await handle_sse(scope, receive, send)
    else:
        await _msg_app(scope, receive, send)

if __name__ == "__main__":
    uvicorn.run(starlette_app, host="0.0.0.0", port=9006, log_level="info")
