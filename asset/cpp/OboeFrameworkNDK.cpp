#include <oboe/Oboe.h>
#include <vector>
#include <string>
#include <iostream>

struct PhoneMicrophone {
    int32_t deviceId;
    std::string name;
    int32_t maxChannels;
    oboe::InputPreset inputPreset;
};

class AndroidMicSearcher {
public:
    // Enumerates input devices available to AAudio / OpenSL ES
    static std::vector<PhoneMicrophone> findMicrophones() {
        std::vector<PhoneMicrophone> micList;

        // Create an input stream builder to test hardware capabilities
        oboe::AudioStreamBuilder builder;
        builder.setDirection(oboe::Direction::Input);

        // Define target input presets to check (e.g., Voice Recognition vs Unprocessed for ANC)
        std::vector<oboe::InputPreset> presets = {
            oboe::InputPreset::Unprocessed,       // Raw dual-mic input (best for ANC algorithms)
            oboe::InputPreset::VoiceRecognition,  // Optimized for clear speech
            oboe::InputPreset::Camcorder          // Often selects rear/top mic array
        };

        for (auto preset : presets) {
            builder.setInputPreset(preset);
            
            // Query built-in device characteristics
            PhoneMicrophone mic;
            mic.deviceId = oboe::kUnspecified; // System default or custom ID
            mic.inputPreset = preset;
            mic.maxChannels = 2; // Check for stereo/dual-mic support
            
            if (preset == oboe::InputPreset::Unprocessed) {
                mic.name = "Primary / Raw Microphones (Unprocessed)";
            } else if (preset == oboe::InputPreset::VoiceRecognition) {
                mic.name = "Front / Voice Mic (Beamformed)";
            } else {
                mic.name = "Secondary / Camcorder Noise Mic";
            }

            micList.push_back(mic);
        }

        return micList;
    }

    // Configures Oboe stream to open a specific microphone by ID or Preset
    static oboe::Result openMicrophone(int32_t deviceId, oboe::InputPreset preset) {
        oboe::AudioStreamBuilder builder;
        
        builder.setDirection(oboe::Direction::Input)
               ->setPerformanceMode(oboe::PerformanceMode::LowLatency)
               ->setSharingMode(oboe::SharingMode::Exclusive)
               ->setFormat(oboe::AudioFormat::Float)
               ->setChannelCount(2) // Request stereo for dual-mic processing
               ->setInputPreset(preset);

        if (deviceId != oboe::kUnspecified) {
            builder.setDeviceId(deviceId);
        }

        std::shared_ptr<oboe::AudioStream> stream;
        return builder.openStream(stream);
    }
};
