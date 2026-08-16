#!/bin/bash
set -e

CONTAINER_NAME="sandbox-container"

echo "=== Agent Verification Inside Sandbox ==="

# 1. Check if container is running
if ! docker ps --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
    echo "[ERROR] Sandbox container '${CONTAINER_NAME}' is not running! Please run ./setup_sandbox.sh first."
    exit 1
fi

# 2. Verify dependencies inside container
echo "Preparing python dependencies inside container..."
docker exec "${CONTAINER_NAME}" pip install --upgrade pip >/dev/null 2>&1 || true
docker exec "${CONTAINER_NAME}" pip install openai >/dev/null 2>&1 || true

echo "Dependencies verified. Invoking containerized agent..."

# 3. Invoke agent inside Docker (keys loaded from container environment)
docker exec \
  "${CONTAINER_NAME}" \
  python /workspace/agent.py

echo "=== Agent Verification Done ==="
exit 0
