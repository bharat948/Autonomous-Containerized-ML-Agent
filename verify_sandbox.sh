#!/bin/bash

CONTAINER_NAME="sandbox-container"
TEST_FILE="/home/bharat/explore/test_mount_host.txt"

echo "=== Sandbox Verification ==="

# 1. Check if container is running
if ! docker ps --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
    echo "[ERROR] Container '${CONTAINER_NAME}' is not running!"
    exit 1
fi

echo "[1/4] Container is running."

# 2. Write file on host
echo "host_write" > "${TEST_FILE}"
if [ ! -f "${TEST_FILE}" ]; then
    echo "[ERROR] Failed to write test file on host!"
    exit 1
fi
echo "[2/4] Wrote test file on host."

# 3. Read & append inside container
if ! docker exec "${CONTAINER_NAME}" sh -c '[ -f /workspace/test_mount_host.txt ]'; then
    echo "[ERROR] Test file is not visible inside the container! Mount verification failed."
    rm -f "${TEST_FILE}"
    exit 1
fi

# Append inside container
docker exec "${CONTAINER_NAME}" sh -c 'echo "container_append" >> /workspace/test_mount_host.txt'
echo "[3/4] Successfully read and appended to test file inside container."

# 4. Verify content on host
if ! grep -q "host_write" "${TEST_FILE}" || ! grep -q "container_append" "${TEST_FILE}"; then
    echo "[ERROR] Appended content from container was not reflected on host!"
    rm -f "${TEST_FILE}"
    exit 1
fi
echo "[4/4] Verified container updates on host."

# Cleanup
rm -f "${TEST_FILE}"
echo "[OK] Sandbox mount verification passed successfully!"
exit 0
