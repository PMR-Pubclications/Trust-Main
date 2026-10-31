#include <iostream>
#include <thread>
#include <filesystem>
#include <chrono>
#include "TrustMainGateway.h"

namespace fs = std::filesystem;

class TrustMainCore {
public:
    static bool InitializeSecuritySubsystem() {
        fs::path certsDir = fs::current_path() / "certs";
        fs::path clientKey = certsDir / "client.key";
        fs::path clientCsr = certsDir / "client.csr";

        // Verify key and CSR exist within Trust-Main's secure boundary
        if (!fs::exists(clientKey) || !fs::exists(clientCsr)) {
            std::cerr << "[Trust-Main] Error: Missing required identity assets in " << certsDir << "\n";
            return false;
        }

        std::cout << "[Trust-Main] Security subsystem initialized successfully.\n";
        return true;
    }
};

int main() {
    std::cout << "[*] Booting Trust-Main Server & Shield-Sword Engine..." << std::endl;

    // 1. Run the security subsystem check first
    if (!TrustMainCore::InitializeSecuritySubsystem()) {
        std::cerr << "[-] Critical: Security subsystem check failed. Aborting boot sequence." << std::endl;
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
    std::thread listenerThread([&gateway]() {
        gateway.acceptConnection();
    });
    listenerThread.detach();

    // 4. Main processing loop (C++ engine handles ingestion & threat neutralization)
    while (true) {
        // Once the C++ engine cleans/analyzes data, dispatch the lightweight state to Trust-Shell:
        // std::string verifiedState = "{\"status\":\"secure\",\"node\":\"active\"}";
        // gateway.dispatchToTrustMain(verifiedState);

        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }

    return 0;
}
