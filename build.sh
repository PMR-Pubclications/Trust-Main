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