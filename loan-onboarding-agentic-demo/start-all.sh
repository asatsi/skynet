#!/bin/bash
echo "Did you activate .venv in mcp-servers?"
# BFSI Loan Onboarding Copilot — start-all.sh
# Works on macOS AND Linux; uses python3/pip3 explicitly.
set -e
BASE="$(cd "$(dirname "$0")" && pwd)"
LOG="$BASE/logs"
mkdir -p "$LOG"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info() { echo -e "${GREEN}[START]${NC} $*"; }
wait_msg(){ echo -e "${YELLOW}[WAIT] ${NC} $*"; }
ok()  { echo -e "${CYAN}[OK]   ${NC} $*"; }

info "=== BFSI Loan Onboarding Copilot ==="
echo ""

# ── Detect python3 / pip3 ──────────────────────────────────────────────────────
PYTHON=$(command -v python3 || command -v python)
PIP=$(command -v pip3 || command -v pip)
info "Python: $PYTHON   Pip: $PIP"

# ── 1. Build Spring Boot services ─────────────────────────────────────────────
info "Building Spring Boot microservices…"
for SVC in customer-service kyc-service document-service \
           risk-service workflow-service loan-service; do
    info "  Building $SVC…"
    (cd "$BASE/services/$SVC" && mvn -q package -DskipTests 2>&1 | tail -3)
    ok "  $SVC built"
done
echo ""

# ── 2. Start Spring Boot services ─────────────────────────────────────────────
info "Starting Spring Boot microservices…"

start_svc() {
    local name=$1 port=$2
    local jar
    jar=$(ls "$BASE/services/$name/target/"*.jar 2>/dev/null | head -1)
    if [ -z "$jar" ]; then
        echo "  ⚠️  No JAR for $name — skipping"
        return
    fi
    info "  Starting $name on :$port"
    nohup java -jar "$jar" > "$LOG/$name.log" 2>&1 &
    echo $! > "$LOG/$name.pid"
}

start_svc customer-service  8081
start_svc kyc-service        8082
start_svc document-service   8083
start_svc risk-service       8084
start_svc workflow-service   8085
start_svc loan-service       8086

wait_msg "Waiting 20s for Spring Boot services to initialise…"
sleep 20
echo ""

# ── 3. Install Python dependencies ────────────────────────────────────────────
info "Installing Python dependencies…"
$PIP install -q -r "$BASE/mcp-servers/requirements.txt" 2>&1 | tail -2
$PIP install -q -r "$BASE/agents/requirements.txt"      2>&1 | tail -2
ok "Python dependencies ready"
echo ""

# ── 4. Start MCP domain servers ───────────────────────────────────────────────
info "Starting MCP domain servers…"

start_mcp() {
    local script=$1 port=$2
    info "  Starting $script on :$port"
    nohup $PYTHON "$BASE/mcp-servers/$script" \
        > "$LOG/$script.log" 2>&1 &
    echo $! > "$LOG/$script.pid"
}

start_mcp customer_mcp_server.py  9001
start_mcp kyc_mcp_server.py       9002
start_mcp document_mcp_server.py  9003
start_mcp risk_mcp_server.py      9004
start_mcp workflow_mcp_server.py  9005
start_mcp knowledge_mcp_server.py 9006
start_mcp loan_mcp_server.py      9007

wait_msg "Waiting 6s for MCP servers…"
sleep 6
echo ""

# ── 5. Start MCP Gateway ───────────────────────────────────────────────────────
info "Starting MCP Gateway on :9000…"
nohup $PYTHON "$BASE/mcp-servers/gateway_server.py" \
    > "$LOG/gateway_server.log" 2>&1 &
echo $! > "$LOG/gateway_server.pid"
sleep 3
echo ""

# ── 6. Start Agent Server + UI ────────────────────────────────────────────────
info "Starting Agent Server + UI on :8096…"
nohup $PYTHON "$BASE/agents/server.py" \
    > "$LOG/agent-server.log" 2>&1 &
echo $! > "$LOG/agent-server.pid"
sleep 5
echo ""

# ── 7. Summary ─────────────────────────────────────────────────────────────────
info "=== All services started ==="
echo ""
echo "  🏦  Loan Copilot UI       →  http://localhost:8096"
echo ""
echo "  ── Spring Boot ──────────────────────────────────────"
echo "  👤  Customer Service      →  http://localhost:8081/swagger-ui.html"
echo "  🔐  KYC Service           →  http://localhost:8082/swagger-ui.html"
echo "  📄  Document Service      →  http://localhost:8083/swagger-ui.html"
echo "  ⚠️   Risk Service          →  http://localhost:8084/swagger-ui.html"
echo "  🔄  Workflow Service      →  http://localhost:8085/swagger-ui.html"
echo "  💰  Loan Service          →  http://localhost:8086/swagger-ui.html"
echo ""
echo "  ── MCP Servers ──────────────────────────────────────"
echo "  🔌  MCP Gateway           →  http://localhost:9000/tools"
echo "  🔌  Customer MCP          →  http://localhost:9001/sse"
echo "  🔌  KYC MCP               →  http://localhost:9002/sse"
echo "  🔌  Document MCP          →  http://localhost:9003/sse"
echo "  🔌  Risk MCP              →  http://localhost:9004/sse"
echo "  🔌  Workflow MCP          →  http://localhost:9005/sse"
echo "  🔌  Knowledge MCP         →  http://localhost:9006/sse"
echo "  🔌  Loan MCP              →  http://localhost:9007/sse"
echo ""
echo "  📁  Logs  →  $LOG/"
echo "  🛑  Stop  →  ./stop-all.sh"
echo ""
