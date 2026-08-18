#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${1:-$REPO_DIR/data}"

# Shift first arg if it was provided as data dir
if [ "$#" -gt 0 ]; then
    shift
fi

# Remaining args (if any) form the custom prompt
PROMPT="$*"

echo "=================================================="
echo "   Containerized TDD ML Agent Entrypoint"
echo "=================================================="
echo "Repo Directory: ${REPO_DIR}"
echo "Data Directory: ${DATA_DIR}"

if [ ! -d "${DATA_DIR}" ]; then
    echo "Creating target data directory: ${DATA_DIR}"
    mkdir -p "${DATA_DIR}"
fi

# 1. Initialize Sandbox with dual mounts (Workspace RW, App Code RO)
"${REPO_DIR}/setup_sandbox.sh" "${DATA_DIR}"

# 2. Ensure python dependencies inside container
echo "Ensuring container python dependencies (openai)..."
docker exec sandbox-container pip install --quiet openai

echo ""
echo "=== Invoking Sandbox Agent ==="

# 3. Execute agent inside container
if [ -n "${PROMPT}" ]; then
    docker exec sandbox-container python /app/agent.py "${PROMPT}"
else
    docker exec sandbox-container python /app/agent.py
fi

echo ""
echo "=== Execution Complete ==="
if [ -f "${DATA_DIR}/agent_trace.json" ]; then
    echo "Execution trace written to: ${DATA_DIR}/agent_trace.json"
fi
exit 0
