"""Main MCP server for the healthcare microservices, served over HTTP/SSE.

Endpoints:
    GET  /sse       - SSE stream endpoint for MCP clients
    POST /messages/ - client-to-server message endpoint

Run directly with:
    python -m healthcare_mcp.server
or via the convenience script:
    python run.py
"""

import logging
from typing import Any

import mcp.types as types
import uvicorn
from mcp.server import Server
from mcp.server.lowlevel.server import LifespanResultT, ServerRequestContext
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response
from starlette.routing import Mount, Route

from . import __version__
from .config import MCP_SERVER_HOST, MCP_SERVER_PORT
from .tools import appointment_tools, claims_tools, ehr_tools, patient_tools

logger = logging.getLogger("healthcare_mcp")

# Aggregate tool definitions and handlers from all 4 service modules.
_TOOL_MODULES = [patient_tools, claims_tools, ehr_tools, appointment_tools]

ALL_TOOLS: list[types.Tool] = [tool for module in _TOOL_MODULES for tool in module.TOOLS]

TOOL_HANDLERS: dict[str, Any] = {}
for _module in _TOOL_MODULES:
    TOOL_HANDLERS.update(_module.HANDLERS)


async def handle_list_tools(
    ctx: ServerRequestContext[LifespanResultT],
    params: types.PaginatedRequestParams | None,
) -> types.ListToolsResult:
    """Return the full list of healthcare tools to the MCP client."""
    return types.ListToolsResult(tools=ALL_TOOLS)


async def handle_call_tool(
    ctx: ServerRequestContext[LifespanResultT],
    params: types.CallToolRequestParams,
) -> types.CallToolResult:
    """Dispatch a tool call to the matching handler and wrap the result."""
    handler = TOOL_HANDLERS.get(params.name)
    if handler is None:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Error: unknown tool '{params.name}'")],
            isError=True,
        )
    try:
        content = await handler(params.arguments or {})
        return types.CallToolResult(content=content)
    except KeyError as exc:
        return types.CallToolResult(
            content=[
                types.TextContent(type="text", text=f"Error: missing required argument {exc}")
            ],
            isError=True,
        )
    except Exception as exc:  # noqa: BLE001 - surface any failure to the MCP client
        logger.exception("Tool '%s' failed", params.name)
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Error: tool '{params.name}' failed: {exc}")],
            isError=True,
        )


def create_server() -> Server:
    """Create the MCP server instance with all healthcare tools registered."""
    return Server(
        name="healthcare-mcp",
        version=__version__,
        on_list_tools=handle_list_tools,
        on_call_tool=handle_call_tool,
    )


def create_app() -> Starlette:
    """Create the Starlette ASGI app exposing the MCP server over SSE."""
    server = create_server()
    sse = SseServerTransport("/messages/")

    async def handle_sse(request) -> Response:
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await server.run(
                streams[0],
                streams[1],
                server.create_initialization_options(),
            )
        # Return an empty response to avoid a NoneType error on disconnect.
        return Response()

    routes = [
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Mount("/messages/", app=sse.handle_post_message),
    ]

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
        )
    ]

    return Starlette(routes=routes, middleware=middleware)


def main() -> None:
    """Run the MCP server with uvicorn."""
    logging.basicConfig(level=logging.INFO)
    app = create_app()
    logger.info(
        "Starting healthcare MCP server on %s:%s (SSE at /sse, messages at /messages/)",
        MCP_SERVER_HOST,
        MCP_SERVER_PORT,
    )
    uvicorn.run(app, host=MCP_SERVER_HOST, port=MCP_SERVER_PORT)


if __name__ == "__main__":
    main()
