#!/bin/bash

# Exit immediately if any command exits with a non-zero status
set -e

echo "[INFO] Starting trust repository audit and verification..."

# Example: Check if required configuration files exist
if [ ! -f "authorized-whitelist.json" ]; then
  echo "[ERROR] Missing authorized-whitelist.json!"
  exit 1
fi

# Run your Node.js verification or signing script
node sign-script.js

echo "[INFO] Trust check script completed successfully."
