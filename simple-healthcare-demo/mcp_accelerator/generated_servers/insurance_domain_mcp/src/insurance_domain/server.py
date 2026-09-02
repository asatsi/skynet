# Auto-generated MCP Server by mcp_accelerator
import os
import json
import asyncio
import httpx
from typing import Dict, Any, Optional, List
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Insurance Domain MCP Server")

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

@mcp.tool(description="List all insurance claims")
async def list_claims() -> str:
    url = f"http://localhost:8082/api/claims"
    params = None
    json_body = None
    return await _make_api_request(url, method="GET", json_data=json_body, params=params)

@mcp.tool(description="Submit a new claim")
async def submit_claim(patientId: Optional[int] = None, providerName: Optional[str] = None, claimAmount: Optional[float] = None, serviceDate: Optional[str] = None, diagnosisCode: Optional[str] = None, description: Optional[str] = None) -> str:
    url = f"http://localhost:8082/api/claims"
    params = None
    json_body = {}
    if patientId is not None: json_body['patientId'] = patientId
    if providerName is not None: json_body['providerName'] = providerName
    if claimAmount is not None: json_body['claimAmount'] = claimAmount
    if serviceDate is not None: json_body['serviceDate'] = serviceDate
    if diagnosisCode is not None: json_body['diagnosisCode'] = diagnosisCode
    if description is not None: json_body['description'] = description
    return await _make_api_request(url, method="POST", json_data=json_body, params=params)

@mcp.tool(description="Get claim by ID")
async def get_claim_by_id(id: Any) -> str:
    url = f"http://localhost:8082/api/claims/{id}"
    params = None
    json_body = None
    return await _make_api_request(url, method="GET", json_data=json_body, params=params)

@mcp.tool(description="Update claim status")
async def update_claim_status(id: Any, status: Optional[str] = None, remarks: Optional[str] = None) -> str:
    url = f"http://localhost:8082/api/claims/{id}/status"
    params = None
    json_body = {}
    if status is not None: json_body['status'] = status
    if remarks is not None: json_body['remarks'] = remarks
    return await _make_api_request(url, method="PUT", json_data=json_body, params=params)

@mcp.tool(description="Get claims by patient ID")
async def get_claims_by_patient_id(patientId: Any) -> str:
    url = f"http://localhost:8082/api/claims/patient/{patientId}"
    params = None
    json_body = None
    return await _make_api_request(url, method="GET", json_data=json_body, params=params)

@mcp.tool(description="Get claims by status")
async def get_claims_by_status(status: Any) -> str:
    url = f"http://localhost:8082/api/claims/status/{status}"
    params = None
    json_body = None
    return await _make_api_request(url, method="GET", json_data=json_body, params=params)
