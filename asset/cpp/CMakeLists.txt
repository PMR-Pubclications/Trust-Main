target_link_libraries(
    your-native-lib
    camera2ndk
    log
)

cmake_minimum_required(VERSION 3.18)
project(CrossPlatformAudio CXX)

set(COMMON_SOURCES src/main.cpp src/LMSFilter.cpp)

if(ANDROID)
    # Include only Android source files
    list(APPEND PLATFORM_SOURCES src/android/AndroidAudio.cpp)
    find_package(oboe REQUIRED CONFIG)
    set(PLATFORM_LIBS oboe::oboe)

elseif(IOS)
    # Include only iOS Objective-C++ source files
    list(APPEND PLATFORM_SOURCES src/ios/IOSAudio.mm)
    find_library(AVFOUNDATION_FRAMEWORK AVFoundation)
    set(PLATFORM_LIBS ${AVFOUNDATION_FRAMEWORK})
endif()

# Build executable with target-specific files only
add_executable(AudioApp ${COMMON_SOURCES} ${PLATFORM_SOURCES})
target_link_libraries(AudioApp PRIVATE ${PLATFORM_LIBS})

cmake_minimum_required(VERSION 3.18)
project(AudioFilterEngine CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Shared source files (DSP algorithms, filters, utilities)
set(CORE_SOURCES
    src/LMSAdaptiveFilter.cpp
    src/SingleChannelNoiseFilter.cpp
)

# -----------------------------------------------------------------------------
# Android Platform Target
# -----------------------------------------------------------------------------
if(ANDROID)
    message(STATUS "Configuring for Android (ABI: ${ANDROID_ABI}, API: ${ANDROID_PLATFORM})")
    
    list(APPEND PLATFORM_SOURCES src/android/AndroidMicSearcher.cpp)
    
    # Create shared library (.so) for JNI / Android NDK integration
    add_library(AudioFilterEngine SHARED ${CORE_SOURCES} ${PLATFORM_SOURCES})
    
    # Link native Android logging library
    find_library(log-lib log)
    target_link_libraries(AudioFilterEngine PRIVATE ${log-lib})

# -----------------------------------------------------------------------------
# iOS Platform Target
# -----------------------------------------------------------------------------
elseif(IOS)
    message(STATUS "Configuring for iOS (Arch: ${CMAKE_OSX_ARCHITECTURES})")
    
    # Include Objective-C++ files (.mm) for CoreAudio / AVFoundation
    list(APPEND PLATFORM_SOURCES src/ios/IOSMicSearcher.mm)
    
    # Create static library (.a) or framework for Xcode consumption
    add_library(AudioFilterEngine STATIC ${CORE_SOURCES} ${PLATFORM_SOURCES})
    
    # Link iOS frameworks
    find_library(AVFOUNDATION_FRAMEWORK AVFoundation)
    find_library(AUDIOUNIT_FRAMEWORK AudioUnit)
    
    target_link_libraries(AudioFilterEngine PRIVATE 
        ${AVFOUNDATION_FRAMEWORK} 
        ${AUDIOUNIT_FRAMEWORK}
    )

    # Set Xcode-specific target properties
    set_target_properties(AudioFilterEngine PROPERTIES
        XCODE_ATTRIBUTE_ENABLE_BITCODE "NO"
        XCODE_ATTRIBUTE_CLANG_ENABLE_OBJC_ARC "YES"
    )

else()
    message(FATAL_ERROR "Unsupported platform. Use the Android or iOS toolchain configuration.")
endif()

# Export include directories
target_include_directories(AudioFilterEngine PUBLIC 
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
)

cmake_minimum_required(VERSION 3.18)
project(AudioVideoEngine CXX)

set(CMAKE_CXX_STANDARD 17)

set(CORE_SOURCES
    src/LMSAdaptiveFilter.cpp
    src/SingleChannelNoiseFilter.cpp
)

# -----------------------------------------------------------------------------
# Linux Server Target
# -----------------------------------------------------------------------------
if(CMAKE_SYSTEM_NAME STREQUAL "Linux" AND NOT ANDROID)
    list(APPEND SERVER_SOURCES 
        src/linux/ServerMain.cpp 
        src/linux/LinuxCamera.cpp
    )
    add_executable(media_server ${CORE_SOURCES} ${SERVER_SOURCES})
    find_package(Threads REQUIRED)
    target_link_libraries(media_server PRIVATE Threads::Threads)

# -----------------------------------------------------------------------------
# Android Target
# -----------------------------------------------------------------------------
elseif(ANDROID)
    list(APPEND ANDROID_SOURCES 
        src/android/AndroidMicSearcher.cpp 
        src/android/AndroidCamera.cpp
    )
    add_library(AudioVideoEngine SHARED ${CORE_SOURCES} ${ANDROID_SOURCES})
    
    # Link Android NDK Camera2 & Media libraries
    find_library(camera2ndk-lib camera2ndk)
    find_library(mediandk-lib mediandk)
    find_library(log-lib log)
    
    target_link_libraries(AudioVideoEngine PRIVATE 
        ${camera2ndk-lib} 
        ${mediandk-lib} 
        ${log-lib}
    )

# -----------------------------------------------------------------------------
# iOS Target
# -----------------------------------------------------------------------------
elseif(IOS)
    list(APPEND IOS_SOURCES 
        src/ios/IOSMicSearcher.mm 
        src/ios/IOSCamera.mm
    )
    add_library(AudioVideoEngine STATIC ${CORE_SOURCES} ${IOS_SOURCES})
    
    find_library(AVFOUNDATION_FRAMEWORK AVFoundation)
    find_library(COREMEDIA_FRAMEWORK CoreMedia)
    
    target_link_libraries(AudioVideoEngine PRIVATE 
        ${AVFOUNDATION_FRAMEWORK} 
        ${COREMEDIA_FRAMEWORK}
    )
endif()
