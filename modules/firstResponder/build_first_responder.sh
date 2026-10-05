#!/usr/bin/env bash

set -e
set -o pipefail

# Locate absolute script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "[INFO] Building firstResponder module at: $SCRIPT_DIR"

# 1. Ensure vendor directory and AudioVideoEngine-CPP are present
mkdir -p vendor
VENDOR_ENGINE="$SCRIPT_DIR/vendor/AudioVideoEngine-CPP"

if [ ! -d "$VENDOR_ENGINE" ]; then
    echo "[INFO] Cloning AudioVideoEngine-CPP into $VENDOR_ENGINE..."
    git clone https://github.com/PMR-Pubclications/AudioVideoEngine-CPP.git "$VENDOR_ENGINE"
fi

# 2. Configure CMake inside modules/firstResponder/build
BUILD_DIR="$SCRIPT_DIR/build"
PYTHON_DIR="$SCRIPT_DIR/python"

mkdir -p "$BUILD_DIR"
mkdir -p "$PYTHON_DIR"

cd "$BUILD_DIR"

echo "[INFO] Running CMake build configuration..."
cmake -DCMAKE_BUILD_TYPE=Release ..

NPROC=$(nproc 2>/dev/null || echo 4)
make -j"$NPROC"

# 3. Copy compiled pyboson shared library into modules/firstResponder/python/
PYBOSON_LIB=$(find "$BUILD_DIR" -type f \( -name "pyboson*.so" -o -name "pyboson*.dylib" -o -name "pyboson*.pyd" \) | head -n 1)

if [ -n "$PYBOSON_LIB" ]; then
    cp "$PYBOSON_LIB" "$PYTHON_DIR/"
    echo "[SUCCESS] Shared library copied: $(basename "$PYBOSON_LIB") -> modules/firstResponder/python/"
else
    echo "[ERROR] Compilation finished but pyboson binary missing in build folder."
    exit 1
fi
