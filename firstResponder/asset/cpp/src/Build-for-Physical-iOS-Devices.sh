# Generate Xcode project targeting real iPhones/iPads
cmake -B build/ios-device -G Xcode \
  -DCMAKE_SYSTEM_NAME=iOS \
  -DCMAKE_OSX_SYSROOT=iphoneos \
  -DCMAKE_OSX_ARCHITECTURES=arm64 \
  -DCMAKE_BUILD_TYPE=Release

# Build static library (.a)
cmake --build build/ios-device --config Release
