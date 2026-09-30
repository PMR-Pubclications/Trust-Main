# Trust-Main security/native/camera
#
# Cross-platform camera capture abstraction shared by the face and gait
# capture front-ends (mobile/browser) before frames reach the face/gait
# recognition stubs. Only one platform backend is compiled per target:
#   - Linux (V4L2)      -> requires a real camera capture pipeline to be
#                          wired in; this repository only ships device
#                          enumeration, not recognition.
#   - Android (Camera2/NDK)
#   - iOS (AVFoundation)
#
# This CMakeLists.txt exists to allow a headless Linux CI/server to at
# least compile-check the Linux backend as part of the /security smoke
# checks. It intentionally does not attempt to build the Android/iOS
# backends on Linux (they require their respective SDKs/toolchains).
cmake_minimum_required(VERSION 3.18)
project(TrustSecurityCamera CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(CMAKE_SYSTEM_NAME STREQUAL "Linux" AND NOT ANDROID)
    message(STATUS "[security/native/camera] Configuring Linux V4L2 backend")

    add_library(trust_security_camera_linux OBJECT linux/LinuxCamera.cpp)
    target_include_directories(trust_security_camera_linux PUBLIC include)
    target_compile_definitions(trust_security_camera_linux PRIVATE PLATFORM_LINUX=1)

elseif(ANDROID)
    message(STATUS "[security/native/camera] Configuring Android NDK backend")

    add_library(trust_security_camera_android OBJECT
        android/AndroidCamera.cpp
        android/native_camera.cpp
    )
    target_include_directories(trust_security_camera_android PUBLIC include)
    target_compile_definitions(trust_security_camera_android PRIVATE PLATFORM_ANDROID=1)

    find_library(camera2ndk-lib camera2ndk)
    find_library(log-lib log)
    target_link_libraries(trust_security_camera_android PRIVATE ${camera2ndk-lib} ${log-lib})

elseif(IOS)
    message(STATUS "[security/native/camera] Configuring iOS AVFoundation backend")

    add_library(trust_security_camera_ios OBJECT ios/IOSCamera.mm)
    target_include_directories(trust_security_camera_ios PUBLIC include)
    target_compile_definitions(trust_security_camera_ios PRIVATE PLATFORM_IOS=1)

    find_library(AVFOUNDATION_FRAMEWORK AVFoundation)
    target_link_libraries(trust_security_camera_ios PRIVATE ${AVFOUNDATION_FRAMEWORK})

else()
    message(WARNING "[security/native/camera] No supported platform backend for this target; skipping native camera build.")
endif()
