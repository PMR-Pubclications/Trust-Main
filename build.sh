#!/usr/bin/env bash
# ==============================================================================
# Trust-Main: TFML Build & Deployment Script
# Compiles binaries, verifies dependencies, and auto-updates marketing collateral.
# ==============================================================================

set -e

echo "--------------------------------------------------"
echo "[TFML BUILD] Initiating Trust-Main Build Sequence..."
echo "--------------------------------------------------"

# Step 1: Environment Checks & Dependencies
if ! command -v python3 &> /dev/null; then
    echo "[BUILD ERROR] Python3 is required but not installed." >&2
    exit 1
fi

echo "[BUILD STEP 1/3] Verifying Python runtime and dependencies..."
python3 -m pip install --upgrade pip --quiet

# Step 2: Compile Real-Time Success & Marketing Package
echo "[BUILD STEP 2/3] Generating real-time municipal & hospital marketing package..."
python3 compile_marketing_package.py

# Step 3: Build Native Hardware & Firmware Modules (Trust-Main / firstResponder)
echo "[BUILD STEP 3/3] Building core hardware and firmware targets..."
if [ -d "modules/firstResponder" ]; then
    cd modules/firstResponder
    if [ -f "build.sh" ]; then
        ./build.sh
    fi
    cd ../..
fi

echo "--------------------------------------------------"
echo "[TFML BUILD SUCCESS] Build complete. Marketing package updated at asset/PressRelease/TFML_Master_Marketing_Package.md[span_20](start_span)[span_20](end_span)."
echo "--------------------------------------------------"

#!/usr/bin/env bash
# ==============================================================================
# Trust-Main: TFML Build & Deployment Script
# Compiles binaries, verifies dependencies, and auto-updates marketing collateral.
# ==============================================================================

set -e

echo "--------------------------------------------------"
echo "[TFML BUILD] Initiating Trust-Main Build Sequence..."
echo "--------------------------------------------------"

# Step 1: Environment Checks & Dependencies
if ! command -v python3 &> /dev/null; then
    echo "[BUILD ERROR] Python3 is required but not installed." >&2
    exit 1
fi

echo "[BUILD STEP 1/3] Verifying Python runtime and dependencies..."
python3 -m pip install --upgrade pip --quiet

# Step 2: Compile Real-Time Success & Marketing Package
echo "[BUILD STEP 2/3] Generating real-time municipal & hospital marketing package..."
python3 compile_marketing_package.py

# Step 3: Build Native Hardware & Firmware Modules (Trust-Main / firstResponder)
echo "[BUILD STEP 3/3] Building core hardware and firmware targets..."
if [ -d "modules/firstResponder" ]; then
    cd modules/firstResponder
    if [ -f "build.sh" ]; then
        ./build.sh
    fi
    cd ../..
fi

echo "--------------------------------------------------"
echo "[TFML BUILD SUCCESS] Build complete. Marketing package updated at asset/PressRelease/TFML_Master_Marketing_Package.md[span_20](start_span)[span_20](end_span)."
echo "--------------------------------------------------"

run https://github.com/PMR-Pubclications/Trust-Main/tree/main/sh

#!/usr/bin/env bash
# ==============================================================================
# Trust-Main: EMS Module Build & Compilation Script
# Installs dependencies, validates thermal/voice services, and generates reports.
# ==============================================================================

set -e

echo "--------------------------------------------------"
echo "[EMS BUILD] Initializing EMS Module Build Sequence..."
echo "--------------------------------------------------"

# Step 1: Install Python Requirements for EMS AI & Thermal Analyzer
if [ -f "requirements.txt" ]; then
    echo "[EMS BUILD STEP 1/2] Installing EMS Python dependencies..."
    python3 -m pip install -r requirements.txt --quiet
else
    echo "[EMS BUILD STEP 1/2] No requirements.txt found. Skipping dependency installation."
fi

# Step 2: Compile Local EMS Clinical Impact Report
echo "[EMS BUILD STEP 2/2] Compiling de-identified EMS clinical success metrics..."
python3 ems_compiler.py

echo "--------------------------------------------------"
echo "[EMS BUILD SUCCESS] EMS module build complete. Clinical report generated."
echo "--------------------------------------------------"


