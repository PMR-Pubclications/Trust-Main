# Update submodules across Trust-Main
git submodule update --init --recursive

# Test-build the server-side backend stack
cd Trust-Main
mkdir -p build && cd build
cmake ..
make -j$(nproc)
