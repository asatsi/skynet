# Insurance Domain MCP Server

Auto-generated MCP (Model Context Protocol) domain server.

## Microservices Included

- **claims-processing-service** (Port 8082): /Users/skpagare/my-lab/skynet/claims-processing-service

## Exposed MCP Tools (6)

- `list_claims`: List all insurance claims (`GET /api/claims`)
- `submit_claim`: Submit a new claim (`POST /api/claims`)
- `get_claim_by_id`: Get claim by ID (`GET /api/claims/{id}`)
- `update_claim_status`: Update claim status (`PUT /api/claims/{id}/status`)
- `get_claims_by_patient_id`: Get claims by patient ID (`GET /api/claims/patient/{patientId}`)
- `get_claims_by_status`: Get claims by status (`GET /api/claims/status/{status}`)

## How to Run

Run with `uv`:

```bash
cd insurance_domain_mcp
uv run python run.py
```
