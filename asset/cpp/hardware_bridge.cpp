#include <napi.h>
#include <chrono>
#include <thread>

// Simulated C++ thermal sensor capture routine
float GetThermalSensorReadout() {
    // Low-level hardware read (e.g., I2C, SPI, or V4L2 video device)
    return 36.6f; // Temperature in Celsius
}

// 1. C++ function exposed to JavaScript
Napi::Value GetTemperature(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    
    // Read from C++ hardware layer
    float temp = GetThermalSensorReadout();
    
    // Return result directly to JavaScript as a Number
    return Napi::Number::New(env, temp);
}

// 2. C++ function returning raw frame/thermal buffer memory
Napi::Value CaptureThermalFrame(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    
    // Simulated thermal frame buffer size (e.g., 80x60 thermal matrix = 4800 floats)
    size_t bufferSize = 4800 * sizeof(float);
    float* frameData = (float*)malloc(bufferSize);

    // Populate frameData with raw sensor values...

    // Wrap raw memory buffer directly into a JavaScript ArrayBuffer (Zero-Copy)
    return Napi::ArrayBuffer::New(env, frameData, bufferSize, [](Napi::Env env, void* finalizeData) {
        free(finalizeData); // Clean up memory when JS garbage collects
    });
}

// Register Module Functions for Node.js N-API
Napi::Object Init(Napi::Env env, Napi::Object exports) {
    exports.Set(Napi::String::New(env, "getTemperature"), Napi::Function::New(env, GetTemperature));
    exports.Set(Napi::String::New(env, "captureThermalFrame"), Napi::Function::New(env, CaptureThermalFrame));
    return exports;
}

NODE_API_MODULE(hardware_bridge, Init)
