#!/usr/bin/env python3
"""Unified, compressed noise-resilient voice command router for Anon AI.

Combines all core pipeline, forensic, and agent commands into a high-performance,
memory-cached router mapped to the Anon project layout (Anon/scripts/utils/).
"""

from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

# Directory Anchor Resolution
UTILS_DIR = Path(__file__).resolve().parent           # Anon/scripts/utils/
SCRIPTS_DIR = UTILS_DIR.parent                         # Anon/scripts/
PROJECT_ROOT = SCRIPTS_DIR.parent                      # Anon/

# Compressed Alias Map: (Aliases) -> Relative Path String
RAW_ALIAS_MAP: dict[tuple[str, ...], str] = {
    ("main", "run main"): "../main.py",
    ("train model", "train"): "training/train.py",
    ("evaluate model", "evaluate"): "training/evaluate.py",
    ("predict", "run prediction"): "deploy/predict.py",
    ("api", "start api"): "deploy/api.py",
    ("clean data", "clean"): "preprocessing/clean_data.py",
    ("augment data", "augment"): "preprocessing/augment.py",
    ("agent loop", "run agent", "agent"): "agent_loop.py",
    ("opensea", "open sea"): "opensea-agent-access.py",
    ("google drive", "drive"): "access-google-drive.py",
    ("secure google drive", "secure google"): "secure-googledive-access.py",
    ("sweep ellipal", "ellipal"): "sweep_to_ellipal.py",
    ("etherscan",): "etherscan-data-api.py",
    ("liquid",): "liquid-installer.py",
    ("ferensics ai server", "anon ai server", "forensic server"): "ferensics-ai/ferensicAIserver.py",
    ("video ballistics", "ballistics"): "ferensics-ai/video_ballistics.py",
    ("ballistics comparator",): "ferensics-ai/ballistics_comparator.py",
    ("forensic physics", "physics"): "ferensics-ai/ferensics _physcs.py",
    ("train forensic slm", "train slm"): "ferensics-ai/train_forensic_slm.py",
    "sft trainer", "trainer": "ferensics-ai/SFTTrainer.py",
}


def normalize(val: str) -> str:
    """Strips voice command prefixes and normalizes input string."""
    val = val.lower().strip()
    for p in ("run ", "execute ", "launch ", "start ", "open "):
        if val.startswith(p):
            val = val[len(p):]
            break
    return re.sub(r"[^\w\s]", "", val).strip()


@lru_cache(maxsize=1)
def build_script_index() -> dict[str, Path]:
    """Compresses lookup table and indexes project files into an in-memory map."""
    index: dict[str, Path] = {}

    # 1. Unroll compressed alias mappings
    for aliases, rel_path in RAW_ALIAS_MAP.items():
        target = (SCRIPTS_DIR / rel_path).resolve()
        for alias in (aliases if isinstance(aliases, tuple) else (aliases,)):
            index[normalize(alias)] = target

    # 2. Dynamic scan across Anon/scripts/ for unmapped scripts
    if SCRIPTS_DIR.exists():
        for child in SCRIPTS_DIR.rglob("*"):
            if child.is_file() and child.suffix.lower() in {".py", ".sh"}:
                norm_stem = normalize(child.stem)
                if norm_stem not in index:
                    index[norm_stem] = child

    return index


def get_best_match(query: str, cutoff: float = 0.45) -> Path | None:
    """O(1) exact lookup with substring and Levenshtein fuzzy matching fallback."""
    cleaned = normalize(query)
    if not cleaned:
        return None

    index = build_script_index()

    # Exact or substring match
    if cleaned in index:
        return index[cleaned]
    for key, path in index.items():
        if key and (key in cleaned or cleaned in key):
            return path

    # Fuzzy match for speech-to-text noise
    matches = difflib.get_close_matches(cleaned, index.keys(), n=1, cutoff=cutoff)
    return index[matches[0]] if matches else None


def list_scripts() -> str:
    """Lists indexed scripts formatted relative to Anon project root."""
    unique_paths = sorted(set(build_script_index().values()))
    names = [
        p.relative_to(PROJECT_ROOT).as_posix() if PROJECT_ROOT in p.parents else p.name
        for p in unique_paths
    ]
    return "Available Anon AI Executables:\n- " + "\n- ".join(names)


def run_script(script_path: Path) -> int:
    """Executes target script from Anon root directory."""
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return 1

    rel = script_path.relative_to(PROJECT_ROOT) if PROJECT_ROOT in script_path.parents else script_path
    print(f"⚡ Executing: {rel}")
    return subprocess.run([sys.executable, str(script_path)], cwd=str(PROJECT_ROOT)).returncode


def handle_command(command: str) -> int:
    """Routes voice/text commands to matching script execution handlers."""
    raw = command.strip()
    if not raw:
        return 1

    lowered = raw.lower()
    if lowered in {"help", "--help", "?"}:
        print("Commands: list | run <script_or_alias> | quit\nShortcuts: train, api, agent, ballistics, physics")
        return 0
    if lowered in {"list", "list scripts", "ls", "show scripts"}:
        print(list_scripts())
        return 0
    if lowered in {"quit", "exit", "stop"}:
        print("Anon AI router terminated.")
        return 0

    match = get_best_match(raw)
    if match:
        return run_script(match)

    print(f"❌ Command not recognized: '{raw}' (type 'list' for options)")
    return 1


def listen_for_voice() -> str | None:
    """Captures voice input with noise suppression tuned for ambient field conditions."""
    try:
        import speech_recognition as sr  # type: ignore
    except Exception:
        print("⚠️ SpeechRecognition package missing. Switching to CLI input.")
        return None

    r = sr.Recognizer()
    r.dynamic_energy_threshold, r.pause_threshold, r.operation_timeout = True, 0.5, 4.0

    print("🎙️ Anon AI Listening...")
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = r.listen(source, timeout=3.5, phrase_time_limit=4.0)
        except sr.WaitTimeoutError:
            print("⚠️ Timeout: No speech detected.")
            return None

    try:
        text = r.recognize_google(audio)
        print(f"🗣️ Heard: {text}")
        return text
    except Exception as exc:
        print(f"⚠️ Voice processing error: {exc}")
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Unified Voice Router for Anon AI")
    parser.add_argument("--command", help="Direct text command")
    parser.add_argument("--voice", action="store_true", help="Listen for voice input")
    args = parser.parse_args()

    if args.voice:
        cmd = listen_for_voice()
        return handle_command(cmd) if cmd else 1
    if args.command:
        return handle_command(args.command)

    build_script_index()  # Pre-warm cache
    print("Anon AI Voice Command Router [/Anon/scripts/utils/voice_command_router.py]")
    print("Type 'help' or enter a command. Ctrl+C to exit.")

    while True:
        try:
            text = input("Anon-AI> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if text.strip() and handle_command(text) == 0 and text.strip().lower() in {"quit", "exit", "stop"}:
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
