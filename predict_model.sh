#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${1:-$REPO_DIR/data}"

if [ "$#" -gt 0 ]; then
    shift
fi

INPUT_JSON="${1:-{\}}"

if [ ! -d "${DATA_DIR}" ]; then
    echo "Error: Data directory '${DATA_DIR}' does not exist." >&2
    exit 1
fi

if [ ! -f "${DATA_DIR}/final_model.pkl" ]; then
    echo "Error: No trained model binary found at '${DATA_DIR}/final_model.pkl'." >&2
    exit 1
fi

if [ ! -f "${DATA_DIR}/predict.py" ]; then
    echo "Error: No inference script found at '${DATA_DIR}/predict.py'." >&2
    exit 1
fi

# Ensure sandbox container is up with target dataset mounted
"${REPO_DIR}/setup_sandbox.sh" "${DATA_DIR}" >/dev/null 2>&1

echo "=================================================="
echo "   Containerized Model Inference Runner"
echo "=================================================="
echo "Workspace Data Dir: ${DATA_DIR}"
echo "Input JSON Sample:  ${INPUT_JSON}"
echo "--------------------------------------------------"
echo "Executing Prediction Output:"

docker exec sandbox-container python /workspace/predict.py "${INPUT_JSON}"
echo "=================================================="
