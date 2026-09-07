import os, httpx, json, uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Mount

BASE_URL = os.environ.get("DOCUMENT_SERVICE_URL", "http://localhost:8083")
app = Server("document-mcp-server")
sse = SseServerTransport("/messages/")

@app.list_tools()
async def list_tools():
    return [
        Tool(name="get_documents_by_loan",     description="Get all documents for a loan application.",
             inputSchema={"type":"object","properties":{"loan_id":{"type":"integer"}},"required":["loan_id"]}),
        Tool(name="get_documents_by_customer", description="Get all documents for a customer.",
             inputSchema={"type":"object","properties":{"customer_id":{"type":"integer"}},"required":["customer_id"]}),
        Tool(name="get_document_checklist",    description="Get document verification checklist for a loan.",
             inputSchema={"type":"object","properties":{"loan_id":{"type":"integer"}},"required":["loan_id"]}),
        Tool(name="verify_document",           description="Mark a document as verified.",
             inputSchema={"type":"object","properties":{"document_id":{"type":"integer"},"officer":{"type":"string"}},"required":["document_id"]}),
        Tool(name="reject_document",           description="Reject a document with a reason.",
             inputSchema={"type":"object","properties":{"document_id":{"type":"integer"},"reason":{"type":"string"}},"required":["document_id","reason"]}),
        Tool(name="register_document",         description="Register a new document for a loan/customer.",
             inputSchema={"type":"object","properties":{
                 "customer_id":{"type":"integer"},"loan_application_id":{"type":"integer"},
                 "document_type":{"type":"string"},"file_name":{"type":"string"}},
             "required":["customer_id","loan_application_id","document_type","file_name"]}),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    async with httpx.AsyncClient() as c:
        try:
            if   name == "get_documents_by_loan":
                r = await c.get(f"{BASE_URL}/api/v1/documents/loan/{arguments['loan_id']}", timeout=30)
            elif name == "get_documents_by_customer":
                r = await c.get(f"{BASE_URL}/api/v1/documents/customer/{arguments['customer_id']}", timeout=30)
            elif name == "get_document_checklist":
                r = await c.get(f"{BASE_URL}/api/v1/documents/loan/{arguments['loan_id']}/checklist", timeout=30)
            elif name == "verify_document":
                r = await c.put(f"{BASE_URL}/api/v1/documents/{arguments['document_id']}/verify",
                                params={"officer": arguments.get("officer","MCP_AGENT")}, timeout=30)
            elif name == "reject_document":
                r = await c.put(f"{BASE_URL}/api/v1/documents/{arguments['document_id']}/reject",
                                json={"reason": arguments["reason"]}, timeout=30)
            elif name == "register_document":
                payload = {"customerId":arguments["customer_id"],"loanApplicationId":arguments["loan_application_id"],
                           "documentType":arguments["document_type"],"fileName":arguments["file_name"],
                           "fileSize":arguments.get("file_size","Unknown")}
                r = await c.post(f"{BASE_URL}/api/v1/documents", json=payload, timeout=30)
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
    uvicorn.run(starlette_app, host="0.0.0.0", port=9003, log_level="info")
