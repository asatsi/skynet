#!/usr/bin/env python3
"""Simple script to run the healthcare MCP server."""
import uvicorn

from healthcare_mcp.config import MCP_SERVER_HOST, MCP_SERVER_PORT
from healthcare_mcp.server import create_app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host=MCP_SERVER_HOST, port=MCP_SERVER_PORT)
