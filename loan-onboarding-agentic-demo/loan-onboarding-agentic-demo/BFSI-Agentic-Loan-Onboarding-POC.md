# BFSI Intelligent Loan Onboarding Copilot
## Enterprise Agentic AI POC Specification

### Version
1.0

### Objective
Build a complete Agentic AI Proof-of-Concept for Commercial Loan Onboarding in Banking.

The platform must demonstrate:
- Multi-Agent Collaboration
- MCP Gateway Pattern
- MCP Tool Discovery
- Deterministic Business Tools
- Spring Boot Microservices
- Human-in-the-Loop Approvals
- ChromaDB-based RAG
- MCP-based Backend Integration
- Enterprise Observability
- Auditability

The architecture should be deployable locally using:
- Docker Desktop
- Kubernetes (Optional)
- Ollama
- ChromaDB
- Python MCP Servers
- Spring Boot Services
- React UI

## Business Scenario
ABC Logistics applies for a commercial loan.

Customer: ABC Logistics
Loan Type: Working Capital
Amount: $2,500,000
Purpose: Fleet Expansion

## High-Level Architecture

```mermaid
flowchart TB
    USER["Loan Officer"]
    UI["Agentic Loan Portal"]
    ORCH["Coordinator Agent"]

    subgraph AGENTS
        CUST["Customer Agent"]
        RISK["Risk Agent"]
        OPS["Operations Agent"]
        KNOW["Knowledge Agent"]
        SRE["Platform Operations Agent"]
    end

    subgraph MCP
        GW["MCP Gateway"]
        CUST_MCP["Customer MCP"]
        DOC_MCP["Document MCP"]
        RISK_MCP["Risk MCP"]
        WF_MCP["Workflow MCP"]
        SRE_MCP["Operations MCP"]
        RAG_MCP["Knowledge MCP"]
    end

    subgraph SERVICES
        CUSTOMER_API["Customer Service"]
        KYC_API["KYC Service"]
        DOC_API["Document Service"]
        RISK_API["Risk Service"]
        WF_API["Workflow Service"]
        CORE_API["Loan Service"]
    end

    subgraph RAG
        CHROMADB["ChromaDB"]
        DOCS["Policy Documents"]
    end
```

## Technology Stack
- React / NextJS / Tailwind / Material UI
- Python LangGraph or CrewAI
- FastMCP
- Ollama (Qwen 3 / Mistral)
- ChromaDB
- Spring Boot Microservices

## Spring Boot Microservices
1. Customer Service
2. KYC Service
3. Document Service
4. Risk Service
5. Workflow Service
6. Loan Service

## MCP Gateway Responsibilities
- Tool Discovery
- Tool Registration
- Authentication
- Authorization
- Auditing
- Metrics
- Routing

## Agents
### Coordinator Agent
- Intent Classification
- Task Distribution
- Result Aggregation
- Approval Workflow Management

### Customer Agent
- Customer Profile Intelligence

### Risk Agent
- Credit & Risk Analysis

### Operations Agent
- Workflow Monitoring

### Knowledge Agent
- Policy & SOP Retrieval via ChromaDB

### Platform Operations Agent
- System Diagnostics

## UI Screens
1. Loan Operations Dashboard
2. Agent Chat
3. Agent Activity Timeline
4. MCP Activity Panel
5. Knowledge Evidence Panel
6. Observability Dashboard

## Deliverables
- React UI
- Coordinator Agent
- Five Domain Agents
- MCP Gateway
- Six MCP Servers
- Six Spring Boot Microservices
- ChromaDB Configuration
- Sample Banking Data
- Docker Compose
- Kubernetes Manifests
- Test Suite
- Demo Scripts
- Architecture Documentation

## Success Criteria
- Multi-Agent Architecture
- MCP Gateway Pattern
- Deterministic MCP Tools
- Spring Boot Backend Services
- ChromaDB-based RAG
- Human-in-the-Loop Governance
- Enterprise Auditability
- BFSI Business Relevance

## POC Tagline
Enterprise Agentic AI Commercial Loan Onboarding Copilot combining AI agents, MCP-based enterprise tool access, Spring Boot microservices, ChromaDB-powered knowledge retrieval, and governed decision making.
