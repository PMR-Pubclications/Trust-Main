import os
import re
import csv
from pydub import AudioSegment
from faster_whisper import WhisperModel

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_AUDIO_PATH = "long_recording.mp3"  # Works with .wav, .mp3, .m4a, .flac, etc.
OUTPUT_DIR = "custom_voice_dataset"
SAMPLE_RATE = 22050                     # Standard Piper TTS sample rate
MODEL_SIZE = "base.en"                  # Options: 'tiny.en', 'base.en', 'small.en', 'medium.en'
DEVICE = "cuda"                         # Set to "cpu" if running without NVIDIA GPU
COMPUTE_TYPE = "float16"                # Use "int8" for CPU

# Minimum/maximum duration (in seconds) for Piper clips
MIN_CLIP_DURATION = 1.0
MAX_CLIP_DURATION = 12.0
# Padding (in seconds) added around each slice to avoid clipping initial/final consonants
PADDING_SEC = 0.08
# ==========================================


def clean_text_for_tts(text: str) -> str:
    """Cleans up raw transcription text for TTS training."""
    text = text.strip()
    # Replace multiple spaces/newlines with single spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove uncommon non-printable characters or unusual brackets
    text = re.sub(r'[\[\]\(\)\{\}]', '', text)
    return text


def process_audio_to_piper_dataset():
    if not os.path.exists(INPUT_AUDIO_PATH):
        raise FileNotFoundError(f"Input audio file not found: {INPUT_AUDIO_PATH}")

    wavs_dir = os.path.join(OUTPUT_DIR, "wavs")
    os.makedirs(wavs_dir, exist_ok=True)
    metadata_path = os.path.join(OUTPUT_DIR, "metadata.csv")

    print(f"Loading source audio file: {INPUT_AUDIO_PATH}...")
    audio = AudioSegment.from_file(INPUT_AUDIO_PATH)
    audio_duration_sec = len(audio) / 1000.0

    print(f"Loading Whisper model ('{MODEL_SIZE}' on {DEVICE})...")
    model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)

    print("Transcribing and segmenting on voice activity (VAD)...")
    segments, info = model.transcribe(
        INPUT_AUDIO_PATH,
        language="en",
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=500,  # Split if pause is >= 500ms
            speech_pad_ms=80
        )
    )

    metadata_entries = []
    clip_counter = 1

    for segment in segments:
        text = clean_text_for_tts(segment.text)
        duration = segment.end - segment.start

        # Filter out empty strings, too short clips, or overly long clips
        if not text or duration < MIN_CLIP_DURATION or duration > MAX_CLIP_DURATION:
            continue

        # Calculate padded start/end timestamps in milliseconds
        start_ms = max(0, int((segment.start - PADDING_SEC) * 1000))
        end_ms = min(len(audio), int((segment.end + PADDING_SEC) * 1000))

        # Slice the audio segment
        clip = audio[start_ms:end_ms]

        # Convert audio properties to Piper standards (22050Hz, 16-bit PCM, Mono)
        clip = clip.set_frame_rate(SAMPLE_RATE).set_channels(1).set_sample_width(2)

        # Export audio clip
        filename_base = f"line_{clip_counter:04d}"
        wav_filename = f"{filename_base}.wav"
        wav_filepath = os.path.join(wavs_dir, wav_filename)

        clip.export(wav_filepath, format="wav")

        # Save metadata entry (line_0001|Transcribed text)
        metadata_entries.append((filename_base, text))
        
        print(f"[{filename_base}] ({duration:.2f}s): {text}")
        clip_counter += 1

    # Write pipe-separated metadata.csv
    print(f"\nWriting {len(metadata_entries)} dataset entries to {metadata_path}...")
    with open(metadata_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="|")
        writer.writerows(metadata_entries)

    print("Dataset extraction complete!")
    print(f"Output folder structure:\n  • Clips: {wavs_dir}/\n  • Map: {metadata_path}")


if __name__ == "__main__":
    process_audio_to_piper_dataset()
