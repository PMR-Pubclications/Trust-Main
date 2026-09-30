#if defined(PLATFORM_LINUX) && !defined(PLATFORM_ANDROID)
#include "CameraInterface.h"
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/videodev2.h>
#include <iostream>
#include <filesystem>

class LinuxCameraBackend : public CameraBackend {
public:
    std::vector<CameraInfo> findCameras() override {
        std::vector<CameraInfo> cameras;

        // Iterate through system video nodes (/dev/video0, /dev/video1, etc.)
        for (int i = 0; i < 16; ++i) {
            std::string devicePath = "/dev/video" + std::to_string(i);
            if (!std::filesystem::exists(devicePath)) continue;

            int fd = open(devicePath.c_str(), O_RDWR | O_NONBLOCK, 0);
            if (fd < 0) continue;

            struct v4l2_capability cap;
            if (ioctl(fd, VIDIOC_QUERYCAP, &cap) == 0) {
                // Ensure device supports video capture (and not raw radio/vbi)
                if (cap.device_caps & V4L2_CAP_VIDEO_CAPTURE) {
                    CameraInfo info;
                    info.id = devicePath;
                    info.name = reinterpret_cast<char*>(cap.card);
                    info.facing = LensFacing::External;
                    cameras.push_back(info);
                }
            }
            close(fd);
        }
        return cameras;
    }

    bool openCamera(const std::string& cameraId) override {
        std::cout << "[Linux Server] Initializing V4L2 Device: " << cameraId << std::endl;
        return true;
    }
};
#endif
