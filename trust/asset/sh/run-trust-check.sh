#!/bin/bash

# Exit immediately if any command exits with a non-zero status
set -e

echo "[INFO] Starting trust repository audit and verification..."

# Check if required whitelist file exists
if [ ! -f "White-List-File.json" ]; then
  echo "[ERROR] Missing White-List-File.json!"
  exit 1
fi

# Run NFT signature verification
echo "[INFO] Running NFT signature verification..."
node nftsignature.js

echo "[INFO] Trust check script completed successfully."
