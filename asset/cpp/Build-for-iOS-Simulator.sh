# Target iOS Simulator on Apple Silicon Macs (M1/M2/M3/M4)
cmake -B build/ios-simulator -G Xcode \
  -DCMAKE_SYSTEM_NAME=iOS \
  -DCMAKE_OSX_SYSROOT=iphonesimulator \
  -DCMAKE_OSX_ARCHITECTURES=arm64 \
  -DCMAKE_BUILD_TYPE=Debug

cmake --build build/ios-simulator --config Debug
