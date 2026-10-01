#if defined(PLATFORM_ANDROID)
#include "CameraInterface.h"
#include <camera/NCameraManager.h>
#include <camera/NCameraMetadata.h>
#include <camera/NCameraDevice.h>
#include <vector>
#include <iostream>

class AndroidCameraBackend : public CameraBackend {
public:
    std::vector<CameraInfo> findCameras() override {
        std::vector<CameraInfo> cameras;
        ACameraManager* cameraManager = ACameraManager_create();
        ACameraIdList* cameraIdList = nullptr;

        if (ACameraManager_getCameraIdList(cameraManager, &cameraIdList) == ACAMERA_OK) {
            for (int i = 0; i < cameraIdList->numCameras; ++i) {
                const char* id = cameraIdList->cameraIds[i];
                ACameraMetadata* metadata = nullptr;
                
                if (ACameraManager_getCameraCharacteristics(cameraManager, id, &metadata) == ACAMERA_OK) {
                    CameraInfo info;
                    info.id = id;
                    info.name = "Android Camera " + std::string(id);

                    // Query camera orientation (Front vs Back)
                    ACameraMetadata_const_entry facingEntry;
                    if (ACameraMetadata_getConstEntry(metadata, ACAMERA_LENS_FACING, &facingEntry) == ACAMERA_OK) {
                        auto facing = static_cast<acamera_metadata_enum_android_lens_facing_t>(facingEntry.data.u8[0]);
                        info.facing = (facing == ACAMERA_LENS_FACING_FRONT) ? LensFacing::Front : LensFacing::Back;
                    }

                    cameras.push_back(info);
                    ACameraMetadata_free(metadata);
                }
            }
            ACameraManager_deleteCameraIdList(cameraIdList);
        }
        ACameraManager_delete(cameraManager);
        return cameras;
    }

    bool openCamera(const std::string& cameraId) override {
        std::cout << "[Android Camera] Opening Native Camera ID: " << cameraId << std::endl;
        return true;
    }
};
#endif
