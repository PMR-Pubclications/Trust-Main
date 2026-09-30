#!/bin/bash

# Exit immediately if any command exits with a non-zero status
set -e

echo "[INFO] Starting trust repository audit and verification..."

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
WHITELIST_FILE="${REPO_ROOT}/security/manifests/White-List-File.json"
SIGNATURE_SCRIPT="${REPO_ROOT}/security/javascript/nftsignature.js"

# Check if required whitelist file exists
if [ ! -f "$WHITELIST_FILE" ]; then
  echo "[ERROR] Missing White-List-File.json!"
  exit 1
fi

# Run NFT signature verification
echo "[INFO] Running NFT signature verification..."
node "$SIGNATURE_SCRIPT"

echo "[INFO] Trust check script completed successfully."
