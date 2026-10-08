cmake_minimum_required(VERSION 3.18)
project(AudioVideoEngine LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(CORE_SOURCES src/lmsAdaptiveFiter.cpp)

if(ANDROID)
    add_library(audio_video_engine SHARED
        ${CORE_SOURCES}
        android/AndroidCamera.cpp
    )
    target_compile_definitions(audio_video_engine PRIVATE PLATFORM_ANDROID)

    find_library(camera2ndk-lib camera2ndk)
    find_library(log-lib log)
    target_link_libraries(audio_video_engine PRIVATE ${camera2ndk-lib} ${log-lib})
elseif(IOS)
    enable_language(OBJCXX)
    add_library(audio_video_engine STATIC
        ${CORE_SOURCES}
        ios/IOSCamera.mm
    )
    target_compile_definitions(audio_video_engine PRIVATE PLATFORM_IOS)

    find_library(AVFOUNDATION_FRAMEWORK AVFoundation)
    target_link_libraries(audio_video_engine PRIVATE ${AVFOUNDATION_FRAMEWORK})
else()
    add_library(audio_video_engine STATIC
        ${CORE_SOURCES}
        linux/LinuxCamera.cpp
    )
    target_compile_definitions(audio_video_engine PRIVATE PLATFORM_LINUX)
endif()

target_include_directories(audio_video_engine PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
)
