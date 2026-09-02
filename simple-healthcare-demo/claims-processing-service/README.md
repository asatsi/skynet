# Claims Processing Service

A Spring Boot microservice for managing healthcare insurance claims. Handles the full claim lifecycle from submission through review, approval/rejection, and payment.

## Overview

The Claims Processing Service provides REST APIs for creating, reading, updating, and deleting insurance claims. It supports querying claims by patient or status, and includes a dedicated endpoint for transitioning claims through the processing workflow.

## Technology Stack

- **Java 17**
- **Spring Boot 3.2.0**
- **Spring Data JPA** - Data persistence
- **Spring Validation** - Request validation
- **H2 Database** - In-memory database
- **Maven** - Build tool

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

The service starts on **port 8082**.

## H2 Console

The H2 in-memory database console is available at:

```
http://localhost:8082/h2-console
```

Connection settings:
- **JDBC URL:** `jdbc:h2:mem:claimsdb`
- **Username:** `sa`
- **Password:** (leave empty)

## API Endpoints

### Base URL

```
http://localhost:8082/api/claims
```

### Claims CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/claims` | Get all claims |
| GET | `/api/claims/{id}` | Get claim by ID |
| GET | `/api/claims/claim-number/{claimNumber}` | Get claim by claim number |
| POST | `/api/claims` | Create a new claim |
| PUT | `/api/claims/{id}` | Update an existing claim |
| DELETE | `/api/claims/{id}` | Delete a claim |

### Claim Queries

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/claims/patient/{patientId}` | Get all claims for a patient |
| GET | `/api/claims/status/{status}` | Get all claims by status |

### Claim Status Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| PATCH | `/api/claims/{id}/status` | Update claim status |

### Claim Status Values

- `SUBMITTED` - Initial state when a claim is filed
- `UNDER_REVIEW` - Claim is being reviewed
- `APPROVED` - Claim has been approved
- `REJECTED` - Claim has been rejected
- `PAID` - Claim has been paid out

## Example Requests

### Create a Claim

```bash
curl -X POST http://localhost:8082/api/claims \
  -H "Content-Type: application/json" \
  -d '{
    "claimNumber": "CLM-2024-001",
    "patientId": 1001,
    "policyNumber": "POL-2024-5678",
    "claimDate": "2024-01-15",
    "claimAmount": 2500.00,
    "status": "SUBMITTED",
    "description": "Emergency room visit for severe abdominal pain."
  }'
```

### Get All Claims

```bash
curl http://localhost:8082/api/claims
```

### Get Claim by ID

```bash
curl http://localhost:8082/api/claims/1
```

### Get Claims by Patient

```bash
curl http://localhost:8082/api/claims/patient/1001
```

### Get Claims by Status

```bash
curl http://localhost:8082/api/claims/status/SUBMITTED
```

### Update Claim Status

```bash
curl -X PATCH http://localhost:8082/api/claims/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "APPROVED"}'
```

### Update a Claim

```bash
curl -X PUT http://localhost:8082/api/claims/1 \
  -H "Content-Type: application/json" \
  -d '{
    "claimNumber": "CLM-2024-001",
    "patientId": 1001,
    "policyNumber": "POL-2024-5678",
    "claimDate": "2024-01-15",
    "claimAmount": 2750.00,
    "status": "UNDER_REVIEW",
    "description": "Updated claim with additional charges."
  }'
```

### Delete a Claim

```bash
curl -X DELETE http://localhost:8082/api/claims/1
```

## Postman Collection

A Postman collection with all endpoints is available at:

```
postman/Claims-Processing-Service-API.postman_collection.json
```

Import it into Postman and set the `baseUrl` variable to `http://localhost:8082`.

## Project Structure

```
claims-processing-service/
├── src/main/java/com/healthcare/claimsprocessing/
│   ├── ClaimsProcessingApplication.java
│   ├── controller/
│   │   └── ClaimController.java
│   ├── model/
│   │   ├── Claim.java
│   │   └── ClaimStatus.java
│   ├── repository/
│   │   └── ClaimRepository.java
│   ├── service/
│   │   └── ClaimService.java
│   └── exception/
│       ├── ResourceNotFoundException.java
│       ├── DuplicateResourceException.java
│       ├── ErrorResponse.java
│       └── GlobalExceptionHandler.java
├── src/main/resources/
│   └── application.properties
├── src/test/java/com/healthcare/claimsprocessing/
│   └── ClaimsProcessingApplicationTests.java
├── postman/
│   └── Claims-Processing-Service-API.postman_collection.json
├── pom.xml
├── README.md
└── .gitignore
```
