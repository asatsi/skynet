"""MCP tools for the EHR Service (http://localhost:8083).

Covers lab results, diagnoses, treatment plans, and the aggregated patient
health summary.
"""

from typing import Any

from mcp.types import TextContent, Tool

from ..config import EHR_SERVICE_URL
from .http_client import error_text, request, success_text

EHR_BASE = f"{EHR_SERVICE_URL}/api/ehr"


async def create_lab_result(arguments: dict[str, Any]) -> list[TextContent]:
    """Create a lab result for a patient."""
    data, error = await request("POST", f"{EHR_BASE}/lab-results", json_body=arguments)
    if error:
        return error_text(error)
    return success_text("Lab result created successfully:", data)


async def get_patient_lab_results(arguments: dict[str, Any]) -> list[TextContent]:
    """Get all lab results for a patient."""
    patient_id = arguments["patientId"]
    data, error = await request("GET", f"{EHR_BASE}/lab-results/patient/{patient_id}")
    if error:
        return error_text(error)
    return success_text(f"Found {len(data)} lab result(s) for patient {patient_id}:", data)


async def create_diagnosis(arguments: dict[str, Any]) -> list[TextContent]:
    """Create a diagnosis for a patient."""
    data, error = await request("POST", f"{EHR_BASE}/diagnoses", json_body=arguments)
    if error:
        return error_text(error)
    return success_text("Diagnosis created successfully:", data)


async def get_patient_diagnoses(arguments: dict[str, Any]) -> list[TextContent]:
    """Get all diagnoses for a patient."""
    patient_id = arguments["patientId"]
    data, error = await request("GET", f"{EHR_BASE}/diagnoses/patient/{patient_id}")
    if error:
        return error_text(error)
    return success_text(f"Found {len(data)} diagnosis(es) for patient {patient_id}:", data)


async def create_treatment_plan(arguments: dict[str, Any]) -> list[TextContent]:
    """Create a treatment plan for a patient."""
    data, error = await request("POST", f"{EHR_BASE}/treatment-plans", json_body=arguments)
    if error:
        return error_text(error)
    return success_text("Treatment plan created successfully:", data)


async def get_patient_treatment_plans(arguments: dict[str, Any]) -> list[TextContent]:
    """Get all treatment plans for a patient."""
    patient_id = arguments["patientId"]
    data, error = await request("GET", f"{EHR_BASE}/treatment-plans/patient/{patient_id}")
    if error:
        return error_text(error)
    return success_text(f"Found {len(data)} treatment plan(s) for patient {patient_id}:", data)


async def get_patient_health_summary(arguments: dict[str, Any]) -> list[TextContent]:
    """Get the complete health summary for a patient."""
    patient_id = arguments["patientId"]
    data, error = await request("GET", f"{EHR_BASE}/patient/{patient_id}/summary")
    if error:
        return error_text(error)
    return success_text(f"Health summary for patient {patient_id}:", data)


TOOLS: list[Tool] = [
    Tool(
        name="create_lab_result",
        description="Create a lab result for a patient",
        inputSchema={
            "type": "object",
            "properties": {
                "patientId": {"type": "integer", "description": "Patient ID"},
                "testName": {"type": "string", "description": "Name of the test"},
                "testCode": {"type": "string", "description": "Test code (e.g., LOINC)"},
                "testDate": {"type": "string", "description": "Test date (YYYY-MM-DD)"},
                "resultValue": {"type": "string", "description": "Result value"},
                "unit": {"type": "string", "description": "Measurement unit"},
                "referenceRange": {"type": "string", "description": "Reference range"},
                "status": {"type": "string", "description": "Result status (e.g., FINAL, PRELIMINARY)"},
                "orderedBy": {"type": "string", "description": "Ordering physician"},
                "notes": {"type": "string", "description": "Additional notes"},
            },
            "required": ["patientId", "testName", "testCode", "testDate"],
        },
    ),
    Tool(
        name="get_patient_lab_results",
        description="Get all lab results for a patient",
        inputSchema={
            "type": "object",
            "properties": {
                "patientId": {"type": "integer", "description": "Patient ID"},
            },
            "required": ["patientId"],
        },
    ),
    Tool(
        name="create_diagnosis",
        description="Create a diagnosis for a patient",
        inputSchema={
            "type": "object",
            "properties": {
                "patientId": {"type": "integer", "description": "Patient ID"},
                "diagnosisCode": {"type": "string", "description": "Diagnosis code (e.g., ICD-10)"},
                "diagnosisName": {"type": "string", "description": "Diagnosis name"},
                "description": {"type": "string", "description": "Description"},
                "diagnosisDate": {"type": "string", "description": "Diagnosis date (YYYY-MM-DD)"},
                "severity": {"type": "string", "description": "Severity (e.g., MILD, MODERATE, SEVERE)"},
                "status": {"type": "string", "description": "Status (e.g., ACTIVE, RESOLVED)"},
                "diagnosedBy": {"type": "string", "description": "Diagnosing physician"},
            },
            "required": ["patientId", "diagnosisCode", "diagnosisName", "diagnosisDate"],
        },
    ),
    Tool(
        name="get_patient_diagnoses",
        description="Get all diagnoses for a patient",
        inputSchema={
            "type": "object",
            "properties": {
                "patientId": {"type": "integer", "description": "Patient ID"},
            },
            "required": ["patientId"],
        },
    ),
    Tool(
        name="create_treatment_plan",
        description="Create a treatment plan for a patient",
        inputSchema={
            "type": "object",
            "properties": {
                "patientId": {"type": "integer", "description": "Patient ID"},
                "planName": {"type": "string", "description": "Plan name"},
                "description": {"type": "string", "description": "Description"},
                "startDate": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "endDate": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "status": {"type": "string", "description": "Status (e.g., ACTIVE, COMPLETED)"},
                "prescribedBy": {"type": "string", "description": "Prescribing physician"},
                "medications": {"type": "string", "description": "Medications"},
                "instructions": {"type": "string", "description": "Patient instructions"},
            },
            "required": ["patientId", "planName", "startDate"],
        },
    ),
    Tool(
        name="get_patient_treatment_plans",
        description="Get all treatment plans for a patient",
        inputSchema={
            "type": "object",
            "properties": {
                "patientId": {"type": "integer", "description": "Patient ID"},
            },
            "required": ["patientId"],
        },
    ),
    Tool(
        name="get_patient_health_summary",
        description="Get the complete health summary for a patient (diagnoses, lab results, treatment plans)",
        inputSchema={
            "type": "object",
            "properties": {
                "patientId": {"type": "integer", "description": "Patient ID"},
            },
            "required": ["patientId"],
        },
    ),
]

HANDLERS = {
    "create_lab_result": create_lab_result,
    "get_patient_lab_results": get_patient_lab_results,
    "create_diagnosis": create_diagnosis,
    "get_patient_diagnoses": get_patient_diagnoses,
    "create_treatment_plan": create_treatment_plan,
    "get_patient_treatment_plans": get_patient_treatment_plans,
    "get_patient_health_summary": get_patient_health_summary,
}
