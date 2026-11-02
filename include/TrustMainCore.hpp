#pragma once

#include <iostream>
#include <filesystem>
#include "SystemTransparency.hpp"

namespace fs = std::filesystem;

class TrustMainCore {
public:
    static bool InitializeSecuritySubsystem() {
        // Run environment transparency audit first
        SystemTransparency::AuditEnvironmentContext();

        fs::path certsDir = fs::current_path() / "certs";
        fs::path clientKey = certsDir / "client.key";
        fs::path clientCsr = certsDir / "client.csr";
        fs::path localCa   = certsDir / "localCA.crt";

        // Verify all required identity and verification assets exist within the secure boundary
        if (!fs::exists(clientKey) || !fs::exists(clientCsr) || !fs::exists(localCa)) {
            SystemTransparency::LogEvent(
                "Trust-Main", 
                "Asset Audit", 
                SystemTransparency::StatusLevel::CRITICAL, 
                "Missing required identity assets (key, CSR, or Root CA) in " + certsDir.string()
            );
            return false;
        }

        SystemTransparency::LogEvent(
            "Trust-Main", 
            "Asset Audit", 
            SystemTransparency::StatusLevel::PASS, 
            "All mTLS identity assets verified in " + certsDir.string()
        );
        return true;
    }
};
