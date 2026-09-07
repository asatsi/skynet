import os, httpx, json, uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Mount

BASE_URL = os.environ.get("RISK_SERVICE_URL", "http://localhost:8084")
app = Server("risk-mcp-server")
sse = SseServerTransport("/messages/")

@app.list_tools()
async def list_tools():
    return [
        Tool(name="get_risk_assessment_by_loan",     description="Get latest risk assessment for a loan.",
             inputSchema={"type":"object","properties":{"loan_id":{"type":"integer"}},"required":["loan_id"]}),
        Tool(name="get_risk_assessments_by_customer",description="Get all risk assessments for a customer.",
             inputSchema={"type":"object","properties":{"customer_id":{"type":"integer"}},"required":["customer_id"]}),
        Tool(name="get_all_risk_assessments",        description="Get all risk assessments.",
             inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="run_risk_assessment",             description="Run a new automated risk assessment.",
             inputSchema={"type":"object","properties":{
                 "customer_id":{"type":"integer"},"loan_application_id":{"type":"integer"},
                 "credit_score":{"type":"integer"},"debt_to_income_ratio":{"type":"number"},
                 "loan_to_value_ratio":{"type":"number"},"notes":{"type":"string"}},
             "required":["customer_id","loan_application_id"]}),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    async with httpx.AsyncClient() as c:
        try:
            if   name == "get_risk_assessment_by_loan":
                r = await c.get(f"{BASE_URL}/api/v1/risk/loan/{arguments['loan_id']}/latest", timeout=30)
            elif name == "get_risk_assessments_by_customer":
                r = await c.get(f"{BASE_URL}/api/v1/risk/customer/{arguments['customer_id']}", timeout=30)
            elif name == "get_all_risk_assessments":
                r = await c.get(f"{BASE_URL}/api/v1/risk", timeout=30)
            elif name == "run_risk_assessment":
                payload = {"customerId":arguments["customer_id"],
                           "loanApplicationId":arguments["loan_application_id"],
                           "creditScore":arguments.get("credit_score",700),
                           "debtToIncomeRatio":arguments.get("debt_to_income_ratio",40.0),
                           "loanToValueRatio":arguments.get("loan_to_value_ratio",70.0),
                           "assessedBy":"RISK_MCP_AGENT",
                           "notes":arguments.get("notes","Automated MCP risk assessment")}
                r = await c.post(f"{BASE_URL}/api/v1/risk/assess", json=payload, timeout=30)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
            return [TextContent(type="text", text=json.dumps(r.json(), indent=2) if r.is_success else f"ERROR {r.status_code}: {r.text}")]
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
    uvicorn.run(starlette_app, host="0.0.0.0", port=9004, log_level="info")
