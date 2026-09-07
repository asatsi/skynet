import os

# ── Spring Boot Service URLs ───────────────────────────────────────────────────
CUSTOMER_SERVICE  = os.getenv("CUSTOMER_SERVICE_URL",  "http://localhost:8081")
KYC_SERVICE       = os.getenv("KYC_SERVICE_URL",       "http://localhost:8082")
DOCUMENT_SERVICE  = os.getenv("DOCUMENT_SERVICE_URL",  "http://localhost:8083")
RISK_SERVICE      = os.getenv("RISK_SERVICE_URL",      "http://localhost:8084")
WORKFLOW_SERVICE  = os.getenv("WORKFLOW_SERVICE_URL",  "http://localhost:8085")
LOAN_SERVICE      = os.getenv("LOAN_SERVICE_URL",      "http://localhost:8086")

# ── MCP Server SSE endpoints ───────────────────────────────────────────────────
MCP_CUSTOMER  = os.getenv("MCP_CUSTOMER_URL",  "http://localhost:9001") + "/sse"
MCP_KYC       = os.getenv("MCP_KYC_URL",       "http://localhost:9002") + "/sse"
MCP_DOCUMENT  = os.getenv("MCP_DOCUMENT_URL",  "http://localhost:9003") + "/sse"
MCP_RISK      = os.getenv("MCP_RISK_URL",      "http://localhost:9004") + "/sse"
MCP_WORKFLOW  = os.getenv("MCP_WORKFLOW_URL",  "http://localhost:9005") + "/sse"
MCP_KNOWLEDGE = os.getenv("MCP_KNOWLEDGE_URL", "http://localhost:9006") + "/sse"
MCP_LOAN      = os.getenv("MCP_LOAN_URL",      "http://localhost:9007") + "/sse"
MCP_GATEWAY   = os.getenv("MCP_GATEWAY_URL",   "http://localhost:9000")  # REST gateway (not SSE)

# ── Ollama ─────────────────────────────────────────────────────────────────────
OLLAMA_URL   = os.getenv("OLLAMA_URL",   "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

# ── Agent server ───────────────────────────────────────────────────────────────
AGENT_SERVER_PORT = int(os.getenv("AGENT_SERVER_PORT", "8096"))

# ── Intent → agent mapping ─────────────────────────────────────────────────────
INTENT_AGENT_MAP = {
    "customer_inquiry":   ["customer"],
    "loan_status":        ["loan", "workflow"],
    "kyc_status":         ["kyc", "customer"],
    "document_check":     ["document"],
    "risk_assessment":    ["risk", "customer"],
    "policy_question":    ["knowledge"],
    "approval_request":   ["workflow", "risk"],
    "full_onboarding":    ["customer", "kyc", "document", "risk", "workflow", "loan"],
    "system_health":      ["platform"],
    "general":            ["customer", "loan"],
}
