# Auto-generated MCP Server by mcp_accelerator
import os
import json
import asyncio
import httpx
from typing import Dict, Any, Optional, List
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Scheduling Domain MCP Server")

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

@mcp.tool(description="List all appointments")
async def list_appointments() -> str:
    url = f"http://localhost:8084/api/appointments"
    params = None
    json_body = None
    return await _make_api_request(url, method="GET", json_data=json_body, params=params)

@mcp.tool(description="Book an appointment")
async def book_appointment(patientId: Optional[int] = None, providerId: Optional[int] = None, appointmentDateTime: Optional[str] = None, reason: Optional[str] = None) -> str:
    url = f"http://localhost:8084/api/appointments"
    params = None
    json_body = {}
    if patientId is not None: json_body['patientId'] = patientId
    if providerId is not None: json_body['providerId'] = providerId
    if appointmentDateTime is not None: json_body['appointmentDateTime'] = appointmentDateTime
    if reason is not None: json_body['reason'] = reason
    return await _make_api_request(url, method="POST", json_data=json_body, params=params)

@mcp.tool(description="Get appointment by ID")
async def get_appointment_by_id(id: Any) -> str:
    url = f"http://localhost:8084/api/appointments/{id}"
    params = None
    json_body = None
    return await _make_api_request(url, method="GET", json_data=json_body, params=params)

@mcp.tool(description="Update appointment")
async def update_appointment(id: Any, appointmentDateTime: Optional[str] = None, reason: Optional[str] = None, status: Optional[str] = None) -> str:
    url = f"http://localhost:8084/api/appointments/{id}"
    params = None
    json_body = {}
    if appointmentDateTime is not None: json_body['appointmentDateTime'] = appointmentDateTime
    if reason is not None: json_body['reason'] = reason
    if status is not None: json_body['status'] = status
    return await _make_api_request(url, method="PUT", json_data=json_body, params=params)

@mcp.tool(description="Cancel appointment")
async def cancel_appointment(id: Any) -> str:
    url = f"http://localhost:8084/api/appointments/{id}/cancel"
    params = None
    json_body = None
    return await _make_api_request(url, method="PUT", json_data=json_body, params=params)

@mcp.tool(description="Get appointments for a patient")
async def get_appointments_by_patient(patientId: Any) -> str:
    url = f"http://localhost:8084/api/appointments/patient/{patientId}"
    params = None
    json_body = None
    return await _make_api_request(url, method="GET", json_data=json_body, params=params)

@mcp.tool(description="Get appointments for a provider")
async def get_appointments_by_provider(providerId: Any) -> str:
    url = f"http://localhost:8084/api/appointments/provider/{providerId}"
    params = None
    json_body = None
    return await _make_api_request(url, method="GET", json_data=json_body, params=params)

@mcp.tool(description="List all providers")
async def list_providers() -> str:
    url = f"http://localhost:8084/api/providers"
    params = None
    json_body = None
    return await _make_api_request(url, method="GET", json_data=json_body, params=params)

@mcp.tool(description="Create a new provider")
async def create_provider(firstName: Optional[str] = None, lastName: Optional[str] = None, specialization: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None) -> str:
    url = f"http://localhost:8084/api/providers"
    params = None
    json_body = {}
    if firstName is not None: json_body['firstName'] = firstName
    if lastName is not None: json_body['lastName'] = lastName
    if specialization is not None: json_body['specialization'] = specialization
    if email is not None: json_body['email'] = email
    if phone is not None: json_body['phone'] = phone
    return await _make_api_request(url, method="POST", json_data=json_body, params=params)
