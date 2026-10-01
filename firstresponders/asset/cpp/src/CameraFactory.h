#pragma once
#include "Platform.h"
#include "CameraInterface.h"
#include <memory>

class CameraFactory {
public:
    static std::unique_ptr<CameraBackend> createForCurrentOS() {
#if defined(PLATFORM_ANDROID)
        return std::make_unique<AndroidCameraBackend>();
#elif defined(PLATFORM_IOS)
        return std::make_unique<IOSCameraBackend>();
#elif defined(PLATFORM_LINUX)
        return std::make_unique<LinuxCameraBackend>();
#else
        return nullptr;
#endif
    }
};
