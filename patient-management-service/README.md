# Patient Management Service

A Spring Boot microservice for managing patients and their medical records, part of the Healthcare Microservices Platform.

## Overview

The Patient Management Service provides REST APIs to:

- Register, retrieve, update, and delete patients
- Record and retrieve medical records for a patient

Patient data is stored in an in-memory H2 database, so all data is reset on every restart.

## Technology Stack

- Java 17
- Spring Boot 3.2.0
- Spring Data JPA
- Spring Validation
- H2 in-memory database
- Maven

## Prerequisites

- Java 17 or higher
- Maven 3.6 or higher

## Build

```bash
mvn clean install
```

## Run

```bash
mvn spring-boot:run
```

The service starts on **port 8081**.

## H2 Console

The H2 database console is available at:

- URL: `http://localhost:8081/h2-console`
- JDBC URL: `jdbc:h2:mem:patientdb`
- Username: `sa`
- Password: *(leave empty)*

## API Endpoints

Base path: `/api/patients`

### Patients

| Method | Endpoint              | Description            | Success Status |
|--------|-----------------------|------------------------|----------------|
| GET    | `/api/patients`       | Get all patients       | 200 OK         |
| GET    | `/api/patients/{id}`  | Get a patient by ID    | 200 OK         |
| POST   | `/api/patients`       | Create a new patient   | 201 Created    |
| PUT    | `/api/patients/{id}`  | Update a patient       | 200 OK         |
| DELETE | `/api/patients/{id}`  | Delete a patient       | 204 No Content |

### Medical Records

| Method | Endpoint                                        | Description                          | Success Status |
|--------|-------------------------------------------------|--------------------------------------|----------------|
| GET    | `/api/patients/{patientId}/medical-records`     | Get all medical records for a patient | 200 OK         |
| POST   | `/api/patients/{patientId}/medical-records`     | Add a medical record to a patient    | 201 Created    |

## Example Requests

### Create a patient

```bash
curl -X POST http://localhost:8081/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "dateOfBirth": "1985-03-15",
    "email": "john.doe@example.com",
    "phone": "+1-555-123-4567",
    "address": "123 Main Street, Springfield, IL 62701",
    "ssn": "123-45-6789",
    "bloodType": "O+",
    "allergies": "Penicillin, Peanuts"
  }'
```

### Get all patients

```bash
curl http://localhost:8081/api/patients
```

### Get a patient by ID

```bash
curl http://localhost:8081/api/patients/1
```

### Update a patient

```bash
curl -X PUT http://localhost:8081/api/patients/1 \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "dateOfBirth": "1985-03-15",
    "email": "john.doe@example.com",
    "phone": "+1-555-987-6543",
    "address": "456 Oak Avenue, Springfield, IL 62702",
    "ssn": "123-45-6789",
    "bloodType": "O+",
    "allergies": "Penicillin, Peanuts, Dust"
  }'
```

### Delete a patient

```bash
curl -X DELETE http://localhost:8081/api/patients/1
```

### Add a medical record to a patient

```bash
curl -X POST http://localhost:8081/api/patients/1/medical-records \
  -H "Content-Type: application/json" \
  -d '{
    "recordDate": "2024-05-10",
    "diagnosis": "Type 2 Diabetes Mellitus",
    "treatment": "Metformin 500mg twice daily, dietary counseling",
    "notes": "Patient advised on blood glucose monitoring. Follow-up in 3 months.",
    "physician": "Dr. Sarah Johnson"
  }'
```

### Get medical records for a patient

```bash
curl http://localhost:8081/api/patients/1/medical-records
```

## Validation Rules

### Patient

- `firstName`, `lastName`: required, max 50 characters
- `dateOfBirth`: required, must be in the past (`YYYY-MM-DD`)
- `email`: required, must be a valid email address, unique
- `phone`: required, valid phone format
- `ssn`: required, format `XXX-XX-XXXX`, unique
- `bloodType`: optional, one of `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`
- `address`: optional, max 255 characters
- `allergies`: optional, max 500 characters

### Medical Record

- `recordDate`: required, cannot be in the future (`YYYY-MM-DD`)
- `diagnosis`: required, max 500 characters
- `treatment`: optional, max 1000 characters
- `notes`: optional, max 2000 characters
- `physician`: required, max 100 characters

## Error Responses

Errors return a consistent JSON body:

```json
{
  "timestamp": "2024-05-10T14:30:00",
  "status": 404,
  "error": "Not Found",
  "message": "Patient not found with id: '99'",
  "path": "uri=/api/patients/99"
}
```

Validation failures return `400 Bad Request` with a `fieldErrors` map; duplicate email/SSN returns `409 Conflict`.

## Postman Collection

A ready-to-use Postman collection is included at `postman/Patient-Management-Service-API.postman_collection.json`. Import it into Postman and set the `baseUrl` collection variable (default: `http://localhost:8081`).

## Testing

```bash
mvn test
```
