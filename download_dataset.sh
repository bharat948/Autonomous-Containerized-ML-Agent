#!/bin/bash
set -e

DATASET_URL="https://raw.githubusercontent.com/mattdelhey/kaggle-titanic/master/Data/train.csv"
OUTPUT_FILE="titanic.csv"

echo "=== Downloading Tabular Dataset ==="
echo "Source: ${DATASET_URL}"

# Download dataset
curl -sL "${DATASET_URL}" -o "${OUTPUT_FILE}"

if [ ! -f "${OUTPUT_FILE}" ] || [ ! -s "${OUTPUT_FILE}" ]; then
    echo "[ERROR] Failed to download dataset or file is empty!"
    exit 1
fi

echo "[OK] Dataset downloaded successfully to ${OUTPUT_FILE}."
echo ""
echo "=== File Info ==="
ls -lh "${OUTPUT_FILE}"
echo ""
echo "=== First 5 Rows ==="
head -n 5 "${OUTPUT_FILE}"
exit 0
