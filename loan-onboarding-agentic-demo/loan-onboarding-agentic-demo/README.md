# BFSI Intelligent Loan Onboarding Copilot
### Enterprise Agentic AI POC — LangGraph + MCP + Spring Boot + Mistral

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Loan Officer Browser                      │
│                   http://localhost:8096                      │
└────────────────────────┬────────────────────────────────────┘
                         │ SSE / REST
┌────────────────────────▼────────────────────────────────────┐
│              Agent Server (FastAPI :8096)                    │
│                                                              │
│  ┌──────────────── LangGraph Coordinator ─────────────────┐ │
│  │  classify_intent → select_agents → execute_agents      │ │
│  │       → [HITL interrupt] → synthesize_response         │ │
│  └──────────────────────────────────────────────────────┘ │ │
└──────────────────────────────────────────────────────────────┘
         │          │          │          │          │
    :9001      :9002      :9003      :9004      :9005/9006
 Customer    KYC-MCP   Doc-MCP   Risk-MCP  Workflow  Knowledge
  -MCP                                      -MCP      -MCP
     │          │          │          │          │
  :8081      :8082      :8083      :8084      :8085   :8086
Customer    KYC Svc   Doc Svc   Risk Svc  Workflow  Loan Svc
  Svc                                      Svc
                         H2 (in-memory databases)
```

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Java | 17+ | `java -version` |
| Maven | 3.8+ | `mvn -version` |
| Python | 3.11+ | `python3 --version` |
| Ollama | latest | `ollama serve` |
| Mistral | latest | `ollama pull mistral` |

---

## Quick Start

```bash
# 1. Clone / open the project
cd loan-onboarding-agentic-demo

# 2. Pull Mistral (one-time)
ollama pull mistral

# 3. Start everything
chmod +x start-all.sh
./start-all.sh

# 4. Open the Copilot UI
open http://localhost:8096
```

To stop all services:
```bash
./stop-all.sh
```

---

## Manual Start (per service)

### Spring Boot Services
```bash
# Build all
for SVC in customer-service kyc-service document-service risk-service workflow-service loan-service; do
  (cd services/$SVC && mvn package -DskipTests)
done

# Run each (in separate terminals)
java -jar services/customer-service/target/*.jar   # :8081
java -jar services/kyc-service/target/*.jar        # :8082
java -jar services/document-service/target/*.jar   # :8083
java -jar services/risk-service/target/*.jar       # :8084
java -jar services/workflow-service/target/*.jar   # :8085
java -jar services/loan-service/target/*.jar       # :8086
```

### MCP Servers
```bash
pip install -r mcp-servers/requirements.txt
python mcp-servers/customer_mcp_server.py   # :9001
python mcp-servers/kyc_mcp_server.py        # :9002
python mcp-servers/document_mcp_server.py   # :9003
python mcp-servers/risk_mcp_server.py       # :9004
python mcp-servers/workflow_mcp_server.py   # :9005
python mcp-servers/knowledge_mcp_server.py  # :9006
```

### Agent Server + UI
```bash
pip install -r agents/requirements.txt
python agents/server.py                     # :8096
```

---

## Port Reference

| Service | Port | URL |
|---------|------|-----|
| **Loan Copilot UI** | 8096 | http://localhost:8096 |
| Customer Service | 8081 | http://localhost:8081/swagger-ui.html |
| KYC Service | 8082 | http://localhost:8082/swagger-ui.html |
| Document Service | 8083 | http://localhost:8083/swagger-ui.html |
| Risk Service | 8084 | http://localhost:8084/swagger-ui.html |
| Workflow Service | 8085 | http://localhost:8085/swagger-ui.html |
| Loan Service | 8086 | http://localhost:8086/swagger-ui.html |
| Customer MCP | 9001 | SSE |
| KYC MCP | 9002 | SSE |
| Document MCP | 9003 | SSE |
| Risk MCP | 9004 | SSE |
| Workflow MCP | 9005 | SSE |
| Knowledge MCP | 9006 | SSE |

---

## Docker Compose (Alternative)

```bash
# Requires Ollama running on host
docker compose up --build
```

---

## Sample Prompts

| Category | Prompt |
|----------|--------|
| Customer | *"Show me all active customers and their credit profiles"* |
| Loan Status | *"What is the full onboarding status for loan application 1?"* |
| KYC | *"What is the KYC status of customer 3 (GreenTech Solutions)?"* |
| Risk | *"Run a risk assessment for loan 3 with credit score 692"* |
| Documents | *"Show the document checklist for loan 1 — what is still pending?"* |
| Workflow | *"What is the workflow progress for loan 2 from XYZ Manufacturing?"* |
| Approvals | *"Are there any loans awaiting final approval?"* |
| Policy RAG | *"What are the eligibility criteria for a working capital loan?"* |
| Policy RAG | *"What is the maximum debt-to-income ratio allowed?"* |
| Platform | *"Check the health of all backend services"* |

---

## UI Screens

| Tab | Description |
|-----|-------------|
| **💬 Chat** | AI copilot chat with live agent reasoning panel |
| **📊 Dashboard** | Loan operations table + customer overview |
| **✅ Approvals** | HITL pending approvals — approve/reject directly |
| **🔧 System Health** | Real-time status of all 6 microservices + Ollama |

---

## Multi-Agent Flow

```
User: "Show full onboarding status for ABC Logistics loan"

Coordinator
  ├─ classify_intent  → "full_onboarding"
  ├─ select_agents    → [customer, kyc, document, risk, workflow, loan]
  ├─ execute_agents
  │   ├─ Customer Agent  → GET /api/v1/customers/search?name=ABC
  │   ├─ KYC Agent       → GET /api/v1/kyc/customer/1
  │   ├─ Document Agent  → GET /api/v1/documents/loan/1/checklist
  │   ├─ Risk Agent      → GET /api/v1/risk/loan/1/latest
  │   ├─ Workflow Agent  → GET /api/v1/workflows/loan/1/summary
  │   └─ Loan Agent      → GET /api/v1/loans/1
  └─ synthesize_response → Comprehensive markdown report
```

---

## HITL (Human-in-the-Loop) Flow

When a loan reaches `FINAL_APPROVAL` stage:
1. Workflow Agent detects `AWAITING_APPROVAL` status
2. Coordinator emits `hitl_required` SSE event
3. UI shows approval modal with loan context
4. Loan officer clicks **Approve** or **Reject**
5. Coordinator resumes, updates Workflow + Loan services
6. Final confirmation response streamed back to officer

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| LLM | Mistral 7B via Ollama |
| Agent Framework | LangGraph (StateGraph + HITL interrupts) |
| MCP Transport | FastMCP SSE (6 domain servers) |
| Backend | Spring Boot 3.2 / Java 17 / H2 |
| Agent API | FastAPI + SSE-Starlette |
| Frontend | Vanilla JS SPA (no build required) |
| RAG | ChromaDB-ready knowledge MCP server |
