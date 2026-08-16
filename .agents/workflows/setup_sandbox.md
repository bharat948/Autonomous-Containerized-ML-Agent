---
description: How to spin up, verify, and tear down the Docker sandbox container with directory mounts.
---

# Setup Sandbox Environment

Follow these steps to set up the container workspace and run verification tests on the directory mounts.

## Step 1: Initializing the Sandbox Container
Run the setup script to pull the python docker image and spin it up in the background:
```bash
./setup_sandbox.sh
```

## Step 2: Running Automated Verification
Run the verification script. It will write a test file on the host, execute a command inside the container to read it and append to it, and then check that the result was written back to the host:
```bash
./verify_sandbox.sh
```

Expected output:
`[OK] Sandbox mount verification passed successfully!`

## Step 3: Tearing Down the Sandbox
When work is complete or you want to restart in a clean state:
```bash
./teardown.sh
```
