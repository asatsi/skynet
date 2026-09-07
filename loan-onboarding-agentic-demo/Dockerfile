FROM python:3.11-slim
WORKDIR /app

# Install deps first (cached layer)
COPY mcp-servers/requirements.txt ./mcp-servers/requirements.txt
RUN pip install --no-cache-dir -r mcp-servers/requirements.txt

# Copy full project (MCP servers need knowledge/ dir for knowledge_mcp)
COPY mcp-servers/ ./mcp-servers/
COPY knowledge/   ./knowledge/

# SERVER env var selects which server to run (e.g. customer_mcp_server)
ENV SERVER=customer_mcp_server
CMD python3 mcp-servers/${SERVER}.py
