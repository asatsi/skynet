"""
MCP Gateway — single entry point for tool discovery, routing and audit.
Aggregates tools from all 7 domain MCP servers and routes calls.
"""
import os, json, asyncio, time, logging
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mcp.client.sse import sse_client
from mcp import ClientSession
import uvicorn

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [GATEWAY] %(message)s")
log = logging.getLogger("gateway")

DOMAIN_SERVERS = {
    "customer":  os.getenv("MCP_CUSTOMER_URL",  "http://localhost:9001") + "/sse",
    "kyc":       os.getenv("MCP_KYC_URL",       "http://localhost:9002") + "/sse",
    "document":  os.getenv("MCP_DOCUMENT_URL",  "http://localhost:9003") + "/sse",
    "risk":      os.getenv("MCP_RISK_URL",      "http://localhost:9004") + "/sse",
    "workflow":  os.getenv("MCP_WORKFLOW_URL",  "http://localhost:9005") + "/sse",
    "knowledge": os.getenv("MCP_KNOWLEDGE_URL", "http://localhost:9006") + "/sse",
    "loan":      os.getenv("MCP_LOAN_URL",      "http://localhost:9007") + "/sse",
}

# In-memory audit log
AUDIT_LOG: list[dict] = []

gw = FastAPI(title="MCP Gateway", version="1.0.0")


async def _list_tools(server_url: str) -> list[dict]:
    try:
        async with sse_client(server_url) as (r, w):
            async with ClientSession(r, w) as session:
                await session.initialize()
                result = await session.list_tools()
                return [
                    {"name": t.name, "description": t.description,
                     "inputSchema": t.inputSchema}
                    for t in result.tools
                ]
    except Exception as e:
        log.warning(f"Could not reach {server_url}: {e}")
        return []


async def _call_tool(server_url: str, tool_name: str,
                     arguments: dict) -> str:
    async with sse_client(server_url) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments=arguments)
            return result.content[0].text if result.content else "null"


@gw.get("/health")
async def health():
    return {"status": "UP", "service": "MCP Gateway", "port": 9000}


@gw.get("/tools")
async def list_all_tools():
    """Discover and return all tools from all registered MCP servers."""
    all_tools: list[dict] = []
    tasks = {name: asyncio.create_task(_list_tools(url))
             for name, url in DOMAIN_SERVERS.items()}
    for domain, task in tasks.items():
        tools = await task
        for t in tools:
            all_tools.append({**t, "domain": domain,
                               "server": DOMAIN_SERVERS[domain]})
    log.info(f"Tool discovery: {len(all_tools)} tools across "
             f"{len(DOMAIN_SERVERS)} servers")
    return {"total": len(all_tools), "tools": all_tools}


@gw.get("/tools/{domain}")
async def list_domain_tools(domain: str):
    """List tools for a specific domain MCP server."""
    url = DOMAIN_SERVERS.get(domain)
    if not url:
        return JSONResponse({"error": f"Unknown domain: {domain}"}, status_code=404)
    tools = await _list_tools(url)
    return {"domain": domain, "total": len(tools), "tools": tools}


@gw.post("/call/{tool_name}")
async def call_tool(tool_name: str, request: Request):
    """Route a tool call to the appropriate domain MCP server."""
    body      = await request.json()
    arguments = body.get("arguments", {})
    domain    = body.get("domain")          # optional hint

    # Find which server owns this tool
    target_url   = None
    target_domain = domain
    if domain and domain in DOMAIN_SERVERS:
        target_url    = DOMAIN_SERVERS[domain]
        target_domain = domain
    else:
        # Discover by scanning all servers
        for d, url in DOMAIN_SERVERS.items():
            tools = await _list_tools(url)
            if any(t["name"] == tool_name for t in tools):
                target_url    = url
                target_domain = d
                break

    if not target_url:
        return JSONResponse(
            {"error": f"Tool '{tool_name}' not found on any MCP server"},
            status_code=404)

    t_start = time.time()
    try:
        result = await _call_tool(target_url, tool_name, arguments)
        status = "SUCCESS"
    except Exception as e:
        result = json.dumps({"error": str(e)})
        status = "ERROR"
    elapsed_ms = round((time.time() - t_start) * 1000)

    # Audit log entry
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "tool":      tool_name,
        "domain":    target_domain,
        "server":    target_url,
        "arguments": arguments,
        "status":    status,
        "elapsed_ms": elapsed_ms,
    }
    AUDIT_LOG.append(entry)
    log.info(f"{status} | {tool_name} | {target_domain} | {elapsed_ms}ms")

    return {"tool": tool_name, "domain": target_domain,
            "status": status, "elapsed_ms": elapsed_ms,
            "result": json.loads(result) if result else None}


@gw.get("/audit")
async def get_audit_log(limit: int = 50):
    """Return the last N audit log entries."""
    return {"total": len(AUDIT_LOG), "entries": AUDIT_LOG[-limit:]}


@gw.get("/servers")
async def list_servers():
    """Return all registered MCP servers."""
    return {"servers": [
        {"domain": d, "url": u} for d, u in DOMAIN_SERVERS.items()
    ]}


if __name__ == "__main__":
    uvicorn.run(gw, host="0.0.0.0", port=9000, log_level="info")
