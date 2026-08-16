# TDD-Driven Sandbox Agent System

A local, isolated Machine Learning (ML) agent runner workspace designed to safely execute data processing, feature selection, and traditional ML model training within a Docker container sandbox.

---

## Technical Architecture Overview
The agent runs directly inside the Docker sandbox container, restricting arbitrary execution tasks from accessing the host's files, secrets, or network directly. The workspace features strict **Test-Driven Development (TDD)** checking scripts to verify every state.

---

## 1. Setup Instructions

### Prerequisites
- Docker / Docker Desktop installed and running.
- Bash/Linux shell.

### Step 1: Clone/Configure Environment Keys
1. Copy the `.env.template` file to `.env`:
   ```bash
   cp .env.template .env
   ```
2. Open `.env` and fill in your absolute API keys (either `OPENAI_API_KEY` or `GEMINI_API_KEY`):
   ```ini
   OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
   GEMINI_API_KEY=YOUR_KEY_HERE
   ```

### Step 2: Configure Ports Mapping (Optional)
The Docker container exposes three default ports to the host shell for ML development (e.g. visualizing dashboards, serving predictions, running notebooks). You can override these local host ports inside `.env`:
- `HOST_PORT_JUPYTER` (default: `8888`)
- `HOST_PORT_TENSORBOARD` (default: `6006`)
- `HOST_PORT_API` (default: `8000`)

### Step 3: Spinning up the Sandbox Container
Run the startup script:
```bash
./setup_sandbox.sh
```
This script stops any running container instances, loads the current `.env` configurations, publishes the host ports, mounts your workspace directory, and starts the container in the background.

---

## 2. Verification & Testing

Verify each component is functional using the automated test suite:

### Test 1: Filesystem Mount Verification
Tests that files are read, written, and updated correctly across both the host and the container.
```bash
./verify_sandbox.sh
```
**Expected Output:**
`[OK] Sandbox mount verification passed successfully!`

### Test 2: Connection & LLM Connection Verification
Ensures Python dependencies (`openai` SDK client) install correctly in the container, environment variables from `.env` are injected, and `agent.py` can fetch completions.
```bash
./verify_agent.sh
```
**Expected Output:**
```
=== LLM Response ===
I can read your message.
====================
Connection verification passed successfully!
```

---

## 3. Teardown & Clean Up

To stop and remove the container when finished developing:
```bash
./teardown.sh
```
This halts the container, removes it from the local Docker tables, and deletes any leftover temporary testing files.
