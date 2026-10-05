#!/usr/bin/env bash

# ==============================================================================
# Trust-Main: firstResponder Submodule & C++ Native Build Pipeline
# Automates submodule initialization, dependency verification, 
# AudioVideoEngine-CPP linkage, and pyboson C++ binding compilation.
# ==============================================================================

set -e # Exit immediately if any command fails
set -o pipefail

# Color Codes for Terminal Output
RED='\030[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_succ()  { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_err()   { echo -e "${RED}[ERROR]${NC} $1"; }

# 1. Resolve Script & Target Working Directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

# Navigate to firstResponder directory if executed from Trust-Main root
if [ -d "$PROJECT_ROOT/firstResponder" ]; then
    PROJECT_ROOT="$PROJECT_ROOT/firstResponder"
fi

cd "$PROJECT_ROOT"
log_info "Working directory set to: $PROJECT_ROOT"

# 2. Check System Tooling Prerequisites
log_info "Checking build dependencies..."

COMMANDS=(git cmake g++ python3)
for cmd in "${COMMANDS[@]}"; do
    if ! command -v "$cmd" &> /dev/null; then
        log_err "Required tool '$cmd' is not installed or not in PATH."
        exit 1
    fi
done

# Verify pybind11 availability in Python environment
if ! python3 -c "import pybind11" &> /dev/null; then
    log_warn "pybind11 python package not found. Attempting install via pip..."
    python3 -m pip install pybind11 || {
        log_err "Failed to install pybind11 via pip. Please install pybind11 manually."
        exit 1
    }
fi
log_succ "All host prerequisites verified."

# 3. Initialize & Sync Git Submodules
log_info "Initializing Git submodules (AudioVideoEngine-CPP)..."
git submodule update --init --recursive || {
    log_warn "Git submodule update failed or no .gitmodules configured at local level."
    log_warn "CMake FetchContent will fall back to pull directly from GitHub if needed."
}

# Ensure vendor directory exists
mkdir -p vendor

# Clone AudioVideoEngine-CPP locally into vendor/ if missing
VENDOR_ENGINE_DIR="$PROJECT_ROOT/vendor/AudioVideoEngine-CPP"
if [ ! -d "$VENDOR_ENGINE_DIR" ]; then
    log_info "Cloning AudioVideoEngine-CPP into vendor directory..."
    git clone https://github.com/PMR-Pubclications/AudioVideoEngine-CPP.git "$VENDOR_ENGINE_DIR"
else
    log_info "AudioVideoEngine-CPP repository verified at $VENDOR_ENGINE_DIR"
fi

# 4. Configure & Execute CMake Build
BUILD_DIR="$PROJECT_ROOT/build"
log_info "Preparing build directory at $BUILD_DIR..."
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Determine core count for parallel compilation
NPROC=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

log_info "Running CMake configuration..."
cmake -DCMAKE_BUILD_TYPE=Release ..

log_info "Compiling native targets using $NPROC worker threads..."
make -j"$NPROC"

# 5. Link Compiled pyboson Shared Object to Python Module Directory
PYTHON_DIR="$PROJECT_ROOT/python"
mkdir -p "$PYTHON_DIR"

# Locate compiled shared library (.so / .dylib / .pyd)
PYBOSON_LIB=$(find "$BUILD_DIR" -type f \( -name "pyboson*.so" -o -name "pyboson*.dylib" -o -name "pyboson*.pyd" \) | head -n 1)

if [ -n "$PYBOSON_LIB" ]; then
    cp "$PYBOSON_LIB" "$PYTHON_DIR/"
    log_succ "Successfully copied compiled module: $(basename "$PYBOSON_LIB") -> firstResponder/python/"
else
    log_err "Build succeeded, but compiled pyboson module binary was not found in build directory."
    exit 1
fi

log_succ "Build process complete! You can now run the EMS loop:"
echo -e "      ${YELLOW}cd $PROJECT_ROOT/python && python3 ems_ai_module.py${NC}"

python3 test_pyboson.py

