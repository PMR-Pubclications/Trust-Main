#pragma once
#include <string>
#include <vector>
#include <memory>

enum class LensFacing { Front, Back, External, Unknown };

struct CameraInfo {
    std::string id;
    std::string name;
    LensFacing facing;
    int maxWidth;
    int maxHeight;
    int maxFPS;
};

class CameraBackend {
public:
    virtual ~CameraBackend() = default;
    virtual std::vector<CameraInfo> findCameras() = 0;
    virtual bool openCamera(const std::string& cameraId) = 0;
};
