#!/bin/bash
set -e

CONTAINER_NAME="sandbox-container"
IMAGE_NAME="python:3.11-slim"
WORKSPACE_DIR="/home/bharat/explore"

echo "Checking if Docker is running..."
if ! docker info >/dev/null 2>&1; then
    echo "Error: Docker daemon is not running. Please start Docker."
    exit 1
fi

# Stop and remove the existing container to ensure new environment variables from .env are loaded
if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
    echo "Stopping and removing existing '${CONTAINER_NAME}' to reload environment config..."
    docker stop "${CONTAINER_NAME}" >/dev/null 2>&1 || true
    docker rm "${CONTAINER_NAME}" >/dev/null 2>&1 || true
fi

ENV_ARG=""
if [ -f "${WORKSPACE_DIR}/.env" ]; then
    echo "Found .env file. Loading environment keys..."
    ENV_ARG="--env-file ${WORKSPACE_DIR}/.env"
    
    # Load HOST_PORT variables to host shell if defined in .env
    export $(grep -E "^HOST_PORT_" "${WORKSPACE_DIR}/.env" | xargs)
fi

# Apply fallback defaults for ports if not explicitly defined
HOST_PORT_JUPYTER=${HOST_PORT_JUPYTER:-8888}
HOST_PORT_TENSORBOARD=${HOST_PORT_TENSORBOARD:-6006}
HOST_PORT_API=${HOST_PORT_API:-8000}

PORT_ARG="-p ${HOST_PORT_JUPYTER}:8888 -p ${HOST_PORT_TENSORBOARD}:6006 -p ${HOST_PORT_API}:8000"

echo "Spinning up new container '${CONTAINER_NAME}' with image '${IMAGE_NAME}'..."
echo "Exposing ports: Jupyter=${HOST_PORT_JUPYTER}, TensorBoard=${HOST_PORT_TENSORBOARD}, API=${HOST_PORT_API}"
docker run -d \
  --name "${CONTAINER_NAME}" \
  ${ENV_ARG} \
  ${PORT_ARG} \
  -v "${WORKSPACE_DIR}:/workspace" \
  -w "/workspace" \
  "${IMAGE_NAME}" \
  tail -f /dev/null

echo "Container '${CONTAINER_NAME}' started successfully with mounted workspace."
