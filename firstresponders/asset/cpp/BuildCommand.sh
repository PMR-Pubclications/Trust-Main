# Set path to your installed Android NDK
export ANDROID_NDK_HOME=$HOME/Android/Sdk/ndk/25.2.9519653

# Generate CMake build files for ARM64 (64-bit real devices)
cmake -B build/android-arm64 \
  -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK_HOME/build/cmake/android.toolchain.cmake \
  -DANDROID_ABI=arm64-v8a \
  -DANDROID_PLATFORM=android-24 \
  -DANDROID_STL=c++_shared \
  -DCMAKE_BUILD_TYPE=Release

# Compile libAudioFilterEngine.so
cmake --build build/android-arm64 --config Release
