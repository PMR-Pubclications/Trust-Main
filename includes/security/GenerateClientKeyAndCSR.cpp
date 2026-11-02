#include <openssl/evp.h>
#include <openssl/rsa.h>
#include <openssl/pem.h>
#include <openssl/x509.h>
#include <iostream>
#include <fstream>
#include <filesystem>

class TrustIdentityManager {
public:
    struct IdentityConfig {
        std::string keyPath;
        std::string csrPath;
        std::string commonName;
    };

    // Generates client identity assets under Trust's secure control
    static bool ProvisionClientIdentity(const IdentityConfig& config) {
        // Ensure secure storage directory exists
        std::filesystem::path p(config.keyPath);
        if (p.has_parent_path()) {
            std::filesystem::create_directories(p.parent_path());
        }

        // 1. Generate 2048-bit RSA Private Key
        EVP_PKEY_CTX* ctx = EVP_PKEY_CTX_new_id(EVP_PKEY_RSA, nullptr);
        if (!ctx) return false;

        if (EVP_PKEY_keygen_init(ctx) <= 0 || EVP_PKEY_CTX_set_rsa_keygen_bits(ctx, 2048) <= 0) {
            EVP_PKEY_CTX_free(ctx);
            return false;
        }

        EVP_PKEY* pkey = nullptr;
        if (EVP_PKEY_keygen(ctx, &pkey) <= 0) {
            EVP_PKEY_CTX_free(ctx);
            return false;
        }
        EVP_PKEY_CTX_free(ctx);

        // 2. Write Private Key securely (restricted permissions)
        FILE* keyFile = fopen(config.keyPath.c_str(), "wb");
        if (!keyFile) {
            EVP_PKEY_free(pkey);
            return false;
        }
        // Set restrictive file permissions on POSIX systems (0600)
        #ifndef _WIN32
        int fd = fileno(keyFile);
        fchmod(fd, 0600);
        #endif

        PEM_write_PrivateKey(keyFile, pkey, nullptr, nullptr, 0, nullptr, nullptr);
        fclose(keyFile);

        // 3. Generate Certificate Signing Request (CSR)
        X509_REQ* req = X509_REQ_new();
        X509_REQ_set_version(req, 0);

        X509_NAME* name = X509_REQ_get_subject_name(req);
        X509_NAME_add_entry_by_txt(name, "CN", MBSTRING_ASC, 
                                   (unsigned char*)config.commonName.c_str(), -1, -1, 0);
        X509_REQ_set_pubkey(req, pkey);
        X509_REQ_sign(req, pkey, EVP_sha256());

        // 4. Output CSR for internal CA signing
        FILE* csrFile = fopen(config.csrPath.c_str(), "wb");
        if (!csrFile) {
            X509_REQ_free(req);
            EVP_PKEY_free(pkey);
            return false;
        }
        PEM_write_X509_REQ(csrFile, req);
        fclose(csrFile);

        // Cleanup
        X509_REQ_free(req);
        EVP_PKEY_free(pkey);
        
        std::cout << "[Trust-Shell] Provisioned identity successfully for: " << config.commonName << std::endl;
        return true;
    }
};
