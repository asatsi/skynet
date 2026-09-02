# Scheduling Domain MCP Server

Auto-generated MCP (Model Context Protocol) domain server.

## Microservices Included

- **appointment-scheduling-service** (Port 8084): /Users/skpagare/my-lab/skynet/appointment-scheduling-service

## Exposed MCP Tools (9)

- `list_appointments`: List all appointments (`GET /api/appointments`)
- `book_appointment`: Book an appointment (`POST /api/appointments`)
- `get_appointment_by_id`: Get appointment by ID (`GET /api/appointments/{id}`)
- `update_appointment`: Update appointment (`PUT /api/appointments/{id}`)
- `cancel_appointment`: Cancel appointment (`PUT /api/appointments/{id}/cancel`)
- `get_appointments_by_patient`: Get appointments for a patient (`GET /api/appointments/patient/{patientId}`)
- `get_appointments_by_provider`: Get appointments for a provider (`GET /api/appointments/provider/{providerId}`)
- `list_providers`: List all providers (`GET /api/providers`)
- `create_provider`: Create a new provider (`POST /api/providers`)

## How to Run

Run with `uv`:

```bash
cd scheduling_domain_mcp
uv run python run.py
```
