#!/bin/bash

CONTAINER_NAME="sandbox-container"

echo "Stopping and removing container '${CONTAINER_NAME}' if it exists..."

if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
    docker stop "${CONTAINER_NAME}" >/dev/null 2>&1 || true
    docker rm "${CONTAINER_NAME}" >/dev/null 2>&1 || true
    echo "Container '${CONTAINER_NAME}' stopped and removed."
else
    echo "Container '${CONTAINER_NAME}' does not exist. Nothing to do."
fi

# Clean up any leftover test files
rm -f /home/bharat/explore/test_mount_host.txt
