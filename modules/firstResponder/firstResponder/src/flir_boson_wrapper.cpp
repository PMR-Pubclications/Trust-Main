#include "flir_boson_wrapper.hpp"
#include <iostream>

namespace Trust::FirstResponder {

FlirBosonCamera::FlirBosonCamera(const std::string& device_path)
    : device_path_(device_path) {}

FlirBosonCamera::~FlirBosonCamera() {
    close();
}

bool FlirBosonCamera::initialize() {
    // Instantiate stream pipeline using AudioVideoEngine-CPP
    video_engine_ = std::make_unique<AudioVideoEngine::VideoStream>();

    AudioVideoEngine::StreamConfig config;
    config.device_path = device_path_;
    config.width = 640;
    config.height = 512;
    config.pixel_format = AudioVideoEngine::PixelFormat::Y16_RADIOMETRIC;
    config.fps = 30;

    if (!video_engine_->OpenStream(config)) {
        std::cerr << "[FLIR_BOSON] AudioVideoEngine failed to initialize device: " << device_path_ << std::endl;
        return false;
    }

    is_initialized_ = true;
    return true;
}

bool FlirBosonCamera::capture_frame(ThermalFrame& out_frame) {
    if (!is_initialized_ || !video_engine_) return false;

    AudioVideoEngine::RawFrame raw_frame;
    if (!video_engine_->ReadFrame(raw_frame)) {
        return false; // Frame dropped or stream buffered
    }

    out_frame.width = raw_frame.width;
    out_frame.height = raw_frame.height;
    out_frame.timestamp_ns = raw_frame.timestamp_ns;

    size_t total_pixels = out_frame.width * out_frame.height;
    out_frame.data_celsius.resize(total_pixels);

    const uint16_t* raw_buffer = reinterpret_cast<const uint16_t*>(raw_frame.data_buffer.data());

    // Convert 16-bit raw counts to float degrees Celsius
    for (size_t i = 0; i < total_pixels; ++i) {
        out_frame.data_celsius[i] = raw_to_celsius(raw_buffer[i]);
    }

    return true;
}

void FlirBosonCamera::close() {
    if (video_engine_) {
        video_engine_->CloseStream();
        video_engine_.reset();
    }
    is_initialized_ = false;
}

} // namespace Trust::FirstResponder
