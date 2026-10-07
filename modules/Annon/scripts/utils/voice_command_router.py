#!/usr/bin/env python3
"""Unified, noise-resilient voice command router with dynamic vocabulary learning.

Mapped to: modules/Annon/scripts/utils/voice_command_router.py
Features persistent learning (learned_vocab.json) to adapt to voice variations over time.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

# Directory Anchor Resolution (modules/Annon/scripts/utils/)
UTILS_DIR = Path(__file__).resolve().parent           # modules/Annon/scripts/utils/
SCRIPTS_DIR = UTILS_DIR.parent                         # modules/Annon/scripts/
ANNON_ROOT = SCRIPTS_DIR.parent                        # modules/Annon/
MODULES_ROOT = ANNON_ROOT.parent                       # modules/

# Dynamic Learning Storage File
LEARNED_VOCAB_FILE = UTILS_DIR / "learned_vocab.json"

# Core Alias Map: (Aliases) -> Relative Path String
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
    ("ferensics ai server", "annon ai server", "forensic server"): "ferensics-ai/ferensicAIserver.py",
    ("video ballistics", "ballistics"): "ferensics-ai/video_ballistics.py",
    ("ballistics comparator",): "ferensics-ai/ballistics_comparator.py",
    ("forensic physics", "physics"): "ferensics-ai/ferensics _physcs.py",
    ("train forensic slm", "train slm"): "ferensics-ai/train_forensic_slm.py",
    ("sft trainer", "trainer"): "ferensics-ai/SFTTrainer.py",
}


def normalize(val: str) -> str:
    """Strips voice command prefixes and normalizes input string."""
    val = val.lower().strip()
    for p in ("run ", "execute ", "launch ", "start ", "open "):
        if val.startswith(p):
            val = val[len(p):]
            break
    return re.sub(r"[^\w\s]", "", val).strip()


def load_learned_vocab() -> dict[str, str]:
    """Loads dynamically learned phrase-to-script mappings from persistent storage."""
    if LEARNED_VOCAB_FILE.exists():
        try:
            with open(LEARNED_VOCAB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Warning: Failed to load dynamic vocab: {e}")
    return {}


def save_learned_phrase(heard_phrase: str, target_rel_path: str) -> None:
    """Saves a new learned voice alias to disk for persistent adaptation."""
    vocab = load_learned_vocab()
    cleaned = normalize(heard_phrase)
    vocab[cleaned] = target_rel_path
    
    try:
        with open(LEARNED_VOCAB_FILE, "w", encoding="utf-8") as f:
            json.dump(vocab, f, indent=2)
        build_script_index.cache_clear()  # Refresh cache with new learned item
        print(f"🧠 Dynamic Learning Updated: '{cleaned}' ➔ {target_rel_path}")
    except Exception as e:
        print(f"❌ Failed to save learned vocabulary: {e}")


@lru_cache(maxsize=1)
def build_script_index() -> dict[str, Path]:
    """Combines core aliases, dynamic learned phrases, and folder scans into memory."""
    index: dict[str, Path] = {}

    # 1. Dynamically Learned Vocabulary (Highest priority for adaptive learning)
    learned = load_learned_vocab()
    for phrase, rel_p in learned.items():
        target = (SCRIPTS_DIR / rel_p).resolve()
        if target.exists():
            index[normalize(phrase)] = target

    # 2. Hardcoded Core Aliases
    for aliases, rel_path in RAW_ALIAS_MAP.items():
        target = (SCRIPTS_DIR / rel_path).resolve()
        for alias in (aliases if isinstance(aliases, tuple) else (aliases,)):
            norm_alias = normalize(alias)
            if norm_alias not in index:
                index[norm_alias] = target

    # 3. Dynamic Directory Scan across modules/Annon/scripts/
    if SCRIPTS_DIR.exists():
        for child in SCRIPTS_DIR.rglob("*"):
            if child.is_file() and child.suffix.lower() in {".py", ".sh"}:
                norm_stem = normalize(child.stem)
                if norm_stem not in index:
                    index[norm_stem] = child

    return index


def get_best_match(query: str, cutoff: float = 0.45) -> Path | None:
    """Lookup with exact match, substring matching, and fuzzy Levenshtein fallback."""
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

    # Fuzzy match fallback for noise/mispronunciations
    matches = difflib.get_close_matches(cleaned, index.keys(), n=1, cutoff=cutoff)
    return index[matches[0]] if matches else None


def list_scripts() -> str:
    """Lists indexed scripts formatted relative to modules/Annon root."""
    unique_paths = sorted(set(build_script_index().values()))
    names = [
        p.relative_to(ANNON_ROOT).as_posix() if ANNON_ROOT in p.parents else p.name
        for p in unique_paths
    ]
    return "Available Annon Executables:\n- " + "\n- ".join(names)


def run_script(script_path: Path) -> int:
    """Executes target script with working directory set to modules/Annon."""
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return 1

    rel = script_path.relative_to(ANNON_ROOT) if ANNON_ROOT in script_path.parents else script_path
    print(f"⚡ Executing: {rel}")
    return subprocess.run([sys.executable, str(script_path)], cwd=str(ANNON_ROOT)).returncode


def learn_interactive(last_heard: str) -> None:
    """Interactive feedback loop to teach the router new misheard phrases."""
    print(f"\n🎓 TEACH ROUTER: What script should '{last_heard}' run?")
    index = build_script_index()
    unique_paths = sorted(set(index.values()))
    
    for idx, path in enumerate(unique_paths, 1):
        rel = path.relative_to(SCRIPTS_DIR).as_posix() if SCRIPTS_DIR in path.parents else path.name
        print(f"  [{idx}] {rel}")
        
    choice = input("Enter number to link (or press Enter to cancel): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(unique_paths):
        selected_path = unique_paths[int(choice) - 1]
        rel_to_scripts = selected_path.relative_to(SCRIPTS_DIR).as_posix()
        save_learned_phrase(last_heard, rel_to_scripts)


def handle_command(command: str) -> int:
    """Routes voice/text commands and triggers training mode if unmatched."""
    raw = command.strip()
    if not raw:
        return 1

    lowered = raw.lower()
    if lowered in {"help", "--help", "?"}:
        print("Commands: list | run <script_or_alias> | learn | quit\nShortcuts: train, api, agent, ballistics, physics")
        return 0
    if lowered in {"list", "list scripts", "ls", "show scripts"}:
        print(list_scripts())
        return 0
    if lowered in {"quit", "exit", "stop"}:
        print("Annon router terminated.")
        return 0

    match = get_best_match(raw)
    if match:
        return run_script(match)

    print(f"❌ Command not recognized: '{raw}'")
    teach = input("Would you like to teach Annon this phrase? (y/N): ").strip().lower()
    if teach == 'y':
        learn_interactive(raw)
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

    print("🎙️ Annon Listening...")
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
    parser = argparse.ArgumentParser(description="Adaptive Voice Router for Annon")
    parser.add_argument("--command", help="Direct text command")
    parser.add_argument("--voice", action="store_true", help="Listen for voice input")
    args = parser.parse_args()

    if args.voice:
        cmd = listen_for_voice()
        return handle_command(cmd) if cmd else 1
    if args.command:
        return handle_command(args.command)

    build_script_index()  # Pre-warm cache
    print("Annon Voice Command Router [/modules/Annon/scripts/utils/voice_command_router.py]")
    print("Type 'help' or enter a command. Ctrl+C to exit.")

    while True:
        try:
            text = input("Annon> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if text.strip() and handle_command(text) == 0 and text.strip().lower() in {"quit", "exit", "stop"}:
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
