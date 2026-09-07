import os, httpx, json, uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Mount

BASE_URL = os.environ.get("CUSTOMER_SERVICE_URL", "http://localhost:8081")
app = Server("customer-mcp-server")
sse = SseServerTransport("/messages/")

@app.list_tools()
async def list_tools():
    return [
        Tool(name="get_all_customers",         description="Retrieve all registered customers.",
             inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="get_customer_by_id",         description="Get a customer by integer ID.",
             inputSchema={"type":"object","properties":{"customer_id":{"type":"integer"}},"required":["customer_id"]}),
        Tool(name="search_customers",           description="Search customers by company or person name.",
             inputSchema={"type":"object","properties":{"name":{"type":"string"}},"required":["name"]}),
        Tool(name="get_customer_credit_profile",description="Get credit eligibility profile for a customer.",
             inputSchema={"type":"object","properties":{"customer_id":{"type":"integer"}},"required":["customer_id"]}),
        Tool(name="create_customer",            description="Create a new customer record.",
             inputSchema={"type":"object","properties":{
                 "first_name":{"type":"string"},"last_name":{"type":"string"},
                 "company_name":{"type":"string"},"email":{"type":"string"},
                 "phone":{"type":"string"},"annual_revenue":{"type":"number"},
                 "business_type":{"type":"string"},"credit_score":{"type":"integer"}},
             "required":["first_name","last_name","company_name","email"]}),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    async with httpx.AsyncClient() as c:
        try:
            if   name == "get_all_customers":
                r = await c.get(f"{BASE_URL}/api/v1/customers", timeout=30)
            elif name == "get_customer_by_id":
                r = await c.get(f"{BASE_URL}/api/v1/customers/{arguments['customer_id']}", timeout=30)
            elif name == "search_customers":
                r = await c.get(f"{BASE_URL}/api/v1/customers/search", params={"name": arguments["name"]}, timeout=30)
            elif name == "get_customer_credit_profile":
                r = await c.get(f"{BASE_URL}/api/v1/customers/{arguments['customer_id']}/credit-profile", timeout=30)
            elif name == "create_customer":
                body = {k: v for k, v in arguments.items()}
                r = await c.post(f"{BASE_URL}/api/v1/customers", json=body, timeout=30)
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
    uvicorn.run(starlette_app, host="0.0.0.0", port=9001, log_level="info")
