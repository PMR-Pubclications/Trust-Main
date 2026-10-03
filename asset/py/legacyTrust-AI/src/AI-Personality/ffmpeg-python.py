"""Backwards-compatible entrypoint; implementation lives in dataset_prep.py (loudnorm)."""
from dataset_prep import process_audio_to_piper_dataset

if __name__ == "__main__":
    process_audio_to_piper_dataset(normalize=True)
