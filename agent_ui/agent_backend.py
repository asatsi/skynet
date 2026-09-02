import asyncio
import json
import logging
import os
import sys
import time
from typing import AsyncGenerator, Dict, List, Any

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from mcp import ClientSession
from mcp.client.sse import sse_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent_backend")

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/sse")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")

app = FastAPI(title="Healthcare MCP Chat Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper to fetch active tools from MCP server
async def fetch_mcp_tools() -> List[Dict[str, Any]]:
    try:
        async with sse_client(MCP_SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_response = await session.list_tools()
                formatted_tools = []
                for tool in tools_response.tools:
                    formatted_tools.append({
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema if hasattr(tool, "inputSchema") else {}
                    })
                return formatted_tools
    except Exception as e:
        logger.error(f"Error fetching tools from MCP: {e}")
        return []

# Execute a single MCP tool call
async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    try:
        async with sse_client(MCP_SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                output = []
                for content in result.content:
                    if hasattr(content, "text"):
                        output.append(content.text)
                    else:
                        output.append(str(content))
                return "\n".join(output) if output else "Tool returned empty response."
    except Exception as e:
        return f"Error executing tool {tool_name}: {str(e)}"

@app.get("/api/status")
async def get_status():
    mcp_status = False
    mcp_tools_count = 0
    try:
        tools = await fetch_mcp_tools()
        mcp_status = True
        mcp_tools_count = len(tools)
    except Exception:
        pass

    ollama_status = False
    ollama_models = []
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            if resp.status_code == 200:
                ollama_status = True
                data = resp.json()
                ollama_models = [m.get("name") for m in data.get("models", [])]
    except Exception:
        pass

    return {
        "mcp_connected": mcp_status,
        "mcp_tools_count": mcp_tools_count,
        "ollama_connected": ollama_status,
        "ollama_models": ollama_models,
        "active_model": OLLAMA_MODEL,
        "mcp_url": MCP_SERVER_URL
    }

@app.get("/api/tools")
async def get_tools():
    tools = await fetch_mcp_tools()
    return {"tools": tools}

# ReAct Agent loop generator with streaming events
async def agent_react_stream(user_message: str, history: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
    def sse_event(event_type: str, data: Any) -> str:
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

    # Step 1: Discover available tools from MCP server
    yield sse_event("reasoning", {"step": 1, "title": "MCP Tool Discovery", "thought": "Connecting to Healthcare MCP server at " + MCP_SERVER_URL + " to discover available domain tools..."})
    
    tools = await fetch_mcp_tools()
    if not tools:
        yield sse_event("reasoning", {"step": 1, "title": "MCP Connection Warning", "thought": "Failed to connect to MCP server or 0 tools returned. Falling back to general reasoning."})
    else:
        yield sse_event("reasoning", {"step": 1, "title": "Tools Registered", "thought": f"Successfully initialized session with {len(tools)} Healthcare MCP tools (Patient Management, Claims, EHR, Appointments)."})

    # Format tools for system prompt context
    tools_summary = "\n".join([f"- `{t['name']}`: {t['description']} | Parameters: {json.dumps(t.get('inputSchema', {}).get('properties', {}))}" for t in tools])

    system_prompt = f"""You are an expert AI Healthcare Operations Assistant equipped with Model Context Protocol (MCP) tools.
You have access to the following 29 MCP tools to manage healthcare data across microservices:

{tools_summary}

CRITICAL OPERATIONAL INSTRUCTIONS:
1. When asked to perform actions, inspect data, or answer queries about patients, claims, medical records, lab results, or appointments, analyze which tool(s) to call.
2. Output your plan and reasoning first.
3. If you decide to call an MCP tool, output your thought and tool request in JSON format:
```json
{{
  "thought": "<Explain why you are calling this tool and what parameters you are choosing>",
  "tool_call": {{
    "name": "<tool_name>",
    "arguments": {{ <args_dict> }}
  }}
}}
```
4. If no more tool calls are needed or no tools apply, summarize the final answer clearly for the user in formatted markdown.
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-6:]: # Keep recent context
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    messages.append({"role": "user", "content": user_message})

    # Step 2: Agent reasoning loop (Up to 4 iterations)
    max_steps = 4
    current_step = 0

    async with httpx.AsyncClient(timeout=60.0) as http_client:
        while current_step < max_steps:
            current_step += 1
            yield sse_event("reasoning", {
                "step": current_step + 1,
                "title": f"Reasoning Cycle #{current_step}",
                "thought": f"Analyzing user intent & context with Ollama LLM ({OLLAMA_MODEL})..."
            })

            # Call Ollama API
            try:
                payload = {
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 0.1}
                }
                response = await http_client.post(f"{OLLAMA_URL}/api/chat", json=payload)
                if response.status_code != 200:
                    yield sse_event("error", f"Ollama API error {response.status_code}: {response.text}")
                    return

                res_json = response.json()
                assistant_msg = res_json.get("message", {}).get("content", "")
            except Exception as e:
                yield sse_event("error", f"Error communicating with Ollama: {str(e)}")
                return

            # Check if LLM output contains tool call JSON block
            tool_call_data = None
            if "```json" in assistant_msg:
                try:
                    json_str = assistant_msg.split("```json")[1].split("```")[0].strip()
                    parsed = json.loads(json_str)
                    if "tool_call" in parsed:
                        tool_call_data = parsed
                except Exception as parse_err:
                    logger.warning(f"Failed to parse tool call JSON: {parse_err}")

            if tool_call_data:
                thought = tool_call_data.get("thought", "Determined tool invocation based on user query.")
                tool_info = tool_call_data.get("tool_call", {})
                tool_name = tool_info.get("name")
                tool_args = tool_info.get("arguments", {})

                yield sse_event("reasoning", {
                    "step": current_step + 1,
                    "title": f"Decision: Execute Tool `{tool_name}`",
                    "thought": thought
                })

                yield sse_event("tool_call", {
                    "tool_name": tool_name,
                    "arguments": tool_args,
                    "timestamp": time.strftime("%H:%M:%S")
                })

                # Execute MCP tool call
                start_time = time.time()
                tool_result_str = await call_mcp_tool(tool_name, tool_args)
                latency_ms = int((time.time() - start_time) * 1000)

                yield sse_event("tool_result", {
                    "tool_name": tool_name,
                    "result": tool_result_str,
                    "latency_ms": latency_ms
                })

                # Append tool observation back into conversation messages for next step
                messages.append({"role": "assistant", "content": assistant_msg})
                messages.append({
                    "role": "user",
                    "content": f"[Tool Execution Result for `{tool_name}`]:\n{tool_result_str}\n\nNow provide the final response to the user or take the next required step."
                })
            else:
                # No tool call requested; this is the final answer
                yield sse_event("final_response", {
                    "content": assistant_msg
                })
                break

    yield sse_event("done", {"status": "complete"})

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message", "")
    history = data.get("history", [])

    return StreamingResponse(
        agent_react_stream(message, history),
        media_type="text/event-stream"
    )

# Static files setup
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Healthcare MCP Agent UI Backend Running</h1>"
