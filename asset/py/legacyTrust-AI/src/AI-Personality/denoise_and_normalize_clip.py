"""Denoise + loudnorm a pydub clip. Implementation lives in audio_utils.py."""
from typing import Optional

import config
from audio_utils import normalize_clip


def denoise_and_normalize_clip(
    clip,
    output_path: str,
    sample_rate: int = config.DEFAULT_SAMPLE_RATE,
    rnnoise_model_path: Optional[str] = None,
):
    normalize_clip(clip, output_path, sample_rate, denoise=True, rnnoise_model_path=rnnoise_model_path)
