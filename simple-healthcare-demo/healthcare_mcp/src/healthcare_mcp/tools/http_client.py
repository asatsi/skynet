"""Shared HTTP helpers for the healthcare MCP tools.

Wraps httpx calls with consistent error handling so every tool returns a
human-readable TextContent result instead of raising transport exceptions
through the MCP protocol layer.
"""

import json
from typing import Any

import httpx
from mcp.types import TextContent

from ..config import HTTP_TIMEOUT


def _format_json(data: Any) -> str:
    """Format JSON data as an indented, human-readable string."""
    return json.dumps(data, indent=2, default=str)


def success_text(message: str, data: Any = None) -> list[TextContent]:
    """Build a successful tool result.

    Args:
        message: Short human-readable summary of the outcome.
        data: Optional JSON-serializable payload to append.

    Returns:
        A single-element list with a TextContent result.
    """
    if data is None:
        text = message
    else:
        text = f"{message}\n{_format_json(data)}"
    return [TextContent(type="text", text=text)]


def error_text(message: str) -> list[TextContent]:
    """Build an error tool result."""
    return [TextContent(type="text", text=f"Error: {message}")]


async def request(
    method: str,
    url: str,
    *,
    json_body: Any = None,
    params: dict[str, Any] | None = None,
) -> tuple[Any | None, str | None]:
    """Perform an HTTP request against a backend microservice.

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE).
        url: Full URL to call.
        json_body: Optional JSON request body.
        params: Optional query parameters.

    Returns:
        A tuple of (parsed_json_or_None, error_message_or_None). On success the
        error message is None; on failure the payload is None and the error
        message describes what went wrong.
    """
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.request(method, url, json=json_body, params=params)
        response.raise_for_status()
    except httpx.ConnectError:
        return None, f"Could not connect to service at {url}. Is the microservice running?"
    except httpx.TimeoutException:
        return None, f"Request to {url} timed out after {HTTP_TIMEOUT}s."
    except httpx.HTTPStatusError as exc:
        body = exc.response.text
        return None, f"Service returned HTTP {exc.response.status_code} for {method} {url}: {body}"
    except httpx.HTTPError as exc:
        return None, f"HTTP error calling {method} {url}: {exc}"

    if response.status_code == 204 or not response.content:
        return {}, None
    try:
        return response.json(), None
    except json.JSONDecodeError:
        return {"raw": response.text}, None
