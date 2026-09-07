import httpx, json, uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Mount

BASE_URL = os.environ.get("LOAN_SERVICE_URL", "http://localhost:8086")
app = Server("loan-mcp-server")
sse = SseServerTransport("/messages/")

@app.list_tools()
async def list_tools():
    return [
        Tool(name="get_all_loans",
             description="Retrieve all loan applications.",
             inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="get_loan_by_id",
             description="Get a loan application by its integer ID.",
             inputSchema={"type":"object",
                          "properties":{"loan_id":{"type":"integer"}},"required":["loan_id"]}),
        Tool(name="get_loans_by_customer",
             description="Get all loans for a customer by customer ID.",
             inputSchema={"type":"object",
                          "properties":{"customer_id":{"type":"integer"}},"required":["customer_id"]}),
        Tool(name="get_loans_by_status",
             description="Get loans filtered by status (DRAFT/SUBMITTED/UNDER_REVIEW/APPROVED/REJECTED/DISBURSED).",
             inputSchema={"type":"object",
                          "properties":{"status":{"type":"string"}},"required":["status"]}),
        Tool(name="submit_loan",
             description="Submit a DRAFT loan application for review.",
             inputSchema={"type":"object",
                          "properties":{"loan_id":{"type":"integer"}},"required":["loan_id"]}),
        Tool(name="approve_loan",
             description="Approve a loan application.",
             inputSchema={"type":"object",
                          "properties":{"loan_id":{"type":"integer"},
                                        "approver":{"type":"string"},
                                        "notes":{"type":"string"}},
                          "required":["loan_id","approver"]}),
        Tool(name="reject_loan",
             description="Reject a loan application with a reason.",
             inputSchema={"type":"object",
                          "properties":{"loan_id":{"type":"integer"},
                                        "reason":{"type":"string"}},
                          "required":["loan_id","reason"]}),
        Tool(name="create_loan",
             description="Create a new loan application.",
             inputSchema={"type":"object",
                          "properties":{
                              "customer_id":{"type":"integer"},
                              "loan_type":{"type":"string"},
                              "amount":{"type":"number"},
                              "purpose":{"type":"string"},
                              "tenure_months":{"type":"integer"},
                              "priority":{"type":"string"}},
                          "required":["customer_id","loan_type","amount","purpose"]}),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    async with httpx.AsyncClient() as c:
        try:
            if name == "get_all_loans":
                r = await c.get(f"{BASE_URL}/api/v1/loans", timeout=30)
            elif name == "get_loan_by_id":
                r = await c.get(f"{BASE_URL}/api/v1/loans/{arguments['loan_id']}", timeout=30)
            elif name == "get_loans_by_customer":
                r = await c.get(f"{BASE_URL}/api/v1/loans/customer/{arguments['customer_id']}", timeout=30)
            elif name == "get_loans_by_status":
                r = await c.get(f"{BASE_URL}/api/v1/loans/status/{arguments['status']}", timeout=30)
            elif name == "submit_loan":
                r = await c.put(f"{BASE_URL}/api/v1/loans/{arguments['loan_id']}/submit", timeout=30)
            elif name == "approve_loan":
                r = await c.put(f"{BASE_URL}/api/v1/loans/{arguments['loan_id']}/approve",
                                json={"approver": arguments["approver"],
                                      "notes": arguments.get("notes","Approved via MCP")}, timeout=30)
            elif name == "reject_loan":
                r = await c.put(f"{BASE_URL}/api/v1/loans/{arguments['loan_id']}/reject",
                                json={"reason": arguments["reason"]}, timeout=30)
            elif name == "create_loan":
                payload = {
                    "customerId":    arguments["customer_id"],
                    "loanType":      arguments["loan_type"],
                    "amount":        arguments["amount"],
                    "purpose":       arguments["purpose"],
                    "tenureMonths":  arguments.get("tenure_months", 36),
                    "priority":      arguments.get("priority","MEDIUM"),
                    "currency":      "USD",
                }
                r = await c.post(f"{BASE_URL}/api/v1/loans", json=payload, timeout=30)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
            return [TextContent(type="text",
                                text=json.dumps(r.json(), indent=2) if r.is_success
                                     else f"ERROR {r.status_code}: {r.text}")]
        except Exception as e:
            return [TextContent(type="text", text=f"ERROR: {e}")]

async def handle_sse(scope, receive, send):
    async with sse.connect_sse(scope, receive, send) as streams:
        await app.run(streams[0], streams[1], app.create_initialization_options())

_msg = Starlette(debug=False, routes=[Mount("/messages/", app=sse.handle_post_message)])

async def starlette_app(scope, receive, send):
    if scope["type"] == "http" and scope.get("path","").rstrip("/") == "/sse":
        await handle_sse(scope, receive, send)
    else:
        await _msg(scope, receive, send)

if __name__ == "__main__":
    uvicorn.run(starlette_app, host="0.0.0.0", port=9007, log_level="info")
