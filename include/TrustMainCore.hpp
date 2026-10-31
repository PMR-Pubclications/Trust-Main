#pragma once

#include <iostream>
#include <filesystem>

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
