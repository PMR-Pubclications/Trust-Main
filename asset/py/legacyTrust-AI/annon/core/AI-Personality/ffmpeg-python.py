import os
import re
import csv
import ffmpeg
from pydub import AudioSegment
from faster_whisper import WhisperModel

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_AUDIO_PATH = "long_recording.mp3"
OUTPUT_DIR = "custom_voice_dataset"
SAMPLE_RATE = 22050
MODEL_SIZE = "base.en"
DEVICE = "cuda"
COMPUTE_TYPE = "float16"

# Audio Clip Constraints
MIN_CLIP_DURATION = 1.0
MAX_CLIP_DURATION = 12.0
PADDING_SEC = 0.08

# Normalization Settings (ffmpeg loudnorm / EBU R128)
TARGET_I = -20.0    # Target Integrated Loudness / RMS level (-20 LUFS)
TARGET_TP = -1.0    # Target Maximum True Peak (-1.0 dBFS)
TARGET_LRA = 7.0    # Target Loudness Range
# ==========================================


def normalize_and_export_clip(clip: AudioSegment, output_path: str, sample_rate: int = 22050):
    """
    Pipes raw PCM audio from pydub through ffmpeg-python to apply 
    EBU R128 RMS/Loudness & True Peak normalization, then exports 16-bit mono WAV.
    """
    raw_pcm = clip.raw_data

    # Define ffmpeg-python pipeline
    stream = (
        ffmpeg
        .input(
            'pipe:', 
            format='s16le', 
            ac=clip.channels, 
            ar=clip.frame_rate
        )
        # loudnorm filter balances RMS/Loudness while capping maximum Peak
        .filter(
            'loudnorm', 
            I=TARGET_I, 
            TP=TARGET_TP, 
            LRA=TARGET_LRA
        )
        .output(
            output_path, 
            ar=sample_rate, 
            ac=1, 
            acodec='pcm_s16le'
        )
        .overwrite_output()
    )

    # Execute ffmpeg process asynchronously via stdin pipe
    process = stream.run_async(pipe_stdin=True, quiet=True)
    process.communicate(input=raw_pcm)


def clean_text_for_tts(text: str) -> str:
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[\[\]\(\)\{\}]', '', text)
    return text


def process_audio_to_piper_dataset():
    if not os.path.exists(INPUT_AUDIO_PATH):
        raise FileNotFoundError(f"Input file not found: {INPUT_AUDIO_PATH}")

    wavs_dir = os.path.join(OUTPUT_DIR, "wavs")
    os.makedirs(wavs_dir, exist_ok=True)
    metadata_path = os.path.join(OUTPUT_DIR, "metadata.csv")

    print(f"Loading audio source: {INPUT_AUDIO_PATH}...")
    audio = AudioSegment.from_file(INPUT_AUDIO_PATH)

    print(f"Initializing Whisper ({MODEL_SIZE} on {DEVICE})...")
    model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)

    segments, _ = model.transcribe(
        INPUT_AUDIO_PATH,
        language="en",
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500, speech_pad_ms=80)
    )

    metadata_entries = []
    clip_counter = 1

    for segment in segments:
        text = clean_text_for_tts(segment.text)
        duration = segment.end - segment.start

        if not text or duration < MIN_CLIP_DURATION or duration > MAX_CLIP_DURATION:
            continue

        start_ms = max(0, int((segment.start - PADDING_SEC) * 1000))
        end_ms = min(len(audio), int((segment.end + PADDING_SEC) * 1000))

        clip = audio[start_ms:end_ms]

        filename_base = f"line_{clip_counter:04d}"
        wav_filepath = os.path.join(wavs_dir, f"{filename_base}.wav")

        # Normalize audio via ffmpeg-python and export to WAV
        normalize_and_export_clip(clip, wav_filepath, sample_rate=SAMPLE_RATE)

        metadata_entries.append((filename_base, text))
        print(f"[{filename_base}] ({duration:.2f}s) Normalized -> {text}")
        clip_counter += 1

    print(f"\nSaving metadata map to {metadata_path}...")
    with open(metadata_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="|")
        writer.writerows(metadata_entries)

    print("Dataset preparation with peak and RMS normalization complete.")


if __name__ == "__main__":
    process_audio_to_piper_dataset()
