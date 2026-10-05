cmake_minimum_required(VERSION 3.14)
project(TrustFirstResponder CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 1. Fetch or Link PMR-Publications/AudioVideoEngine-CPP
include(FetchContent)
FetchContent_Declare(
    AudioVideoEngine
    GIT_REPOSITORY https://github.com/PMR-Pubclications/AudioVideoEngine-CPP.git
    GIT_TAG        main
)
FetchContent_MakeAvailable(AudioVideoEngine)

# 2. Pybind11 Setup for Python C++ API
find_package(pybind11 REQUIRED)

include_directories(
    include
    ${audiovideoengine_SOURCE_DIR}/include
)

# 3. Flir Boson Radiometric Hardware Wrapper Library
add_library(flir_boson_static STATIC
    src/flir_boson_wrapper.cpp
)

# Link against the underlying AudioVideoEngine target
target_link_libraries(flir_boson_static PRIVATE AudioVideoEngine)

# 4. Pybind11 Native Module
pybind11_add_module(pyboson
    src/pybind_wrapper.cpp
)

target_link_libraries(pyboson PRIVATE flir_boson_static AudioVideoEngine)
