"""Backwards-compatible entrypoint; implementation lives in dataset_prep.py (resample only)."""
from dataset_prep import process_audio_to_piper_dataset
from audio_utils import clean_text_for_tts

__all__ = ["process_audio_to_piper_dataset", "clean_text_for_tts"]

if __name__ == "__main__":
    process_audio_to_piper_dataset(normalize=False)
