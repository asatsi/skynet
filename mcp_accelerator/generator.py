import json
import os
import re
from typing import List, Dict, Any
from mcp_accelerator.models import DomainGroup, ToolEndpoint, ToolParameter

class MCPServerGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = os.path.abspath(output_dir)

    def generate_domain_servers(self, domain_groups: List[DomainGroup], base_port: int = 8100) -> List[str]:
        generated_paths: List[str] = []
        port_offset = 0

        for domain in domain_groups:
            domain_port = base_port + port_offset
            port_offset += 1

            server_dir = os.path.join(self.output_dir, f"{domain.name}_mcp")
            os.makedirs(server_dir, exist_ok=True)
            os.makedirs(os.path.join(server_dir, "src", domain.name), exist_ok=True)

            # Generate files
            self._generate_server_py(server_dir, domain, domain_port)
            self._generate_run_py(server_dir, domain, domain_port)
            self._generate_pyproject_toml(server_dir, domain)
            self._generate_readme(server_dir, domain, domain_port)

            generated_paths.append(server_dir)

        return generated_paths

    def _generate_server_py(self, server_dir: str, domain: DomainGroup, port: int):
        code_lines = [
            "# Auto-generated MCP Server by mcp_accelerator",
            "import os",
            "import json",
            "import asyncio",
            "import httpx",
            "from typing import Dict, Any, Optional, List",
            "from mcp.server.fastmcp import FastMCP",
            "",
            f'mcp = FastMCP("{domain.name.replace("_", " ").title()} MCP Server")',
            "",
            "# Shared async HTTP Client helper",
            "async def _make_api_request(url: str, method: str = 'GET', json_data: Any = None, params: Any = None) -> str:",
            "    async with httpx.AsyncClient(timeout=30.0) as client:",
            "        try:",
            "            resp = await client.request(method=method, url=url, json=json_data, params=params)",
            "            if resp.status_code in [200, 201]:",
            "                try:",
            "                    return json.dumps(resp.json(), indent=2)",
            "                except Exception:",
            "                    return resp.text",
            "            elif resp.status_code == 204:",
            "                return 'Success (204 No Content)'",
            "            else:",
            "                return f'HTTP Error {resp.status_code}: {resp.text}'",
            "        except Exception as e:",
            "            return f'Request Exception: {str(e)}'",
            ""
        ]

        # Generate tool function definitions
        for tool in domain.tools:
            code_lines.extend(self._generate_tool_code(tool))

        server_py_path = os.path.join(server_dir, "src", domain.name, "server.py")
        with open(server_py_path, "w", encoding="utf-8") as f:
            f.write("\n".join(code_lines))

    def _generate_tool_code(self, tool: ToolEndpoint) -> List[str]:
        lines = []
        func_name = tool.name
        docstring = tool.description.replace('"', '\\"')

        # Construct function arguments
        arg_defs = []
        param_names = []
        path_params = []
        query_params = []
        body_props = []

        # Find path parameters like {id} or {patientId}
        path_param_matches = re.findall(r'\{([^}]+)\}', tool.path)
        for p in path_param_matches:
            path_params.append(p)
            arg_defs.append(f"{p}: Any")
            param_names.append(p)

        # OpenAPI parameters
        for p in tool.parameters:
            if p.name not in param_names:
                arg_defs.append(f"{p.name}: Optional[{self._python_type(p.param_type)}] = None")
                param_names.append(p.name)
                if "[path]" in p.description or p.name in tool.path:
                    path_params.append(p.name)
                else:
                    query_params.append(p.name)

        # Request body properties schema
        if tool.request_body_schema and "properties" in tool.request_body_schema:
            props = tool.request_body_schema.get("properties", {})
            for prop_name, prop_schema in props.items():
                if prop_name not in param_names:
                    p_type = prop_schema.get("type", "string")
                    arg_defs.append(f"{prop_name}: Optional[{self._python_type(p_type)}] = None")
                    param_names.append(prop_name)
                    body_props.append(prop_name)

        args_str = ", ".join(arg_defs)

        lines.append(f'@mcp.tool(description="{docstring}")')
        lines.append(f"async def {func_name}({args_str}) -> str:")
        
        # Build path interpolation
        formatted_path = tool.path
        for p in path_params:
            formatted_path = formatted_path.replace(f"{{{p}}}", f"{{{p}}}")

        lines.append(f'    url = f"{tool.base_url}{formatted_path}"')
        
        # Build query parameters dictionary
        if query_params:
            lines.append("    params = {}")
            for qp in query_params:
                lines.append(f"    if {qp} is not None: params['{qp}'] = {qp}")
        else:
            lines.append("    params = None")

        # Build JSON body dictionary
        if body_props:
            lines.append("    json_body = {}")
            for bp in body_props:
                lines.append(f"    if {bp} is not None: json_body['{bp}'] = {bp}")
        else:
            lines.append("    json_body = None")

        lines.append(f'    return await _make_api_request(url, method="{tool.http_method}", json_data=json_body, params=params)')
        lines.append("")
        return lines

    def _python_type(self, json_type: str) -> str:
        jt = json_type.lower()
        if jt in ["integer", "int"]:
            return "int"
        elif jt in ["number", "float", "double"]:
            return "float"
        elif jt in ["boolean", "bool"]:
            return "bool"
        elif jt in ["array", "list"]:
            return "List[Any]"
        elif jt in ["object", "dict"]:
            return "Dict[str, Any]"
        else:
            return "str"

    def _generate_run_py(self, server_dir: str, domain: DomainGroup, port: int):
        code = f"""# /// script
# dependencies = [
#   "mcp>=1.2.0,<2.0.0",
#   "httpx>=0.25.0",
#   "uvicorn>=0.24.0",
# ]
# ///

import os
import sys

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from {domain.name}.server import mcp

if __name__ == "__main__":
    print(f"Launching {domain.name} MCP Server on port {port}...")
    mcp.run()
"""
        with open(os.path.join(server_dir, "run.py"), "w", encoding="utf-8") as f:
            f.write(code)

    def _generate_pyproject_toml(self, server_dir: str, domain: DomainGroup):
        toml_content = f"""[project]
name = "{domain.name.replace('_', '-')}-mcp"
version = "0.1.0"
description = "MCP Server for {domain.name} domain tools"
requires-python = ">=3.11"
dependencies = [
    "mcp>=1.2.0,<2.0.0",
    "httpx>=0.25.0",
    "uvicorn>=0.24.0",
    "starlette>=0.27.0",
]

[tool.uv]
package = false
"""
        with open(os.path.join(server_dir, "pyproject.toml"), "w", encoding="utf-8") as f:
            f.write(toml_content)

    def _generate_readme(self, server_dir: str, domain: DomainGroup, port: int):
        tool_list = "\n".join([f"- `{t.name}`: {t.description} (`{t.http_method} {t.path}`)" for t in domain.tools])
        services_list = "\n".join([f"- **{s.name}** (Port {s.port}): {s.path}" for s in domain.services])

        readme_content = f"""# {domain.name.replace('_', ' ').title()} MCP Server

Auto-generated MCP (Model Context Protocol) domain server.

## Microservices Included

{services_list}

## Exposed MCP Tools ({len(domain.tools)})

{tool_list}

## How to Run

Run with `uv`:

```bash
cd {domain.name}_mcp
uv run python run.py
```
"""
        with open(os.path.join(server_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme_content)
