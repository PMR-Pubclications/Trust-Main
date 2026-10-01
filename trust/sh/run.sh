#!/bin/bash
# Root-level runner for Trustfence Teardown Service

# Get the absolute path of the repository root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/trust_teardown.py"

echo "[*] Initializing Trustfence Teardown Handler from root..."

# Check for root permissions (needed for kernel cache purging)
if [ "$EUID" -ne 0 ]; then
    echo "[!] Warning: Not running as root. Cache purging (/proc/sys/vm/drop_caches) will require elevation."
fi

# Verify the Python script exists in the root
if [ -f "$PYTHON_script" ]; then
    echo "[+] Launching Python teardown server..."
    python3 "$PYTHON_SCRIPT"
else
    echo "[!] Error: trust_teardown.py not found in the root directory."
    exit 1
fi
