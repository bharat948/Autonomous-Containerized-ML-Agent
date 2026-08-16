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

# Check if the container already exists
if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
    # Check if it is running
    if docker ps --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
        echo "Container '${CONTAINER_NAME}' is already running."
        exit 0
    else
        echo "Starting existing stopped container '${CONTAINER_NAME}'..."
        docker start ${CONTAINER_NAME}
        exit 0
    fi
fi

echo "Spinning up new container '${CONTAINER_NAME}' with image '${IMAGE_NAME}'..."
docker run -d \
  --name "${CONTAINER_NAME}" \
  -v "${WORKSPACE_DIR}:/workspace" \
  -w "/workspace" \
  "${IMAGE_NAME}" \
  tail -f /dev/null

echo "Container '${CONTAINER_NAME}' started successfully."
