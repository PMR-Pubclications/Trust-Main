cmake_minimum_required(VERSION 3.18)
project(AudioVideoEngine LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

add_executable(audio_video_engine
    src/CodeElimination-via-FactoryPattern.cpp
    src/lmsAdaptiveFiter.cpp
    src/Single-MicrophoneSpectralNoiseSuppressor.cpp
    linux/LinuxCamera.cpp
)

target_compile_definitions(audio_video_engine PRIVATE PLATFORM_LINUX)
target_include_directories(audio_video_engine PRIVATE include src)

find_package(Threads REQUIRED)
target_link_libraries(audio_video_engine PRIVATE Threads::Threads)
