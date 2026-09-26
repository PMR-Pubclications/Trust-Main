#include <camera/NdkCameraManager.h>
#include <camera/NdkCameraDevice.h>
#include <camera/NdkCameraError.h>
#include <android/log.h>

#define LOG_TAG "TrustfenceNativeCamera"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

// Camera device state callback listeners
static ACameraDevice_stateCallbacks deviceCallbacks = {
    .context = nullptr,
    .onDisconnected = [](void* context, ACameraDevice* device) {
        LOGI("Camera device disconnected.");
    },
    .onError = [](void* context, ACameraDevice* device, int error) {
        LOGE("Camera device error encountered: %d", error);
    }
};

void initAndOpenNativeCamera() {
    // 1. Create the native Camera Manager instance
    ACameraManager* cameraManager = ACameraManager_create();
    if (!cameraManager) {
        LOGE("Failed to initialize ACameraManager.");
        return;
    }

    // 2. Enumerate available hardware camera IDs
    ACameraIdList* cameraIdList = nullptr;
    binder_status_t status = ACameraManager_getCameraIdList(cameraManager, &cameraIdList);
    if (status != ACAMERA_OK || cameraIdList == nullptr) {
        LOGE("Failed to retrieve camera ID list. Status: %d", status);
        ACameraManager_delete(cameraManager);
        return;
    }

    LOGI("Detected %d physical camera(s) on device.", cameraIdList->numCameras);

    // 3. Open the primary camera device (index 0)
    if (cameraIdList->numCameras > 0) {
        const char* targetCameraId = cameraIdList->cameraIds[0];
        LOGI("Attempting to open camera ID: %s", targetCameraId);

        ACameraDevice* cameraDevice = nullptr;
        status = ACameraManager_openCamera(cameraManager, targetCameraId, &deviceCallbacks, &cameraDevice);

        if (status == ACAMERA_OK && cameraDevice) {
            LOGI("Successfully bound to native camera device.");
            
            // [Next Step]: Configure capture session, assign surface outputs,
            // or route raw image buffers into a secure local processing pipeline.

            // Clean up device handle when finished
            // ACameraDevice_close(cameraDevice);
        } else {
            LOGE("Failed to open target camera. Status code: %d", status);
        }
    }

    // 4. Release manager memory allocations
    ACameraManager_deleteCameraIdList(cameraIdList);
    ACameraManager_delete(cameraManager);
}
