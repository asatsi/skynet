# /// script
# dependencies = [
#   "fastapi>=0.100.0",
#   "uvicorn>=0.24.0",
#   "httpx>=0.25.0",
#   "mcp>=0.9.0",
#   "sse-starlette>=1.0.0",
# ]
# ///

import os
import sys
import uvicorn

if __name__ == "__main__":
    print("==========================================================")
    print(" Launching Healthcare MCP Agent UI on http://localhost:8090 ")
    print("==========================================================")
    uvicorn.run("agent_backend:app", host="0.0.0.0", port=8090, reload=True)
