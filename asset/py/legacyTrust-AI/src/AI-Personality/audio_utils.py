"""Shared text cleaning and ffmpeg normalization used by the dataset tools."""
import os
import re
from typing import Optional

import config


def clean_text_for_tts(text: str) -> str:
    """Cleans up raw transcription text for TTS training."""
    text = re.sub(r"\s+", " ", text.strip())
    return re.sub(r"[\[\]\(\)\{\}]", "", text)


def normalize_clip(
    clip,
    output_path: str,
    sample_rate: int = config.DEFAULT_SAMPLE_RATE,
    denoise: bool = False,
    rnnoise_model_path: Optional[str] = None,
) -> None:
    """
    Pipes a pydub AudioSegment through ffmpeg (optional highpass + denoise,
    then EBU R128 loudnorm) and writes a 16-bit mono WAV.
    Raises RuntimeError if ffmpeg fails.
    """
    import ffmpeg

    stream = ffmpeg.input("pipe:", format="s16le", ac=clip.channels, ar=clip.frame_rate)

    if denoise:
        stream = stream.filter("highpass", f=config.HIGHPASS_FREQ)
        if rnnoise_model_path and os.path.exists(rnnoise_model_path):
            stream = stream.filter("arnndn", m=rnnoise_model_path)
        else:
            stream = stream.filter(
                "afftdn",
                nr=config.AFFTDN_NOISE_REDUCE,
                nf=config.AFFTDN_NOISE_FLOOR,
                tn=config.TRACK_NOISE,
            )

    stream = stream.filter("loudnorm", I=config.TARGET_I, TP=config.TARGET_TP, LRA=config.TARGET_LRA)
    stream = stream.output(output_path, ar=sample_rate, ac=1, acodec="pcm_s16le").overwrite_output()

    process = stream.run_async(pipe_stdin=True, pipe_stderr=True)
    _, stderr = process.communicate(input=clip.raw_data)
    if process.returncode != 0:
        raise RuntimeError(f"ffmpeg failed ({process.returncode}) for {output_path}: {stderr.decode(errors='replace')[-500:]}")


def chunk_text_stream(text: str, min_words: int = 3):
    """
    Splits text on clause and sentence boundaries (. , ! ? ; :)
    to yield short phrases suitable for sub-200ms latency synthesis.
    """
    pattern = re.compile(r'(?<=[.!?;,:])\s+')
    parts = pattern.split(text)

    buffer = ""
    for part in parts:
        buffer = f"{buffer} {part}".strip() if buffer else part
        # Yield if we have reached a reasonable word threshold
        if len(buffer.split()) >= min_words:
            yield buffer
            buffer = ""

    if buffer:
        yield buffer
