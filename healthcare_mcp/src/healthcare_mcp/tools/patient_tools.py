"""MCP tools for the Patient Management Service (http://localhost:8081).

Covers patient CRUD plus patient medical records.
"""

from typing import Any

from mcp.types import TextContent, Tool

from ..config import PATIENT_SERVICE_URL
from .http_client import error_text, request, success_text

PATIENTS_BASE = f"{PATIENT_SERVICE_URL}/api/patients"


async def create_patient(arguments: dict[str, Any]) -> list[TextContent]:
    """Create a new patient."""
    data, error = await request("POST", PATIENTS_BASE, json_body=arguments)
    if error:
        return error_text(error)
    return success_text("Patient created successfully:", data)


async def get_patient(arguments: dict[str, Any]) -> list[TextContent]:
    """Get a patient by ID."""
    patient_id = arguments["patientId"]
    data, error = await request("GET", f"{PATIENTS_BASE}/{patient_id}")
    if error:
        return error_text(error)
    return success_text(f"Patient {patient_id}:", data)


async def list_patients(arguments: dict[str, Any]) -> list[TextContent]:
    """List all patients."""
    data, error = await request("GET", PATIENTS_BASE)
    if error:
        return error_text(error)
    return success_text(f"Found {len(data)} patient(s):", data)


async def update_patient(arguments: dict[str, Any]) -> list[TextContent]:
    """Update an existing patient."""
    arguments = dict(arguments)
    patient_id = arguments.pop("patientId")
    data, error = await request("PUT", f"{PATIENTS_BASE}/{patient_id}", json_body=arguments)
    if error:
        return error_text(error)
    return success_text(f"Patient {patient_id} updated successfully:", data)


async def delete_patient(arguments: dict[str, Any]) -> list[TextContent]:
    """Delete a patient by ID."""
    patient_id = arguments["patientId"]
    _, error = await request("DELETE", f"{PATIENTS_BASE}/{patient_id}")
    if error:
        return error_text(error)
    return success_text(f"Patient {patient_id} deleted successfully.")


async def get_patient_medical_records(arguments: dict[str, Any]) -> list[TextContent]:
    """Get all medical records for a patient."""
    patient_id = arguments["patientId"]
    data, error = await request("GET", f"{PATIENTS_BASE}/{patient_id}/medical-records")
    if error:
        return error_text(error)
    return success_text(f"Found {len(data)} medical record(s) for patient {patient_id}:", data)


async def add_medical_record(arguments: dict[str, Any]) -> list[TextContent]:
    """Add a medical record to a patient."""
    arguments = dict(arguments)
    patient_id = arguments.pop("patientId")
    data, error = await request(
        "POST", f"{PATIENTS_BASE}/{patient_id}/medical-records", json_body=arguments
    )
    if error:
        return error_text(error)
    return success_text(f"Medical record added to patient {patient_id}:", data)


_PATIENT_PROPERTIES = {
    "firstName": {"type": "string", "description": "Patient's first name"},
    "lastName": {"type": "string", "description": "Patient's last name"},
    "dateOfBirth": {"type": "string", "description": "Date of birth (YYYY-MM-DD)"},
    "email": {"type": "string", "description": "Email address"},
    "phone": {"type": "string", "description": "Phone number (e.g., +1-555-0123)"},
    "address": {"type": "string", "description": "Street address"},
    "ssn": {"type": "string", "description": "Social Security Number (XXX-XX-XXXX)"},
    "bloodType": {
        "type": "string",
        "description": "Blood type",
        "enum": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    },
    "allergies": {"type": "string", "description": "Known allergies"},
}

TOOLS: list[Tool] = [
    Tool(
        name="create_patient",
        description="Create a new patient in the system",
        inputSchema={
            "type": "object",
            "properties": _PATIENT_PROPERTIES,
            "required": ["firstName", "lastName", "dateOfBirth", "email", "phone", "ssn"],
        },
    ),
    Tool(
        name="get_patient",
        description="Get a patient by ID",
        inputSchema={
            "type": "object",
            "properties": {
                "patientId": {"type": "integer", "description": "Patient ID"},
            },
            "required": ["patientId"],
        },
    ),
    Tool(
        name="list_patients",
        description="List all patients in the system",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="update_patient",
        description="Update an existing patient's details",
        inputSchema={
            "type": "object",
            "properties": {
                "patientId": {"type": "integer", "description": "Patient ID"},
                **_PATIENT_PROPERTIES,
            },
            "required": ["patientId", "firstName", "lastName", "dateOfBirth", "email", "phone", "ssn"],
        },
    ),
    Tool(
        name="delete_patient",
        description="Delete a patient by ID",
        inputSchema={
            "type": "object",
            "properties": {
                "patientId": {"type": "integer", "description": "Patient ID"},
            },
            "required": ["patientId"],
        },
    ),
    Tool(
        name="get_patient_medical_records",
        description="Get all medical records for a patient",
        inputSchema={
            "type": "object",
            "properties": {
                "patientId": {"type": "integer", "description": "Patient ID"},
            },
            "required": ["patientId"],
        },
    ),
    Tool(
        name="add_medical_record",
        description="Add a medical record to a patient",
        inputSchema={
            "type": "object",
            "properties": {
                "patientId": {"type": "integer", "description": "Patient ID"},
                "recordDate": {"type": "string", "description": "Record date (YYYY-MM-DD)"},
                "diagnosis": {"type": "string", "description": "Diagnosis"},
                "treatment": {"type": "string", "description": "Treatment given"},
                "notes": {"type": "string", "description": "Additional notes"},
                "physician": {"type": "string", "description": "Physician name"},
            },
            "required": ["patientId", "recordDate", "diagnosis", "physician"],
        },
    ),
]

HANDLERS = {
    "create_patient": create_patient,
    "get_patient": get_patient,
    "list_patients": list_patients,
    "update_patient": update_patient,
    "delete_patient": delete_patient,
    "get_patient_medical_records": get_patient_medical_records,
    "add_medical_record": add_medical_record,
}
