import os, httpx, json, uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Mount

BASE_URL = os.environ.get("KYC_SERVICE_URL", "http://localhost:8082")
app = Server("kyc-mcp-server")
sse = SseServerTransport("/messages/")

@app.list_tools()
async def list_tools():
    return [
        Tool(name="get_kyc_status",      description="Get latest KYC record for a customer.",
             inputSchema={"type":"object","properties":{"customer_id":{"type":"integer"}},"required":["customer_id"]}),
        Tool(name="get_all_kyc_records", description="Get all KYC records in the system.",
             inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="initiate_kyc",        description="Initiate KYC process for a customer.",
             inputSchema={"type":"object","properties":{"customer_id":{"type":"integer"}},"required":["customer_id"]}),
        Tool(name="verify_kyc",          description="Mark a KYC record as verified.",
             inputSchema={"type":"object","properties":{"kyc_id":{"type":"integer"},"officer":{"type":"string"}},"required":["kyc_id"]}),
        Tool(name="fail_kyc",            description="Fail a KYC record with a reason.",
             inputSchema={"type":"object","properties":{"kyc_id":{"type":"integer"},"reason":{"type":"string"}},"required":["kyc_id","reason"]}),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    async with httpx.AsyncClient() as c:
        try:
            if   name == "get_kyc_status":
                r = await c.get(f"{BASE_URL}/api/v1/kyc/customer/{arguments['customer_id']}/latest", timeout=30)
            elif name == "get_all_kyc_records":
                r = await c.get(f"{BASE_URL}/api/v1/kyc", timeout=30)
            elif name == "initiate_kyc":
                r = await c.post(f"{BASE_URL}/api/v1/kyc/customer/{arguments['customer_id']}/initiate", timeout=30)
            elif name == "verify_kyc":
                r = await c.put(f"{BASE_URL}/api/v1/kyc/{arguments['kyc_id']}/verify",
                                params={"officer": arguments.get("officer","MCP_AGENT")}, timeout=30)
            elif name == "fail_kyc":
                r = await c.put(f"{BASE_URL}/api/v1/kyc/{arguments['kyc_id']}/fail",
                                json={"reason": arguments["reason"]}, timeout=30)
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
    uvicorn.run(starlette_app, host="0.0.0.0", port=9002, log_level="info")
