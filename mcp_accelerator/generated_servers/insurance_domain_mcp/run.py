# /// script
# dependencies = [
#   "mcp>=1.2.0,<2.0.0",
#   "httpx>=0.25.0",
#   "uvicorn>=0.24.0",
# ]
# ///

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from insurance_domain.server import mcp

if __name__ == "__main__":
    print(f"Launching insurance_domain MCP Server on port 8102...")
    mcp.run()
