#!/usr/bin/env bash
set -e

CONTAINER_NAME="sandbox-container"
IMAGE_NAME="python:3.11-slim"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${1:-$REPO_DIR/data}"

# Ensure DATA_DIR exists as absolute path
mkdir -p "${DATA_DIR}"
DATA_DIR_ABS="$(cd "${DATA_DIR}" && pwd)"

echo "=== Setting up TDD Sandbox Container ==="
echo "Repo Directory: ${REPO_DIR}"
echo "Data Workspace Directory: ${DATA_DIR_ABS}"

# 1. Check if docker daemon is running
if ! docker info >/dev/null 2>&1; then
    echo "Error: Docker service is not running or accessible. Please start Docker Desktop/Daemon." >&2
    exit 1
fi

# 2. Check if container exists and stop/remove it to ensure fresh mount config
if docker ps -a --format '{{.Names}}' | grep -wq "${CONTAINER_NAME}"; then
    echo "Stopping and removing existing '${CONTAINER_NAME}' to reload environment and mount config..."
    docker stop "${CONTAINER_NAME}" >/dev/null 2>&1 || true
    docker rm "${CONTAINER_NAME}" >/dev/null 2>&1 || true
fi

# 3. Port mapping configuration (loaded from .env if present)
PORT_FLAGS=""
ENV_FLAG=""

if [ -f "${REPO_DIR}/.env" ]; then
    echo "Found .env file. Loading environment keys..."
    ENV_FLAG="--env-file ${REPO_DIR}/.env"
    
    HOST_PORT_JUPYTER=$(grep -E '^HOST_PORT_JUPYTER=' "${REPO_DIR}/.env" | cut -d '=' -f2 || echo "8888")
    HOST_PORT_TENSORBOARD=$(grep -E '^HOST_PORT_TENSORBOARD=' "${REPO_DIR}/.env" | cut -d '=' -f2 || echo "6006")
    HOST_PORT_API=$(grep -E '^HOST_PORT_API=' "${REPO_DIR}/.env" | cut -d '=' -f2 || echo "8000")
    
    PORT_FLAGS="-p ${HOST_PORT_JUPYTER:-8888}:8888 -p ${HOST_PORT_TENSORBOARD:-6006}:6006 -p ${HOST_PORT_API:-8000}:8000"
    echo "Exposing ports: Jupyter=${HOST_PORT_JUPYTER:-8888}, TensorBoard=${HOST_PORT_TENSORBOARD:-6006}, API=${HOST_PORT_API:-8000}"
else
    echo "Warning: No .env file found. Container will start without pre-loaded API keys."
fi

# 4. Spin up container with dual volume mounts and VENV PATH configuration
echo "Spinning up new container '${CONTAINER_NAME}' with image '${IMAGE_NAME}'..."
docker run -d \
  --name "${CONTAINER_NAME}" \
  ${ENV_FLAG} \
  ${PORT_FLAGS} \
  -e PATH="/opt/venv/bin:/usr/local/bin:/usr/bin:/bin" \
  -e VIRTUAL_ENV="/opt/venv" \
  -v "${DATA_DIR_ABS}":/workspace:rw \
  -v "${REPO_DIR}/agent.py":/app/agent.py:ro \
  -v "${REPO_DIR}/system_prompt.txt":/app/system_prompt.txt:ro \
  -w /workspace \
  "${IMAGE_NAME}" \
  tail -f /dev/null

echo "Initializing Python virtual environment (/opt/venv)..."
docker exec "${CONTAINER_NAME}" python -m venv /opt/venv

echo "Pre-caching core ML dependencies (openai, pandas, scikit-learn, joblib, xgboost, lightgbm)..."
docker exec "${CONTAINER_NAME}" /opt/venv/bin/pip install --quiet openai pandas scikit-learn joblib xgboost lightgbm numpy

echo "Container '${CONTAINER_NAME}' ready with virtualenv /opt/venv."
echo "Workspace: /workspace (RW) | App Code: /app (RO)"
