import os
import ffmpeg
from pydub import AudioSegment

# ==========================================
# NOISE REDUCTION & NORMALIZATION CONFIG
# ==========================================
# Audio Filtering Settings
HIGHPASS_FREQ = 80       # Cut sub-bass frequencies below 80 Hz (HVAC hum, desk thumps)
AFFTDN_NOISE_REDUCE = 12 # Noise reduction in dB (10-15 dB avoids robotic phase artifacts)
AFFTDN_NOISE_FLOOR = -50 # Target noise floor in dB
TRACK_NOISE = 1          # 1 = Adaptive noise floor tracking during speech pauses

# Normalization Settings (EBU R128)
TARGET_I = -20.0         # Integrated Loudness (RMS target)
TARGET_TP = -1.0         # True Peak limit (dBFS)
TARGET_LRA = 7.0         # Loudness Range
# ==========================================


def denoise_and_normalize_clip(
    clip: AudioSegment, 
    output_path: str, 
    sample_rate: int = 22050,
    rnnoise_model_path: str = None
):
    """
    Pipes raw PCM audio from pydub through ffmpeg-python filter chain:
    1. Highpass filter (cuts low rumble)
    2. afftdn (FFT noise reduction) OR arnndn (RNNoise neural filter)
    3. loudnorm (EBU R128 RMS / Peak normalization)
    """
    raw_pcm = clip.raw_data

    # Step 1: Initialize raw PCM input
    stream = ffmpeg.input(
        'pipe:', 
        format='s16le', 
        ac=clip.channels, 
        ar=clip.frame_rate
    )

    # Step 2: Strip sub-bass rumble (<80 Hz)
    stream = stream.filter('highpass', f=HIGHPASS_FREQ)

    # Step 3: Denoise Filter Selection
    if rnnoise_model_path and os.path.exists(rnnoise_model_path):
        # RNNoise Neural Denoiser (requires FFmpeg built with --enable-librnnoise)
        stream = stream.filter('arnndn', m=rnnoise_model_path)
    else:
        # Native Adaptive FFT Noise Reduction (Built-in to all FFmpeg builds)
        stream = stream.filter(
            'afftdn',
            nr=AFFTDN_NOISE_REDUCE,
            nf=AFFTDN_NOISE_FLOOR,
            tn=TRACK_NOISE
        )

    # Step 4: Loudness & True Peak Normalization
    stream = stream.filter(
        'loudnorm',
        I=TARGET_I,
        TP=TARGET_TP,
        LRA=TARGET_LRA
    )

    # Step 5: Export to 16-bit mono WAV
    stream = stream.output(
        output_path, 
        ar=sample_rate, 
        ac=1, 
        acodec='pcm_s16le'
    ).overwrite_output()

    process = stream.run_async(pipe_stdin=True, quiet=True)
    process.communicate(input=raw_pcm)
