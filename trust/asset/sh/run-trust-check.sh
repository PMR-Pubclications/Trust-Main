#!/bin/bash

# Exit immediately if any command exits with a non-zero status
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[INFO] Starting trust repository audit and verification..."

# Check if required whitelist file exists
if [ ! -f "$SCRIPT_DIR/../json/White-List-File.json" ]; then
  echo "[ERROR] Missing White-List-File.json!"
  exit 1
fi

# Run NFT signature verification
echo "[INFO] Running NFT signature verification..."
node "$SCRIPT_DIR/../js/nftsignature.js"

echo "[INFO] Trust check script completed successfully."
