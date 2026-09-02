# EHR Service

Electronic Health Records (EHR) microservice for the healthcare platform. Manages lab results, diagnoses, and treatment plans, and provides an aggregated patient summary view.

## Overview

- **Service name:** ehr-service
- **Port:** 8083
- **Base path:** `/api/ehr`
- **Database:** H2 in-memory (`ehrdb`)

## Technology Stack

- Java 17
- Spring Boot 3.2.0
- Spring Data JPA
- Spring Validation
- H2 in-memory database
- Maven

## Prerequisites

- Java 17 or higher
- Maven 3.6+

## Build

```bash
mvn clean install
```

## Run

```bash
mvn spring-boot:run
```

The service starts on `http://localhost:8083`.

## H2 Console

- URL: `http://localhost:8083/h2-console`
- JDBC URL: `jdbc:h2:mem:ehrdb`
- Username: `sa`
- Password: *(empty)*

## API Endpoints

### Lab Results

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ehr/lab-results` | Get all lab results |
| GET | `/api/ehr/lab-results/{id}` | Get lab result by ID |
| GET | `/api/ehr/lab-results/patient/{patientId}` | Get lab results for a patient |
| POST | `/api/ehr/lab-results` | Create a lab result |

### Diagnoses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ehr/diagnoses` | Get all diagnoses |
| GET | `/api/ehr/diagnoses/{id}` | Get diagnosis by ID |
| GET | `/api/ehr/diagnoses/patient/{patientId}` | Get diagnoses for a patient |
| POST | `/api/ehr/diagnoses` | Create a diagnosis |

### Treatment Plans

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ehr/treatment-plans` | Get all treatment plans |
| GET | `/api/ehr/treatment-plans/{id}` | Get treatment plan by ID |
| GET | `/api/ehr/treatment-plans/patient/{patientId}` | Get treatment plans for a patient |
| POST | `/api/ehr/treatment-plans` | Create a treatment plan |

### Patient Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ehr/patient/{patientId}/summary` | Aggregated EHR summary (lab results, diagnoses, treatment plans) |

## Example Requests

### Create a Lab Result

```bash
curl -X POST http://localhost:8083/api/ehr/lab-results \
  -H "Content-Type: application/json" \
  -d '{
    "patientId": 1001,
    "testName": "Complete Blood Count",
    "testCode": "CBC-001",
    "testDate": "2024-05-10",
    "resultValue": "5.4",
    "unit": "million cells/mcL",
    "referenceRange": "4.5-5.5",
    "status": "COMPLETED",
    "orderedBy": "Dr. Sarah Johnson",
    "notes": "Fasting sample collected at 8 AM"
  }'
```

### Create a Diagnosis

```bash
curl -X POST http://localhost:8083/api/ehr/diagnoses \
  -H "Content-Type: application/json" \
  -d '{
    "patientId": 1001,
    "diagnosisCode": "E11.9",
    "diagnosisName": "Type 2 Diabetes Mellitus",
    "description": "Type 2 diabetes without complications",
    "diagnosisDate": "2024-05-10",
    "severity": "MODERATE",
    "status": "ACTIVE",
    "diagnosedBy": "Dr. Sarah Johnson"
  }'
```

### Create a Treatment Plan

```bash
curl -X POST http://localhost:8083/api/ehr/treatment-plans \
  -H "Content-Type: application/json" \
  -d '{
    "patientId": 1001,
    "planName": "Diabetes Management Plan",
    "description": "Comprehensive plan for managing Type 2 diabetes",
    "startDate": "2024-05-15",
    "endDate": "2024-11-15",
    "status": "ACTIVE",
    "prescribedBy": "Dr. Sarah Johnson",
    "medications": "Metformin 500mg twice daily",
    "instructions": "Monitor blood glucose twice daily. Follow low-carb diet. Exercise 30 minutes daily."
  }'
```

### Get Patient Summary

```bash
curl http://localhost:8083/api/ehr/patient/1001/summary
```

## Postman Collection

Import `postman/EHR-Service-API.postman_collection.json` into Postman. The collection uses a `{{baseUrl}}` variable (default `http://localhost:8083`).

## Error Handling

- `404 Not Found` — resource not found (e.g., unknown lab result ID)
- `400 Bad Request` — validation failure, with per-field details in the response body
- `500 Internal Server Error` — unexpected errors

All errors return a consistent JSON body with `timestamp`, `status`, `error`, `message`, and `path`.
