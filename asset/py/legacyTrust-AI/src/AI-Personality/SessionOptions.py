"""Backwards-compatible entrypoint; implementation lives in piper_session.py."""
import config
from piper_session import create_optimized_piper_session, synthesize_phonemes

__all__ = ["create_optimized_piper_session", "synthesize_phonemes"]

if __name__ == "__main__":
    sample_phoneme_ids = [1, 10, 42, 15, 8, 23, 19, 31, 2]
    try:
        session = create_optimized_piper_session(config.PIPER_MODEL_PATH, device="cuda", cpu_threads=4)
        audio, ms = synthesize_phonemes(session, sample_phoneme_ids)
        print(f"Inference complete: {len(audio)} samples generated in {ms:.2f} ms")
    except Exception as e:
        print(f"Inference failed: {e}")
