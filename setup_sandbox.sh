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
else
    echo "Warning: No .env file found at ${WORKSPACE_DIR}/.env"
fi

echo "Spinning up new container '${CONTAINER_NAME}' with image '${IMAGE_NAME}'..."
docker run -d \
  --name "${CONTAINER_NAME}" \
  ${ENV_ARG} \
  -v "${WORKSPACE_DIR}:/workspace" \
  -w "/workspace" \
  "${IMAGE_NAME}" \
  tail -f /dev/null

echo "Container '${CONTAINER_NAME}' started successfully with mounted workspace."
