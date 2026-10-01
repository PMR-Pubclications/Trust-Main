#include <vector>
#include <cmath>
#include <algorithm>

class SingleChannelNoiseFilter {
private:
    double sample_rate;
    double noise_floor_estimate;
    double alpha_attack;
    double alpha_release;
    double threshold_db;
    double reduction_ratio;

public:
    SingleChannelNoiseFilter(double sample_rate_hz = 44100.0, 
                             double threshold_db = -30.0, 
                             double reduction_db = -12.0)
        : sample_rate(sample_rate_hz), 
          noise_floor_estimate(0.001), 
          threshold_db(threshold_db) {
        
        // Attack time: 10ms, Release time: 100ms
        alpha_attack = std::exp(-1.0 / (0.010 * sample_rate));
        alpha_release = std::exp(-1.0 / (0.100 * sample_rate));
        reduction_ratio = std::pow(10.0, reduction_db / 20.0);
    }

    double process_sample(double input_sample) {
        double abs_sample = std::abs(input_sample);

        // Smooth energy envelope tracking
        if (abs_sample > noise_floor_estimate) {
            noise_floor_estimate = alpha_attack * noise_floor_estimate + (1.0 - alpha_attack) * abs_sample;
        } else {
            noise_floor_estimate = alpha_release * noise_floor_estimate + (1.0 - alpha_release) * abs_sample;
        }

        // Convert current energy estimate to dB FS
        double current_db = 20.0 * std::log10(noise_floor_estimate + 1e-6);

        // Apply dynamic gain reduction if signal drops below speech threshold
        double gain = 1.0;
        if (current_db < threshold_db) {
            double att_factor = (threshold_db - current_db) / 20.0;
            gain = std::max(reduction_ratio, std::pow(10.0, -att_factor));
        }

        return input_sample * gain;
    }
};
