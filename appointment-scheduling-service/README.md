# Appointment Scheduling Service

A Spring Boot microservice for managing healthcare appointments and providers. Part of the healthcare platform microservices suite.

## Overview

The Appointment Scheduling Service provides REST APIs for:
- Managing appointments (schedule, confirm, cancel, complete, mark no-show)
- Managing healthcare providers (doctors, specialists)
- Querying appointments by patient, provider, status, or date

## Technology Stack

- Java 17
- Spring Boot 3.2.0
- Spring Data JPA
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

The service starts on **port 8084**.

## H2 Console

The H2 database console is available at:

- URL: `http://localhost:8084/h2-console`
- JDBC URL: `jdbc:h2:mem:appointmentdb`
- Username: `sa`
- Password: *(empty)*

## API Endpoints

### Appointments (`/api/appointments`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/appointments` | Get all appointments |
| GET | `/api/appointments/{id}` | Get appointment by ID |
| POST | `/api/appointments` | Create a new appointment |
| PUT | `/api/appointments/{id}` | Update an appointment |
| PATCH | `/api/appointments/{id}/status` | Update appointment status |
| DELETE | `/api/appointments/{id}` | Delete an appointment |
| GET | `/api/appointments/patient/{patientId}` | Get appointments by patient |
| GET | `/api/appointments/provider/{providerId}` | Get appointments by provider |
| GET | `/api/appointments/status/{status}` | Get appointments by status |
| GET | `/api/appointments/date/{date}` | Get appointments by date (YYYY-MM-DD) |

### Providers (`/api/providers`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/providers` | Get all providers |
| GET | `/api/providers/{id}` | Get provider by ID |
| POST | `/api/providers` | Create a new provider |
| PUT | `/api/providers/{id}` | Update a provider |
| DELETE | `/api/providers/{id}` | Delete a provider |
| GET | `/api/providers/specialization/{specialization}` | Get providers by specialization |

### Appointment Status Values

`SCHEDULED`, `CONFIRMED`, `CANCELLED`, `COMPLETED`, `NO_SHOW`

## Example Requests

### Create a Provider

```bash
curl -X POST http://localhost:8084/api/providers \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Sarah",
    "lastName": "Johnson",
    "specialization": "Cardiology",
    "email": "sarah.johnson@healthcare.com",
    "phone": "+1-555-0142"
  }'
```

### Create an Appointment

```bash
curl -X POST http://localhost:8084/api/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "patientId": 1,
    "providerId": 1,
    "appointmentDate": "2024-06-15",
    "appointmentTime": "10:30:00",
    "duration": 30,
    "status": "SCHEDULED",
    "reason": "Annual physical examination",
    "notes": "Patient requested morning appointment"
  }'
```

### Update Appointment Status

```bash
curl -X PATCH http://localhost:8084/api/appointments/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "CONFIRMED"}'
```

## Postman Collection

A ready-to-use Postman collection is available at `postman/Appointment-Scheduling-Service-API.postman_collection.json`. Import it into Postman and set the `baseUrl` variable (default: `http://localhost:8084`).

## Error Handling

The service returns structured error responses:

- `400 Bad Request` — validation failures or invalid input
- `404 Not Found` — resource not found
- `500 Internal Server Error` — unexpected errors

Example error response:

```json
{
  "timestamp": "2024-05-20T10:15:30",
  "status": 404,
  "error": "Not Found",
  "message": "Appointment not found with id: '99'",
  "path": "/api/appointments/99"
}
```
