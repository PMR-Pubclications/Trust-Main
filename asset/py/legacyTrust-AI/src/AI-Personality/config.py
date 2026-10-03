"""Single source of truth for the AI-Personality folder."""
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEGACY_ROOT = HERE.parent.parent  # asset/py/legacyTrust-AI (real diagnostics live here)
for _p in (str(HERE), str(LEGACY_ROOT)):
    if _p not in sys.path:
        sys.path.append(_p)

# Piper voice model (one filename shared by every Piper entrypoint)
PIPER_MODEL_PATH = "my_custom_voice.onnx"
PIPER_CONFIG_PATH = f"{PIPER_MODEL_PATH}.json"
DEFAULT_SAMPLE_RATE = 22050  # fallback only; real rate comes from the model .onnx.json

# Dataset pipeline
INPUT_AUDIO_PATH = "long_recording.mp3"
OUTPUT_DIR = "custom_voice_dataset"
WHISPER_MODEL_SIZE = "base.en"
WHISPER_DEVICE = "cuda"          # use "cpu" without an NVIDIA GPU
WHISPER_COMPUTE_TYPE = "float16"  # use "int8" on CPU
MIN_CLIP_DURATION = 1.0
MAX_CLIP_DURATION = 12.0
PADDING_SEC = 0.08
CLIP_NAME_FORMAT = "line_{:04d}"  # matches metadata.csv

# Denoise / loudness (EBU R128)
HIGHPASS_FREQ = 80
AFFTDN_NOISE_REDUCE = 12
AFFTDN_NOISE_FLOOR = -50
TRACK_NOISE = 1
TARGET_I = -20.0
TARGET_TP = -1.0
TARGET_LRA = 7.0
I_TOLERANCE = 1.0
MAX_TRUE_PEAK = TARGET_TP
VERIFY_MAX_WORKERS = 8
WAV_DIR = Path(OUTPUT_DIR) / "wavs"


@dataclass
class AnonPersonaConfig:
    name: str = "Anon"
    origin: str = "Midwest"
    archetype: str = "Systems Partner & Ranch Hand Engineer"
    tagline: str = "Measure twice, cut once."
