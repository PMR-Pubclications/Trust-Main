"""Turns a long recording into a Piper dataset (wavs/ + pipe-separated metadata.csv)."""
import csv
import os

import config
from audio_utils import clean_text_for_tts, normalize_clip


def process_audio_to_piper_dataset(
    input_audio_path: str = config.INPUT_AUDIO_PATH,
    output_dir: str = config.OUTPUT_DIR,
    normalize: bool = True,
    denoise: bool = False,
):
    """With normalize=False clips are only resampled (no ffmpeg loudnorm)."""
    if not os.path.exists(input_audio_path):
        raise FileNotFoundError(f"Input audio file not found: {input_audio_path}")

    from pydub import AudioSegment
    from faster_whisper import WhisperModel

    wavs_dir = os.path.join(output_dir, "wavs")
    os.makedirs(wavs_dir, exist_ok=True)
    metadata_path = os.path.join(output_dir, "metadata.csv")

    print(f"Loading source audio file: {input_audio_path}...")
    audio = AudioSegment.from_file(input_audio_path)

    print(f"Loading Whisper model ('{config.WHISPER_MODEL_SIZE}' on {config.WHISPER_DEVICE})...")
    model = WhisperModel(
        config.WHISPER_MODEL_SIZE, device=config.WHISPER_DEVICE, compute_type=config.WHISPER_COMPUTE_TYPE
    )

    print("Transcribing and segmenting on voice activity (VAD)...")
    segments, _ = model.transcribe(
        input_audio_path,
        language="en",
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500, speech_pad_ms=80),
    )

    entries = []
    counter = 1
    for segment in segments:
        text = clean_text_for_tts(segment.text)
        duration = segment.end - segment.start
        if not text or duration < config.MIN_CLIP_DURATION or duration > config.MAX_CLIP_DURATION:
            continue

        start_ms = max(0, int((segment.start - config.PADDING_SEC) * 1000))
        end_ms = min(len(audio), int((segment.end + config.PADDING_SEC) * 1000))
        clip = audio[start_ms:end_ms]

        name = config.CLIP_NAME_FORMAT.format(counter)
        wav_path = os.path.join(wavs_dir, f"{name}.wav")
        if normalize:
            normalize_clip(clip, wav_path, sample_rate=config.DEFAULT_SAMPLE_RATE, denoise=denoise)
        else:
            clip = clip.set_frame_rate(config.DEFAULT_SAMPLE_RATE).set_channels(1).set_sample_width(2)
            clip.export(wav_path, format="wav")

        entries.append((name, text))
        print(f"[{name}] ({duration:.2f}s): {text}")
        counter += 1

    print(f"\nWriting {len(entries)} dataset entries to {metadata_path}...")
    with open(metadata_path, "w", encoding="utf-8", newline="") as f:
        csv.writer(f, delimiter="|").writerows(entries)
    print(f"Dataset complete. Clips: {wavs_dir}/  Map: {metadata_path}")
    return entries
