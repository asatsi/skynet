"""
MCP Gateway Server — port 9000
Responsibilities per spec:
  Tool Discovery, Tool Registration, Authentication, Authorization,
  Auditing, Metrics, Routing
"""
import json, uuid, datetime, uvicorn
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

try:
    from mcp.client.sse import sse_client
    from mcp.client.session import ClientSession
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    await discover_all_tools()        # runs BEFORE server accepts requests
    yield                             # server is live here
    tool_registry.clear()

gateway = FastAPI(title="MCP Gateway", version="1.0.0",
                  description="Central MCP Gateway — Tool Discovery, Routing, Auditing",
                  lifespan=lifespan)
gateway.add_middleware(CORSMiddleware, allow_origins=["*"],
                       allow_methods=["*"], allow_headers=["*"])

# ── Registry & audit state ────────────────────────────────────────────────────
tool_registry: dict[str, dict] = {}   # tool_name → {server, url, description, schema}
audit_log:     list[dict]      = []   # chronological tool-call audit trail
metrics:       dict[str, dict] = defaultdict(lambda: {"calls": 0, "errors": 0, "total_ms": 0})

import os as _gw_os
MCP_SERVERS = {
    "customer":  _gw_os.environ.get("CUSTOMER_MCP_URL",  "http://localhost:9001/sse"),
    "kyc":       _gw_os.environ.get("KYC_MCP_URL",       "http://localhost:9002/sse"),
    "document":  _gw_os.environ.get("DOCUMENT_MCP_URL",  "http://localhost:9003/sse"),
    "risk":      _gw_os.environ.get("RISK_MCP_URL",      "http://localhost:9004/sse"),
    "workflow":  _gw_os.environ.get("WORKFLOW_MCP_URL",  "http://localhost:9005/sse"),
    "knowledge": _gw_os.environ.get("KNOWLEDGE_MCP_URL", "http://localhost:9006/sse"),
}

# ── Tool discovery ─────────────────────────────────────────────────────────────
async def _discover_from(server_name: str, url: str) -> int:
    if not MCP_AVAILABLE:
        return 0
    try:
        async with sse_client(url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                listed = await session.list_tools()
                for t in listed.tools:
                    tool_registry[t.name] = {
                        "server":      server_name,
                        "url":         url,
                        "name":        t.name,
                        "description": t.description or "",
                        "input_schema": (t.inputSchema or {}) if hasattr(t, "inputSchema")
                                        else (t.input_schema or {}) if hasattr(t, "input_schema")
                                        else {},
                    }
                return len(listed.tools)
    except Exception as exc:
        print(f"  ⚠️  [{server_name}] discovery failed: {exc}")
        return 0

async def discover_all_tools():
    print("[MCP Gateway] Discovering tools from all MCP servers…")
    total = 0
    for name, url in MCP_SERVERS.items():
        n = await _discover_from(name, url)
        print(f"  {'✅' if n else '⚠️ '} {name}: {n} tools")
        total += n
    print(f"[MCP Gateway] Ready — {total} tools registered across {len(MCP_SERVERS)} servers")

# ── REST API: Tool Discovery ───────────────────────────────────────────────────
@gateway.get("/gateway/tools")
async def list_tools(server: str = None):
    """List all registered tools, optionally filtered by server name."""
    tools = list(tool_registry.values())
    if server:
        # support comma-separated list: ?server=customer,risk
        svcs = {s.strip() for s in server.split(",")}
        tools = [t for t in tools if t["server"] in svcs]
    return {"tools": tools, "total": len(tools),
            "servers": list(MCP_SERVERS.keys())}

@gateway.get("/gateway/tools/{tool_name}")
async def get_tool(tool_name: str):
    if tool_name not in tool_registry:
        raise HTTPException(404, f"Tool '{tool_name}' not registered")
    return tool_registry[tool_name]

# ── REST API: Tool Routing (core gateway function) ────────────────────────────
@gateway.post("/gateway/call/{tool_name}")
async def call_tool(tool_name: str, request: Request):
    """Route a tool call to the appropriate MCP server."""
    if tool_name not in tool_registry:
        # Try re-discovery once
        await discover_all_tools()
        if tool_name not in tool_registry:
            raise HTTPException(404, f"Tool '{tool_name}' not found in registry")

    entry    = tool_registry[tool_name]
    args     = await request.json() if request.headers.get("content-type","").startswith("application/json") else {}
    call_id  = str(uuid.uuid4())[:8]
    started  = datetime.datetime.utcnow()

    audit_entry = {
        "call_id":    call_id,
        "timestamp":  started.isoformat(),
        "tool":       tool_name,
        "server":     entry["server"],
        "arguments":  args,
        "status":     "IN_PROGRESS",
        "result":     None,
        "error":      None,
        "duration_ms": None,
    }
    audit_log.append(audit_entry)

    if not MCP_AVAILABLE:
        audit_entry["status"] = "ERROR"
        audit_entry["error"]  = "mcp package not installed"
        raise HTTPException(500, "mcp package not installed")

    try:
        async with sse_client(entry["url"]) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result   = await session.call_tool(tool_name, args)
                content  = result.content[0].text if result.content else ""
                duration = int((datetime.datetime.utcnow() - started).total_seconds() * 1000)

                audit_entry["status"]      = "SUCCESS"
                audit_entry["result"]      = content[:500]
                audit_entry["duration_ms"] = duration
                metrics[tool_name]["calls"]    += 1
                metrics[tool_name]["total_ms"] += duration

                return {"call_id": call_id, "tool": tool_name,
                        "server": entry["server"], "result": content,
                        "duration_ms": duration}

    except Exception as exc:
        duration = int((datetime.datetime.utcnow() - started).total_seconds() * 1000)
        audit_entry["status"]      = "ERROR"
        audit_entry["error"]       = str(exc)
        audit_entry["duration_ms"] = duration
        metrics[tool_name]["errors"] += 1
        raise HTTPException(500, f"Tool call failed: {exc}")

# ── REST API: Audit & Metrics ─────────────────────────────────────────────────
@gateway.get("/gateway/audit")
async def get_audit(limit: int = 50):
    return {"calls": list(reversed(audit_log))[:limit], "total": len(audit_log)}

@gateway.get("/gateway/metrics")
async def get_metrics():
    return {"tools": dict(metrics), "registry_size": len(tool_registry)}

@gateway.get("/gateway/health")
async def health():
    """Check connectivity to every registered MCP server."""
    status = {}
    if not MCP_AVAILABLE:
        return {"error": "mcp not installed", "servers": {}}
    for name, url in MCP_SERVERS.items():
        try:
            async with sse_client(url) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    listed = await session.list_tools()
                    status[name] = {"status": "UP", "tools": len(listed.tools)}
        except Exception as e:
            status[name] = {"status": "DOWN", "error": str(e)[:80]}
    return {"servers": status, "registered_tools": len(tool_registry)}

@gateway.post("/gateway/refresh")
async def refresh_registry():
    """Re-discover tools from all MCP servers."""
    tool_registry.clear()
    await discover_all_tools()
    return {"tools_registered": len(tool_registry)}

if __name__ == "__main__":
    uvicorn.run(gateway, host="0.0.0.0", port=9099, log_level="info")
