"""MCP tools for the Claims Processing Service (http://localhost:8082)."""

from typing import Any

from mcp.types import TextContent, Tool

from ..config import CLAIMS_SERVICE_URL
from .http_client import error_text, request, success_text

CLAIMS_BASE = f"{CLAIMS_SERVICE_URL}/api/claims"

CLAIM_STATUSES = ["SUBMITTED", "UNDER_REVIEW", "APPROVED", "REJECTED", "PAID"]


async def submit_claim(arguments: dict[str, Any]) -> list[TextContent]:
    """Submit a new insurance claim."""
    data, error = await request("POST", CLAIMS_BASE, json_body=arguments)
    if error:
        return error_text(error)
    return success_text("Claim submitted successfully:", data)


async def get_claim(arguments: dict[str, Any]) -> list[TextContent]:
    """Get a claim by ID."""
    claim_id = arguments["claimId"]
    data, error = await request("GET", f"{CLAIMS_BASE}/{claim_id}")
    if error:
        return error_text(error)
    return success_text(f"Claim {claim_id}:", data)


async def list_claims(arguments: dict[str, Any]) -> list[TextContent]:
    """List all claims."""
    data, error = await request("GET", CLAIMS_BASE)
    if error:
        return error_text(error)
    return success_text(f"Found {len(data)} claim(s):", data)


async def get_patient_claims(arguments: dict[str, Any]) -> list[TextContent]:
    """Get all claims for a patient."""
    patient_id = arguments["patientId"]
    data, error = await request("GET", f"{CLAIMS_BASE}/patient/{patient_id}")
    if error:
        return error_text(error)
    return success_text(f"Found {len(data)} claim(s) for patient {patient_id}:", data)


async def get_claims_by_status(arguments: dict[str, Any]) -> list[TextContent]:
    """Get claims filtered by status."""
    status = arguments["status"]
    data, error = await request("GET", f"{CLAIMS_BASE}/status/{status}")
    if error:
        return error_text(error)
    return success_text(f"Found {len(data)} claim(s) with status {status}:", data)


async def update_claim_status(arguments: dict[str, Any]) -> list[TextContent]:
    """Update the status of a claim."""
    claim_id = arguments["claimId"]
    status = arguments["status"]
    data, error = await request(
        "PATCH", f"{CLAIMS_BASE}/{claim_id}/status", json_body={"status": status}
    )
    if error:
        return error_text(error)
    return success_text(f"Claim {claim_id} status updated to {status}:", data)


TOOLS: list[Tool] = [
    Tool(
        name="submit_claim",
        description="Submit a new insurance claim",
        inputSchema={
            "type": "object",
            "properties": {
                "claimNumber": {"type": "string", "description": "Unique claim number"},
                "patientId": {"type": "integer", "description": "Patient ID"},
                "policyNumber": {"type": "string", "description": "Insurance policy number"},
                "claimDate": {"type": "string", "description": "Claim date (YYYY-MM-DD)"},
                "claimAmount": {"type": "number", "description": "Claim amount (must be > 0)"},
                "status": {
                    "type": "string",
                    "description": "Initial claim status",
                    "enum": CLAIM_STATUSES,
                },
                "description": {"type": "string", "description": "Claim description"},
            },
            "required": ["claimNumber", "patientId", "policyNumber", "claimDate", "claimAmount", "status"],
        },
    ),
    Tool(
        name="get_claim",
        description="Get a claim by ID",
        inputSchema={
            "type": "object",
            "properties": {
                "claimId": {"type": "integer", "description": "Claim ID"},
            },
            "required": ["claimId"],
        },
    ),
    Tool(
        name="list_claims",
        description="List all insurance claims",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="get_patient_claims",
        description="Get all claims for a specific patient",
        inputSchema={
            "type": "object",
            "properties": {
                "patientId": {"type": "integer", "description": "Patient ID"},
            },
            "required": ["patientId"],
        },
    ),
    Tool(
        name="get_claims_by_status",
        description="Get all claims with a specific status",
        inputSchema={
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Claim status",
                    "enum": CLAIM_STATUSES,
                },
            },
            "required": ["status"],
        },
    ),
    Tool(
        name="update_claim_status",
        description="Update the status of an existing claim",
        inputSchema={
            "type": "object",
            "properties": {
                "claimId": {"type": "integer", "description": "Claim ID"},
                "status": {
                    "type": "string",
                    "description": "New claim status",
                    "enum": CLAIM_STATUSES,
                },
            },
            "required": ["claimId", "status"],
        },
    ),
]

HANDLERS = {
    "submit_claim": submit_claim,
    "get_claim": get_claim,
    "list_claims": list_claims,
    "get_patient_claims": get_patient_claims,
    "get_claims_by_status": get_claims_by_status,
    "update_claim_status": update_claim_status,
}
