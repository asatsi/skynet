# Healthcare Domain MCP Server

Auto-generated MCP (Model Context Protocol) domain server.

## Microservices Included

- **patient-management-service** (Port 8081): /Users/skpagare/my-lab/skynet/patient-management-service
- **ehr-service** (Port 8083): /Users/skpagare/my-lab/skynet/ehr-service

## Exposed MCP Tools (14)

- `list_patients`: List all patients (`GET /api/patients`)
- `create_patient`: Create a new patient (`POST /api/patients`)
- `get_patient_by_id`: Get patient by ID (`GET /api/patients/{id}`)
- `update_patient`: Update patient details (`PUT /api/patients/{id}`)
- `delete_patient`: Delete patient (`DELETE /api/patients/{id}`)
- `get_medical_records`: Get medical records for patient (`GET /api/patients/{patientId}/medical-records`)
- `add_medical_record`: Add medical record for patient (`POST /api/patients/{patientId}/medical-records`)
- `create_lab_result`: Create a lab result (`POST /api/ehr/lab-results`)
- `get_lab_results_by_patient`: Get lab results for a patient (`GET /api/ehr/lab-results/patient/{patientId}`)
- `create_diagnosis`: Create a diagnosis (`POST /api/ehr/diagnoses`)
- `get_diagnoses_by_patient`: Get diagnoses for a patient (`GET /api/ehr/diagnoses/patient/{patientId}`)
- `create_treatment_plan`: Create a treatment plan (`POST /api/ehr/treatment-plans`)
- `get_treatment_plans_by_patient`: Get treatment plans for a patient (`GET /api/ehr/treatment-plans/patient/{patientId}`)
- `get_health_summary`: Get complete health summary for a patient (`GET /api/ehr/patients/{patientId}/health-summary`)

## How to Run

Run with `uv`:

```bash
cd healthcare_domain_mcp
uv run python run.py
```
