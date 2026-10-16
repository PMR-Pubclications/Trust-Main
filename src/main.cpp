#include <iostream>
#include <thread>
#include "TrustMainGateway.h"

int main() {
    std::cout << "[*] Booting Trust-Main Server & Shield-Sword Engine..." << std::endl;

    // 1. Initialize the C++ Gateway on your designated secure port
    int securePort = 8443;
    TrustMainGateway gateway(securePort);
    
    if (!gateway.initialize()) {
        std::cerr << "[-] Critical: Failed to bind Trust-Main gateway port." << std::endl;
        return 1;
    }

    // 2. Start connection acceptance listener in a background thread
    std::thread listenerThread([&gateway]() {
        gateway.acceptConnection();
    });
    listenerThread.detach();

    // 3. Main processing loop (C++ engine handles ingestion & threat neutralization)
    while (true) {
        // Once the C++ engine cleans/analyzes data, dispatch the lightweight state to Trust-Shell:
        // std::string verifiedState = "{\"status\":\"secure\",\"node\":\"active\"}";
        // gateway.dispatchToTrustMain(verifiedState);

        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }

    return 0;
}
