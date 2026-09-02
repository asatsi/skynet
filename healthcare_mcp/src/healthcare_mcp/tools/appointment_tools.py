"""MCP tools for the Appointment Scheduling Service (http://localhost:8084).

Covers appointments and providers.
"""

from typing import Any

from mcp.types import TextContent, Tool

from ..config import APPOINTMENT_SERVICE_URL
from .http_client import error_text, request, success_text

APPOINTMENTS_BASE = f"{APPOINTMENT_SERVICE_URL}/api/appointments"
PROVIDERS_BASE = f"{APPOINTMENT_SERVICE_URL}/api/providers"

APPOINTMENT_STATUSES = ["SCHEDULED", "CONFIRMED", "CANCELLED", "COMPLETED", "NO_SHOW"]


async def book_appointment(arguments: dict[str, Any]) -> list[TextContent]:
    """Book a new appointment."""
    data, error = await request("POST", APPOINTMENTS_BASE, json_body=arguments)
    if error:
        return error_text(error)
    return success_text("Appointment booked successfully:", data)


async def get_appointment(arguments: dict[str, Any]) -> list[TextContent]:
    """Get an appointment by ID."""
    appointment_id = arguments["appointmentId"]
    data, error = await request("GET", f"{APPOINTMENTS_BASE}/{appointment_id}")
    if error:
        return error_text(error)
    return success_text(f"Appointment {appointment_id}:", data)


async def list_appointments(arguments: dict[str, Any]) -> list[TextContent]:
    """List all appointments."""
    data, error = await request("GET", APPOINTMENTS_BASE)
    if error:
        return error_text(error)
    return success_text(f"Found {len(data)} appointment(s):", data)


async def update_appointment(arguments: dict[str, Any]) -> list[TextContent]:
    """Update an existing appointment."""
    arguments = dict(arguments)
    appointment_id = arguments.pop("appointmentId")
    data, error = await request(
        "PUT", f"{APPOINTMENTS_BASE}/{appointment_id}", json_body=arguments
    )
    if error:
        return error_text(error)
    return success_text(f"Appointment {appointment_id} updated successfully:", data)


async def cancel_appointment(arguments: dict[str, Any]) -> list[TextContent]:
    """Cancel an appointment by setting its status to CANCELLED."""
    appointment_id = arguments["appointmentId"]
    data, error = await request(
        "PATCH", f"{APPOINTMENTS_BASE}/{appointment_id}/status", json_body={"status": "CANCELLED"}
    )
    if error:
        return error_text(error)
    return success_text(f"Appointment {appointment_id} cancelled:", data)


async def get_patient_appointments(arguments: dict[str, Any]) -> list[TextContent]:
    """Get all appointments for a patient."""
    patient_id = arguments["patientId"]
    data, error = await request("GET", f"{APPOINTMENTS_BASE}/patient/{patient_id}")
    if error:
        return error_text(error)
    return success_text(f"Found {len(data)} appointment(s) for patient {patient_id}:", data)


async def get_provider_appointments(arguments: dict[str, Any]) -> list[TextContent]:
    """Get all appointments for a provider."""
    provider_id = arguments["providerId"]
    data, error = await request("GET", f"{APPOINTMENTS_BASE}/provider/{provider_id}")
    if error:
        return error_text(error)
    return success_text(f"Found {len(data)} appointment(s) for provider {provider_id}:", data)


async def create_provider(arguments: dict[str, Any]) -> list[TextContent]:
    """Create a new healthcare provider."""
    data, error = await request("POST", PROVIDERS_BASE, json_body=arguments)
    if error:
        return error_text(error)
    return success_text("Provider created successfully:", data)


async def list_providers(arguments: dict[str, Any]) -> list[TextContent]:
    """List all healthcare providers."""
    data, error = await request("GET", PROVIDERS_BASE)
    if error:
        return error_text(error)
    return success_text(f"Found {len(data)} provider(s):", data)


_APPOINTMENT_PROPERTIES = {
    "patientId": {"type": "integer", "description": "Patient ID"},
    "providerId": {"type": "integer", "description": "Provider ID"},
    "appointmentDate": {"type": "string", "description": "Appointment date (YYYY-MM-DD)"},
    "appointmentTime": {"type": "string", "description": "Appointment time (HH:MM or HH:MM:SS)"},
    "duration": {"type": "integer", "description": "Duration in minutes (>= 1)"},
    "status": {
        "type": "string",
        "description": "Appointment status",
        "enum": APPOINTMENT_STATUSES,
    },
    "reason": {"type": "string", "description": "Reason for the appointment"},
    "notes": {"type": "string", "description": "Additional notes"},
}

TOOLS: list[Tool] = [
    Tool(
        name="book_appointment",
        description="Book a new appointment for a patient with a provider",
        inputSchema={
            "type": "object",
            "properties": _APPOINTMENT_PROPERTIES,
            "required": ["patientId", "providerId", "appointmentDate", "appointmentTime", "duration"],
        },
    ),
    Tool(
        name="get_appointment",
        description="Get an appointment by ID",
        inputSchema={
            "type": "object",
            "properties": {
                "appointmentId": {"type": "integer", "description": "Appointment ID"},
            },
            "required": ["appointmentId"],
        },
    ),
    Tool(
        name="list_appointments",
        description="List all appointments",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="update_appointment",
        description="Update an existing appointment",
        inputSchema={
            "type": "object",
            "properties": {
                "appointmentId": {"type": "integer", "description": "Appointment ID"},
                **_APPOINTMENT_PROPERTIES,
            },
            "required": ["appointmentId", "patientId", "providerId", "appointmentDate", "appointmentTime", "duration"],
        },
    ),
    Tool(
        name="cancel_appointment",
        description="Cancel an appointment",
        inputSchema={
            "type": "object",
            "properties": {
                "appointmentId": {"type": "integer", "description": "Appointment ID"},
            },
            "required": ["appointmentId"],
        },
    ),
    Tool(
        name="get_patient_appointments",
        description="Get all appointments for a patient",
        inputSchema={
            "type": "object",
            "properties": {
                "patientId": {"type": "integer", "description": "Patient ID"},
            },
            "required": ["patientId"],
        },
    ),
    Tool(
        name="get_provider_appointments",
        description="Get all appointments for a provider",
        inputSchema={
            "type": "object",
            "properties": {
                "providerId": {"type": "integer", "description": "Provider ID"},
            },
            "required": ["providerId"],
        },
    ),
    Tool(
        name="create_provider",
        description="Create a new healthcare provider",
        inputSchema={
            "type": "object",
            "properties": {
                "firstName": {"type": "string", "description": "Provider's first name"},
                "lastName": {"type": "string", "description": "Provider's last name"},
                "specialization": {"type": "string", "description": "Medical specialization"},
                "email": {"type": "string", "description": "Email address"},
                "phone": {"type": "string", "description": "Phone number"},
            },
            "required": ["firstName", "lastName", "specialization", "email"],
        },
    ),
    Tool(
        name="list_providers",
        description="List all healthcare providers",
        inputSchema={"type": "object", "properties": {}},
    ),
]

HANDLERS = {
    "book_appointment": book_appointment,
    "get_appointment": get_appointment,
    "list_appointments": list_appointments,
    "update_appointment": update_appointment,
    "cancel_appointment": cancel_appointment,
    "get_patient_appointments": get_patient_appointments,
    "get_provider_appointments": get_provider_appointments,
    "create_provider": create_provider,
    "list_providers": list_providers,
}
