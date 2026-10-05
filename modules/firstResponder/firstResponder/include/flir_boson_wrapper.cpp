#pragma once

#include <vector>
#include <cstdint>
#include <string>
#include <memory>

// Import core stream definitions from AudioVideoEngine-CPP
#include "AudioVideoEngine/VideoStream.hpp"
#include "AudioVideoEngine/FrameBuffer.hpp"

namespace Trust::FirstResponder {

struct ThermalFrame {
    uint32_t width;
    uint32_t height;
    std::vector<float> data_celsius; // Radiometric values converted to Deg C
    uint64_t timestamp_ns;
};

class FlirBosonCamera {
public:
    FlirBosonCamera(const std::string& device_path = "/dev/video0");
    ~FlirBosonCamera();

    bool initialize();
    bool capture_frame(ThermalFrame& out_frame);
    void close();

private:
    std::string device_path_;
    bool is_initialized_ = false;

    // AudioVideoEngine C++ core pipeline instance
    std::unique_ptr<AudioVideoEngine::VideoStream> video_engine_;

    inline float raw_to_celsius(uint16_t raw_val) const {
        // High-Gain Radiometric Conversion (0.01K per LSB)
        return (static_cast<float>(raw_val) * 0.01f) - 273.15f;
    }
};

} // namespace Trust::FirstResponder
