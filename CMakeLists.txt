cmake_minimum_required(VERSION 3.20)
project(TrustMainServer)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include AudioVideoEngine-CPP headers and source targets
add_subdirectory(vendor/AudioVideoEngine)

# Main server executable containing the gateway socket loop
add_executable(trust_main_server 
    src/main.cpp 
    src/TrustMainGateway.cpp
)

# Link the high-performance C++ engine libraries

add_subdirectory(vendor/AudioVideoEngine-CPP)
target_link_libraries(trust_main_server PRIVATE AudioVideoEngineCore)

target_link_libraries(trust_main_server PRIVATE AudioVideoEngineCore)
