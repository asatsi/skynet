#!/bin/bash
BASE="$(cd "$(dirname "$0")" && pwd)"
LOG="$BASE/logs"
echo "[STOP] Stopping all BFSI Loan Onboarding services…"
STOPPED=0
for PID_FILE in "$LOG"/*.pid; do
    [ -f "$PID_FILE" ] || continue
    PID=$(cat "$PID_FILE")
    NAME=$(basename "$PID_FILE" .pid)
    if kill "$PID" 2>/dev/null; then
        echo "  ✅ Stopped $NAME (PID $PID)"
        STOPPED=$((STOPPED+1))
    else
        echo "  ⚠️  $NAME (PID $PID) was not running"
    fi
    rm -f "$PID_FILE"
done
echo "[STOP] Done — stopped $STOPPED process(es)."
