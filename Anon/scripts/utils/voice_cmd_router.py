#!/usr/bin/env python3
"""Noise-resilient voice and text command router for Anon AI.

Mapped to the Anon AI project file structure (Anon/scripts/utils/).
Routes voice commands and fast text shortcuts to execution pipelines across
preprocessing, training, deploy, and forensic submodules.
"""

from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

# ==============================================================================
# Directory Resolution based on Anon AI Project Schematic
# ==============================================================================
UTILS_DIR = Path(__file__).resolve().parent           # Anon/scripts/utils/
SCRIPTS_DIR = UTILS_DIR.parent                         # Anon/scripts/
PROJECT_ROOT = SCRIPTS_DIR.parent                      # Anon/

# Schematic Core Directories
PREPROCESSING_DIR = SCRIPTS_DIR / "preprocessing"
MODELS_SCRIPTS_DIR = SCRIPTS_DIR / "models"
TRAINING_DIR = SCRIPTS_DIR / "training"
DEPLOY_DIR = SCRIPTS_DIR / "deploy"
CONFIG_DIR = PROJECT_ROOT / "config"
MODELS_ARTIFACTS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Extended Forensic/Agent Submodules
FERENSICS_AI_DIR = SCRIPTS_DIR / "ferensics-ai"

# Direct Alias Map for O(1) Routing & Noisy Audio Matches
ALIAS_MAP = {
    # Core Pipeline Executables
    "train model": TRAINING_DIR / "train.py",
    "evaluate model": TRAINING_DIR / "evaluate.py",
    "run prediction": DEPLOY_DIR / "predict.py",
    "start api": DEPLOY_DIR / "api.py",
    "clean data": PREPROCESSING_DIR / "clean_data.py",
    "augment data": PREPROCESSING_DIR / "augment.py",
    
    # Agent & Operations Suite
    "agent loop": SCRIPTS_DIR / "agent_loop.py",
    "run agent": SCRIPTS_DIR / "agent_loop.py",
    "opensea": SCRIPTS_DIR / "opensea-agent-access.py",
    "open sea": SCRIPTS_DIR / "opensea-agent-access.py",
    "google drive": SCRIPTS_DIR / "access-google-drive.py",
    "secure google drive": SCRIPTS_DIR / "secure-googledive-access.py",
    "sweep ellipal": SCRIPTS_DIR / "sweep_to_ellipal.py",
    "etherscan": SCRIPTS_DIR / "etherscan-data-api.py",
    "liquid": SCRIPTS_DIR / "liquid-installer.py",
    
    # Anon Forensics Suite
    "ferensics ai server": FERENSICS_AI_DIR / "ferensicAIserver.py",
    "anon ai server": FERENSICS_AI_DIR / "ferensicAIserver.py",
    "forensic server": FERENSICS_AI_DIR / "ferensicAIserver.py",
    "video ballistics": FERENSICS_AI_DIR / "video_ballistics.py",
    "ballistics": FERENSICS_AI_DIR / "video_ballistics.py",
    "ballistics comparator": FERENSICS_AI_DIR / "ballistics_comparator.py",
    "forensic physics": FERENSICS_AI_DIR / "ferensics _physcs.py",
    "physics": FERENSICS_AI_DIR / "ferensics _physcs.py",
    "train forensic slm": FERENSICS_AI_DIR / "train_forensic_slm.py",
    "train slm": FERENSICS_AI_DIR / "train_forensic_slm.py",
    "sft trainer": FERENSICS_AI_DIR / "SFTTrainer.py",
    "trainer": FERENSICS_AI_DIR / "SFTTrainer.py",
}


def normalize(value: str) -> str:
    """Strips voice filler words and normalizes input text."""
    val = value.lower().strip()
    for prefix in ("run ", "execute ", "launch ", "start ", "open "):
        if val.startswith(prefix):
            val = val[len(prefix):]
            break
    return re.sub(r"[^\w\s]", "", val).strip()


@lru_cache(maxsize=1)
def build_script_index() -> dict[str, Path]:
    """Pre-caches script locations across the Anon AI directory tree into memory."""
    index: dict[str, Path] = {}

    # 1. Register explicit alias targets
    for alias, path in ALIAS_MAP.items():
        if path.exists():
            index[normalize(alias)] = path

    # 2. Recursively index executable scripts under Anon/scripts/
    if SCRIPTS_DIR.exists():
        for child in SCRIPTS_DIR.rglob("*"):
            if child.is_file() and child.suffix.lower() in {".py", ".sh"}:
                index[normalize(child.stem)] = child

    # 3. Index top-level entrypoints (e.g., Anon/main.py)
    main_py = PROJECT_ROOT / "main.py"
    if main_py.exists():
        index["main"] = main_py
        index["run main"] = main_py

    return index


def get_best_match(query: str, cutoff: float = 0.45) -> Path | None:
    """Matches exact input or applies Levenshtein fuzzy auto-correct for street noise."""
    cleaned = normalize(query)
    if not cleaned:
        return None

    index = build_script_index()

    # Fast path: exact match
    if cleaned in index:
        return index[cleaned]

    # Substring containment
    for key, path in index.items():
        if key and (key in cleaned or cleaned in key):
            return path

    # Fuzzy match fallback for garbled voice inputs
    matches = difflib.get_close_matches(cleaned, index.keys(), n=1, cutoff=cutoff)
    if matches:
        return index[matches[0]]

    return None


def list_scripts() -> str:
    """Displays all indexed tools across the Anon AI modules."""
    index = build_script_index()
    unique_paths = sorted(set(index.values()))
    names = [
        p.relative_to(PROJECT_ROOT).as_posix() if PROJECT_ROOT in p.parents else p.name
        for p in unique_paths
    ]
    return "Available Anon AI Scripts:\n- " + "\n- ".join(names)


def run_script(script_path: Path) -> int:
    """Executes target script within the active Python environment."""
    if not script_path.exists():
        print(f"❌ Target script not found: {script_path}")
        return 1

    rel_path = script_path.relative_to(PROJECT_ROOT) if PROJECT_ROOT in script_path.parents else script_path
    print(f"⚡ Launching: {rel_path}")
    result = subprocess.run([sys.executable, str(script_path)], cwd=str(PROJECT_ROOT))
    return result.returncode


def handle_command(command: str) -> int:
    """Parses user input string and triggers execution or output utility."""
    raw = command.strip()
    if not raw:
        return 1

    lowered = raw.lower()
    if lowered in {"help", "--help", "?"}:
        print(
            "Anon AI Router Commands:\n"
            "  list | run <script_or_alias> | quit\n"
            "Schematic Short-keys:\n"
            "  'train model', 'start api', 'clean data', 'video ballistics', 'agent loop'"
        )
        return 0

    if lowered in {"list", "list scripts", "ls", "show scripts"}:
        print(list_scripts())
        return 0

    if lowered in {"quit", "exit", "stop"}:
        print("Anon AI voice session ended.")
        return 0

    match = get_best_match(raw)
    if match:
        return run_script(match)

    print(f"❌ No matching script found for: '{raw}'")
    print("Tip: Type 'list' or say 'help' for available commands.")
    return 1


def listen_for_voice() -> str | None:
    """Captures microphone input tuned for high ambient noise."""
    try:
        import speech_recognition as sr  # type: ignore
    except Exception:
        print("⚠️ SpeechRecognition package not found. Falling back to CLI mode.")
        return None

    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.5
    recognizer.operation_timeout = 4.0

    print("🎙️ Anon AI Listening (scripts/utils)...")
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = recognizer.listen(source, timeout=3.5, phrase_time_limit=4.0)
        except sr.WaitTimeoutError:
            print("⚠️ Listening timed out. No voice detected.")
            return None

    try:
        text = recognizer.recognize_google(audio)
        print(f"🗣️ Heard: {text}")
        return text
    except Exception as exc:
        print(f"⚠️ Speech processing failed: {exc}")
        return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Anon AI Module Voice Command Router")
    parser.add_argument("--command", help="Direct text command")
    parser.add_argument("--voice", action="store_true", help="Activate microphone listener")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.voice:
        command = listen_for_voice()
        if not command:
            return 1
        return handle_command(command)

    if args.command:
        return handle_command(args.command)

    # Pre-cache directory structure
    build_script_index()

    print("Anon AI Voice Command Router [/Anon/scripts/utils]")
    print("Type 'help' or enter a command. Ctrl+C to exit.")

    while True:
        try:
            text = input("Anon-AI> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if not text.strip():
            continue
        result = handle_command(text)
        if result == 0 and text.strip().lower() in {"quit", "exit", "stop"}:
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
