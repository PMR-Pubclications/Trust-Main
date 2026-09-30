#if defined(PLATFORM_IOS)
#include "CameraInterface.h"
#import <AVFoundation/AVFoundation.h>
#include <iostream>

class IOSCameraBackend : public CameraBackend {
public:
    std::vector<CameraInfo> findCameras() override {
        std::vector<CameraInfo> cameras;

        NSArray<AVCaptureDeviceType>* deviceTypes = @[
            AVCaptureDeviceTypeBuiltInWideAngleCamera,
            AVCaptureDeviceTypeBuiltInUltraWideCamera,
            AVCaptureDeviceTypeBuiltInTelephotoCamera
        ];

        AVCaptureDeviceDiscoverySession* session = [AVCaptureDeviceDiscoverySession
            discoverySessionWithDeviceTypes:deviceTypes
                                  mediaType:AVMediaTypeVideo
                                   position:AVCaptureDevicePositionUnspecified];

        for (AVCaptureDevice* device in session.devices) {
            CameraInfo info;
            info.id = [device.uniqueID UTF8String];
            info.name = [device.localizedName UTF8String];

            if (device.position == AVCaptureDevicePositionFront) {
                info.facing = LensFacing::Front;
            } else if (device.position == AVCaptureDevicePositionBack) {
                info.facing = LensFacing::Back;
            } else {
                info.facing = LensFacing::External;
            }

            cameras.push_back(info);
        }
        return cameras;
    }

    bool openCamera(const std::string& cameraId) override {
        std::cout << "[iOS Camera] Opening AVCaptureDevice ID: " << cameraId << std::endl;
        return true;
    }
};
#endif
