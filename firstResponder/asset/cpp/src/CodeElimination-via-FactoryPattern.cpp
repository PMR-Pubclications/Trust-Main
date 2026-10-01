#include "Platform.h"
#include <iostream>
#include <memory>

// Abstract Interface
class AudioBackend {
public:
    virtual void initialize() = 0;
    virtual ~AudioBackend() = default;
};

// --- Android Implementation (Eliminated on iOS/Desktop) ---
#if defined(PLATFORM_ANDROID)
#include <oboe/Oboe.h> // Header only compiled on Android

class AndroidBackend : public AudioBackend {
public:
    void initialize() override {
        std::cout << "Starting " << OS_NAME << " Oboe Audio Engine...\n";
    }
};
#endif

// --- iOS Implementation (Eliminated on Android/Desktop) ---
#if defined(PLATFORM_IOS)
class IOSBackend : public AudioBackend {
public:
    void initialize() override {
        std::cout << "Starting " << OS_NAME << " CoreAudio Engine...\n";
    }
};
#endif

// --- Startup OS Discovery & Factory ---
class AudioBackendFactory {
public:
    static std::unique_ptr<AudioBackend> createForCurrentOS() {
        std::cout << "[Startup] Detected Operating System: " << OS_NAME << std::endl;

#if defined(PLATFORM_ANDROID)
        return std::make_unique<AndroidBackend>();
#elif defined(PLATFORM_IOS)
        return std::make_unique<IOSBackend>();
#else
        std::cerr << "No audio backend available for this platform." << std::endl;
        return nullptr;
#endif
    }
};

int main() {
    // Discovers platform and instantiates only the active OS driver
    auto backend = AudioBackendFactory::createForCurrentOS();
    if (backend) {
        backend->initialize();
    }
    return 0;
}
