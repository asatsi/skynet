"""Configuration for the healthcare MCP server.

Service base URLs can be overridden via environment variables. Each URL is the
base URL of the corresponding Spring Boot microservice (without the /api/...
suffix, which is added by the tool modules).
"""

import os

PATIENT_SERVICE_URL = os.getenv("PATIENT_SERVICE_URL", "http://localhost:8081")
CLAIMS_SERVICE_URL = os.getenv("CLAIMS_SERVICE_URL", "http://localhost:8082")
EHR_SERVICE_URL = os.getenv("EHR_SERVICE_URL", "http://localhost:8083")
APPOINTMENT_SERVICE_URL = os.getenv("APPOINTMENT_SERVICE_URL", "http://localhost:8084")

# MCP server settings
MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))

# HTTP client timeout (seconds) for calls to the backend services
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "30.0"))
