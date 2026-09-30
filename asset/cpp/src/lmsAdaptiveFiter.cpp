#include <vector>
#include <cmath>
#include <iostream>
#include <algorithm>

class LMSAdaptiveFilter {
private:
    size_t filter_taps;
    double mu; // Learning rate (step size)
    std::vector<double> weights;
    std::vector<double> buffer;

public:
    LMSAdaptiveFilter(size_t taps = 64, double learning_rate = 0.01)
        : filter_taps(taps), mu(learning_rate), weights(taps, 0.0), buffer(taps, 0.0) {}

    // Processes a single audio frame sample
    // primary_mic (d): Desired speech + background noise
    // reference_mic (x): Ambient background noise captured near earbud exterior
    double process_sample(double primary_mic, double reference_mic) {
        // Shift delay line buffer
        for (size_t i = filter_taps - 1; i > 0; --i) {
            buffer[i] = buffer[i - 1];
        }
        buffer[0] = reference_mic;

        // Estimate current noise sample y_hat = w^T * x
        double estimated_noise = 0.0;
        for (size_t i = 0; i < filter_taps; ++i) {
            estimated_noise += weights[i] * buffer[i];
        }

        // Subtract noise from primary signal to get clean audio error e[n]
        double clean_output = primary_mic - estimated_noise;

        // Update weights via Gradient Descent: w[n+1] = w[n] + 2 * mu * e[n] * x[n]
        for (size_t i = 0; i < filter_taps; ++i) {
            weights[i] += 2.0 * mu * clean_output * buffer[i];
            
            // Weight clipping to prevent gradient explosion
            weights[i] = std::clamp(weights[i], -2.0, 2.0);
        }

        return clean_output;
    }

    // Process full block/buffer of PCM float audio
    void process_block(const std::vector<double>& primary, 
                       const std::vector<double>& reference, 
                       std::vector<double>& output) {
        output.resize(primary.size());
        for (size_t i = 0; i < primary.size(); ++i) {
            output[i] = process_sample(primary[i], reference[i]);
        }
    }
};
