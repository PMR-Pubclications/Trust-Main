#include <iostream>
#include <thread>
#include <chrono>
#include <filesystem>
#include "TrustMainGateway.h"
#include "TrustMainCore.hpp" // Pulls in your independent security subsystem check

int main() {
    std::cout << "[*] Booting Trust-Main Server & Shield-Sword Engine..." << std::endl;

    // 1. Mandatory Security Subsystem Check (Executes first before binding ports)
    if (!TrustMainCore::InitializeSecuritySubsystem()) {
        std::cerr << "[-] Critical: Security subsystem check failed. Missing required identity assets. Aborting boot." << std::endl;
        return 1;
    }

    // 2. Initialize the C++ Gateway on your designated secure port
    int securePort = 8443;
    TrustMainGateway gateway(securePort);
    
    if (!gateway.initialize()) {
        std::cerr << "[-] Critical: Failed to bind Trust-Main gateway port." << std::endl;
        return 1;
    }

    // 3. Start connection acceptance listener in a background thread 
    // (Maintains active communication pipeline with AudioVideoEngine-CPP)
    std::thread listenerThread([&gateway]() {
        gateway.acceptConnection();
    });
    listenerThread.detach();

    std::cout << "[+] Trust-Main active and listening for AudioVideoEngine-CPP connections on port " << securePort << "..." << std::endl;

    // 4. Main processing loop (Handles incoming data, state updates, and engine synchronization)
    while (true) {
        // Your established back-and-forth engine ingestion and dispatch logic runs here:
        // std::string verifiedState = gateway.pollEngineState();
        // gateway.dispatchToTrustShell(verifiedState);

        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }

    return 0;
}
