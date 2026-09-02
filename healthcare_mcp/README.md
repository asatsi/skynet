# Healthcare MCP Server

An MCP (Model Context Protocol) server that exposes tools for 4 Spring Boot
healthcare microservices over HTTP/SSE transport, built with the official
[MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk).

## Backend services

| Service | Default URL | Base path |
|---|---|---|
| Patient Management | http://localhost:8081 | `/api/patients` |
| Claims Processing | http://localhost:8082 | `/api/claims` |
| EHR | http://localhost:8083 | `/api/ehr` |
| Appointment Scheduling | http://localhost:8084 | `/api/appointments`, `/api/providers` |

## Prerequisites

- Python 3.11+
- The 4 Spring Boot microservices running (see table above)

## Installation

```bash
cd healthcare_mcp
pip install -e .
# or, with uv:
uv pip install -e .
```

## Running the server

```bash
python run.py
# or
python -m healthcare_mcp.server
# or, after installation, the console script:
healthcare-mcp
```

The server listens on port 8000 by default:

- SSE endpoint: `http://localhost:8000/sse`
- Message endpoint: `http://localhost:8000/messages/`

## Configuration

All settings are environment variables:

| Variable | Default | Description |
|---|---|---|
| `PATIENT_SERVICE_URL` | `http://localhost:8081` | Patient Management Service base URL |
| `CLAIMS_SERVICE_URL` | `http://localhost:8082` | Claims Processing Service base URL |
| `EHR_SERVICE_URL` | `http://localhost:8083` | EHR Service base URL |
| `APPOINTMENT_SERVICE_URL` | `http://localhost:8084` | Appointment Scheduling Service base URL |
| `MCP_SERVER_HOST` | `0.0.0.0` | Host interface for the MCP server |
| `MCP_SERVER_PORT` | `8000` | Port for the MCP server |
| `HTTP_TIMEOUT` | `30.0` | Timeout (seconds) for backend HTTP calls |

## Available tools

### Patient Management

- `create_patient` — Create a new patient
- `get_patient` — Get patient by ID
- `list_patients` — List all patients
- `update_patient` — Update patient
- `delete_patient` — Delete patient
- `get_patient_medical_records` — Get medical records for a patient
- `add_medical_record` — Add a medical record to a patient

### Claims Processing

- `submit_claim` — Submit a new claim
- `get_claim` — Get claim by ID
- `list_claims` — List all claims
- `get_patient_claims` — Get claims by patient ID
- `get_claims_by_status` — Get claims by status (`SUBMITTED`, `UNDER_REVIEW`, `APPROVED`, `REJECTED`, `PAID`)
- `update_claim_status` — Update claim status

### EHR

- `create_lab_result` — Create a lab result
- `get_patient_lab_results` — Get lab results for a patient
- `create_diagnosis` — Create a diagnosis
- `get_patient_diagnoses` — Get diagnoses for a patient
- `create_treatment_plan` — Create a treatment plan
- `get_patient_treatment_plans` — Get treatment plans for a patient
- `get_patient_health_summary` — Get the complete health summary for a patient

### Appointment Scheduling

- `book_appointment` — Book an appointment
- `get_appointment` — Get appointment by ID
- `list_appointments` — List all appointments
- `update_appointment` — Update an appointment
- `cancel_appointment` — Cancel an appointment
- `get_patient_appointments` — Get appointments for a patient
- `get_provider_appointments` — Get appointments for a provider
- `create_provider` — Create a provider
- `list_providers` — List all providers

## Example usage with an MCP client

```python
import asyncio

from mcp import ClientSession
from mcp.client.sse import sse_client


async def main():
    async with sse_client("http://localhost:8000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            for tool in tools.tools:
                print(tool.name)

            # Create a patient
            result = await session.call_tool(
                "create_patient",
                arguments={
                    "firstName": "Jane",
                    "lastName": "Doe",
                    "dateOfBirth": "1990-01-15",
                    "email": "jane.doe@example.com",
                    "phone": "+1-555-0123",
                    "ssn": "123-45-6789",
                    "bloodType": "O+",
                },
            )
            print(result.content[0].text)

            # List patients
            result = await session.call_tool("list_patients", arguments={})
            print(result.content[0].text)


asyncio.run(main())
```

## Project structure

```
healthcare_mcp/
├── src/
│   └── healthcare_mcp/
│       ├── __init__.py
│       ├── server.py          # Main MCP server with SSE transport
│       ├── config.py          # Service URLs configuration
│       └── tools/
│           ├── __init__.py
│           ├── http_client.py      # Shared async HTTP helper with error handling
│           ├── patient_tools.py
│           ├── claims_tools.py
│           ├── ehr_tools.py
│           └── appointment_tools.py
├── pyproject.toml
├── README.md
├── .gitignore
└── run.py
```
