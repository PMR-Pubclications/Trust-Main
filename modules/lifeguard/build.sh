#!/usr/bin/env bash
# ==============================================================================
# Trust-Main: Lifeguard Module Build & Compilation Script
# Installs dependencies and generates Lifeguard & Aquatic Rescue reports.
# ==============================================================================

set -e

echo "--------------------------------------------------"
echo "[LIFEGUARD BUILD] Initializing Lifeguard Module Build Sequence..."
echo "--------------------------------------------------"

# Step 1: Install Python Requirements for Aquatic / Sensor Services
if [ -f "requirements.txt" ]; then
    echo "[LIFEGUARD BUILD STEP 1/2] Installing Lifeguard Python dependencies..."
    python3 -m pip install -r requirements.txt --quiet
else
    echo "[LIFEGUARD BUILD STEP 1/2] No requirements.txt found. Skipping dependency installation."
fi

# Step 2: Compile Local Lifeguard Aquatic Safety Report
echo "[LIFEGUARD BUILD STEP 2/2] Compiling Lifeguard rescue success metrics..."
python3 lifeguard_compiler.py

echo "--------------------------------------------------"
echo "[LIFEGUARD BUILD SUCCESS] Lifeguard module build complete. Aquatic safety report generated."
echo "--------------------------------------------------"
