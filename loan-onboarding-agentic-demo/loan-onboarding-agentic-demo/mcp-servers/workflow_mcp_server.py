import os, httpx, json, uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Mount

BASE_URL = os.environ.get("WORKFLOW_SERVICE_URL", "http://localhost:8085")
app = Server("workflow-mcp-server")
sse = SseServerTransport("/messages/")

@app.list_tools()
async def list_tools():
    return [
        Tool(name="get_all_workflows",      description="Get all workflow instances.",
             inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="get_workflow_by_loan",   description="Get workflow instance for a loan.",
             inputSchema={"type":"object","properties":{"loan_id":{"type":"integer"}},"required":["loan_id"]}),
        Tool(name="get_workflow_summary",   description="Get concise workflow progress summary for a loan.",
             inputSchema={"type":"object","properties":{"loan_id":{"type":"integer"}},"required":["loan_id"]}),
        Tool(name="initiate_workflow",      description="Start the onboarding workflow for a loan.",
             inputSchema={"type":"object","properties":{
                 "loan_application_id":{"type":"integer"},"customer_id":{"type":"integer"},
                 "officer":{"type":"string"}},"required":["loan_application_id","customer_id"]}),
        Tool(name="complete_workflow_step", description="Mark a workflow step as completed.",
             inputSchema={"type":"object","properties":{
                 "step_id":{"type":"integer"},"officer":{"type":"string"},"notes":{"type":"string"}},
             "required":["step_id"]}),
        Tool(name="approve_workflow_step",  description="Human approval of a workflow step (HITL).",
             inputSchema={"type":"object","properties":{
                 "step_id":{"type":"integer"},"approver":{"type":"string"},"notes":{"type":"string"}},
             "required":["step_id","approver"]}),
        Tool(name="reject_workflow_step",   description="Reject a workflow step with reason.",
             inputSchema={"type":"object","properties":{
                 "step_id":{"type":"integer"},"rejector":{"type":"string"},"reason":{"type":"string"}},
             "required":["step_id","rejector","reason"]}),
        Tool(name="get_pending_approvals",  description="Get all workflows awaiting human approval.",
             inputSchema={"type":"object","properties":{},"required":[]}),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    async with httpx.AsyncClient() as c:
        try:
            if   name == "get_all_workflows":
                r = await c.get(f"{BASE_URL}/api/v1/workflows", timeout=30)
            elif name == "get_workflow_by_loan":
                r = await c.get(f"{BASE_URL}/api/v1/workflows/loan/{arguments['loan_id']}", timeout=30)
            elif name == "get_workflow_summary":
                r = await c.get(f"{BASE_URL}/api/v1/workflows/loan/{arguments['loan_id']}/summary", timeout=30)
            elif name == "initiate_workflow":
                r = await c.post(f"{BASE_URL}/api/v1/workflows/initiate",
                                 json={"loanApplicationId":arguments["loan_application_id"],
                                       "customerId":arguments["customer_id"],
                                       "officer":arguments.get("officer","SYSTEM")}, timeout=30)
            elif name == "complete_workflow_step":
                r = await c.put(f"{BASE_URL}/api/v1/workflows/steps/{arguments['step_id']}/complete",
                                json={"officer":arguments.get("officer","SYSTEM"),"notes":arguments.get("notes","")}, timeout=30)
            elif name == "approve_workflow_step":
                r = await c.put(f"{BASE_URL}/api/v1/workflows/steps/{arguments['step_id']}/approve",
                                json={"approver":arguments["approver"],"notes":arguments.get("notes","Approved")}, timeout=30)
            elif name == "reject_workflow_step":
                r = await c.put(f"{BASE_URL}/api/v1/workflows/steps/{arguments['step_id']}/reject",
                                json={"rejector":arguments["rejector"],"reason":arguments["reason"]}, timeout=30)
            elif name == "get_pending_approvals":
                r = await c.get(f"{BASE_URL}/api/v1/workflows", timeout=30)
                items = [w for w in r.json() if w.get("status") == "AWAITING_APPROVAL"]
                return [TextContent(type="text", text=json.dumps(items, indent=2))]
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
    uvicorn.run(starlette_app, host="0.0.0.0", port=9005, log_level="info")
