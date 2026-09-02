# Auto-generated MCP Server by mcp_accelerator
import os
import json
import asyncio
import httpx
from typing import Dict, Any, Optional, List
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Healthcare Domain MCP Server")

# Shared async HTTP Client helper
async def _make_api_request(url: str, method: str = 'GET', json_data: Any = None, params: Any = None) -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.request(method=method, url=url, json=json_data, params=params)
            if resp.status_code in [200, 201]:
                try:
                    return json.dumps(resp.json(), indent=2)
                except Exception:
                    return resp.text
            elif resp.status_code == 204:
                return 'Success (204 No Content)'
            else:
                return f'HTTP Error {resp.status_code}: {resp.text}'
        except Exception as e:
            return f'Request Exception: {str(e)}'

@mcp.tool(description="List all patients")
async def list_patients() -> str:
    url = f"http://localhost:8081/api/patients"
    params = None
    json_body = None
    return await _make_api_request(url, method="GET", json_data=json_body, params=params)

@mcp.tool(description="Create a new patient")
async def create_patient(firstName: Optional[str] = None, lastName: Optional[str] = None, dateOfBirth: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None, address: Optional[str] = None, ssn: Optional[str] = None, bloodType: Optional[str] = None, allergies: Optional[str] = None) -> str:
    url = f"http://localhost:8081/api/patients"
    params = None
    json_body = {}
    if firstName is not None: json_body['firstName'] = firstName
    if lastName is not None: json_body['lastName'] = lastName
    if dateOfBirth is not None: json_body['dateOfBirth'] = dateOfBirth
    if email is not None: json_body['email'] = email
    if phone is not None: json_body['phone'] = phone
    if address is not None: json_body['address'] = address
    if ssn is not None: json_body['ssn'] = ssn
    if bloodType is not None: json_body['bloodType'] = bloodType
    if allergies is not None: json_body['allergies'] = allergies
    return await _make_api_request(url, method="POST", json_data=json_body, params=params)

@mcp.tool(description="Get patient by ID")
async def get_patient_by_id(id: Any) -> str:
    url = f"http://localhost:8081/api/patients/{id}"
    params = None
    json_body = None
    return await _make_api_request(url, method="GET", json_data=json_body, params=params)

@mcp.tool(description="Update patient details")
async def update_patient(id: Any, firstName: Optional[str] = None, lastName: Optional[str] = None, dateOfBirth: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None, address: Optional[str] = None, bloodType: Optional[str] = None, allergies: Optional[str] = None) -> str:
    url = f"http://localhost:8081/api/patients/{id}"
    params = None
    json_body = {}
    if firstName is not None: json_body['firstName'] = firstName
    if lastName is not None: json_body['lastName'] = lastName
    if dateOfBirth is not None: json_body['dateOfBirth'] = dateOfBirth
    if email is not None: json_body['email'] = email
    if phone is not None: json_body['phone'] = phone
    if address is not None: json_body['address'] = address
    if bloodType is not None: json_body['bloodType'] = bloodType
    if allergies is not None: json_body['allergies'] = allergies
    return await _make_api_request(url, method="PUT", json_data=json_body, params=params)

@mcp.tool(description="Delete patient")
async def delete_patient(id: Any) -> str:
    url = f"http://localhost:8081/api/patients/{id}"
    params = None
    json_body = None
    return await _make_api_request(url, method="DELETE", json_data=json_body, params=params)

@mcp.tool(description="Get medical records for patient")
async def get_medical_records(patientId: Any) -> str:
    url = f"http://localhost:8081/api/patients/{patientId}/medical-records"
    params = None
    json_body = None
    return await _make_api_request(url, method="GET", json_data=json_body, params=params)

@mcp.tool(description="Add medical record for patient")
async def add_medical_record(patientId: Any, recordDate: Optional[str] = None, description: Optional[str] = None, doctorName: Optional[str] = None, notes: Optional[str] = None) -> str:
    url = f"http://localhost:8081/api/patients/{patientId}/medical-records"
    params = None
    json_body = {}
    if recordDate is not None: json_body['recordDate'] = recordDate
    if description is not None: json_body['description'] = description
    if doctorName is not None: json_body['doctorName'] = doctorName
    if notes is not None: json_body['notes'] = notes
    return await _make_api_request(url, method="POST", json_data=json_body, params=params)

@mcp.tool(description="Create a lab result")
async def create_lab_result(patientId: Optional[int] = None, testName: Optional[str] = None, testDate: Optional[str] = None, resultValue: Optional[str] = None, unit: Optional[str] = None, referenceRange: Optional[str] = None) -> str:
    url = f"http://localhost:8083/api/ehr/lab-results"
    params = None
    json_body = {}
    if patientId is not None: json_body['patientId'] = patientId
    if testName is not None: json_body['testName'] = testName
    if testDate is not None: json_body['testDate'] = testDate
    if resultValue is not None: json_body['resultValue'] = resultValue
    if unit is not None: json_body['unit'] = unit
    if referenceRange is not None: json_body['referenceRange'] = referenceRange
    return await _make_api_request(url, method="POST", json_data=json_body, params=params)

@mcp.tool(description="Get lab results for a patient")
async def get_lab_results_by_patient(patientId: Any) -> str:
    url = f"http://localhost:8083/api/ehr/lab-results/patient/{patientId}"
    params = None
    json_body = None
    return await _make_api_request(url, method="GET", json_data=json_body, params=params)

@mcp.tool(description="Create a diagnosis")
async def create_diagnosis(patientId: Optional[int] = None, icdCode: Optional[str] = None, description: Optional[str] = None, diagnosisDate: Optional[str] = None, diagnosingDoctor: Optional[str] = None) -> str:
    url = f"http://localhost:8083/api/ehr/diagnoses"
    params = None
    json_body = {}
    if patientId is not None: json_body['patientId'] = patientId
    if icdCode is not None: json_body['icdCode'] = icdCode
    if description is not None: json_body['description'] = description
    if diagnosisDate is not None: json_body['diagnosisDate'] = diagnosisDate
    if diagnosingDoctor is not None: json_body['diagnosingDoctor'] = diagnosingDoctor
    return await _make_api_request(url, method="POST", json_data=json_body, params=params)

@mcp.tool(description="Get diagnoses for a patient")
async def get_diagnoses_by_patient(patientId: Any) -> str:
    url = f"http://localhost:8083/api/ehr/diagnoses/patient/{patientId}"
    params = None
    json_body = None
    return await _make_api_request(url, method="GET", json_data=json_body, params=params)

@mcp.tool(description="Create a treatment plan")
async def create_treatment_plan(patientId: Optional[int] = None, title: Optional[str] = None, startDate: Optional[str] = None, endDate: Optional[str] = None, goals: Optional[str] = None, medications: Optional[str] = None) -> str:
    url = f"http://localhost:8083/api/ehr/treatment-plans"
    params = None
    json_body = {}
    if patientId is not None: json_body['patientId'] = patientId
    if title is not None: json_body['title'] = title
    if startDate is not None: json_body['startDate'] = startDate
    if endDate is not None: json_body['endDate'] = endDate
    if goals is not None: json_body['goals'] = goals
    if medications is not None: json_body['medications'] = medications
    return await _make_api_request(url, method="POST", json_data=json_body, params=params)

@mcp.tool(description="Get treatment plans for a patient")
async def get_treatment_plans_by_patient(patientId: Any) -> str:
    url = f"http://localhost:8083/api/ehr/treatment-plans/patient/{patientId}"
    params = None
    json_body = None
    return await _make_api_request(url, method="GET", json_data=json_body, params=params)

@mcp.tool(description="Get complete health summary for a patient")
async def get_health_summary(patientId: Any) -> str:
    url = f"http://localhost:8083/api/ehr/patients/{patientId}/health-summary"
    params = None
    json_body = None
    return await _make_api_request(url, method="GET", json_data=json_body, params=params)
