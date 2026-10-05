cmake_minimum_required(VERSION 3.14)
project(TrustFirstResponder CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(pybind11 REQUIRED)

include_directories(include)

add_library(flir_boson_static STATIC
    src/flir_boson_wrapper.cpp
)

pybind11_add_module(pyboson
    src/pybind_wrapper.cpp
)

target_link_libraries(pyboson PRIVATE flir_boson_static)
