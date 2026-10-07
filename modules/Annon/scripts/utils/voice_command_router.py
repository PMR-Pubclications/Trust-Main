#!/usr/bin/env python3
"""Unified, noise-resilient voice command router for Annon AI.

Mapped to: modules/Annon/scripts/utils/voice_command_router.py
Integrates:
- Badge Assignment & Authentication Controller (Trust-Main/asset/java/BadgeAssignmentController.java)
- Java Ballistic Video Analysis (Trust-Main/asset/java/ballisticVideoAnalysis)
- Python Forensic & Scene Physics Engine (Trust-Main/asset/py/ferensics-ai)
- Local Annon Pipeline Scripts & Dynamic Persistent Vocabulary Learning
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

# ==============================================================================
# Directory Anchor Resolution (modules/Annon/scripts/utils/)
# ==============================================================================
UTILS_DIR = Path(__file__).resolve().parent           # modules/Annon/scripts/utils/
SCRIPTS_DIR = UTILS_DIR.parent                         # modules/Annon/scripts/
ANNON_ROOT = SCRIPTS_DIR.parent                        # modules/Annon/
MODULES_ROOT = ANNON_ROOT.parent                       # modules/

# External Forensics & Authentication Asset Paths (Trust-Main Repository)
TRUST_MAIN_DIR = MODULES_ROOT / "Trust-Main"
JAVA_ASSET_DIR = TRUST_MAIN_DIR / "asset" / "java"
BALLISTIC_JAVA_DIR = JAVA_ASSET_DIR / "ballisticVideoAnalysis"
BADGE_CONTROLLER_FILE = JAVA_ASSET_DIR / "BadgeAssignmentController.java"
FORENSICS_PY_DIR = TRUST_MAIN_DIR / "asset" / "py" / "ferensics-ai"

# Dynamic Learning Storage File
LEARNED_VOCAB_FILE = UTILS_DIR / "learned_vocab.json"

# ==============================================================================
# Core Alias Map: (Aliases) -> Relative Path String
# ==============================================================================
RAW_ALIAS_MAP: dict[tuple[str, ...], str] = {
    # Security, Access Control & Badge Login
    ("badge validation", "validate badge", "badge assignment", "badge controller", "login badge", "authenticate badge", "badge check"): "../../Trust-Main/asset/java/BadgeAssignmentController.java",

    # Core Annon Pipeline
    ("main", "run main"): "../main.py",
    ("train model", "train"): "training/train.py",
    ("evaluate model", "evaluate"): "training/evaluate.py",
    ("predict", "run prediction"): "deploy/predict.py",
    ("api", "start api"): "deploy/api.py",
    ("clean data", "clean"): "preprocessing/clean_data.py",
    ("augment data", "augment"): "preprocessing/augment.py",
    ("agent loop", "run agent", "agent"): "agent_loop.py",

    # Java Ballistics Module (Trust-Main)
    ("ballistic video analysis", "java ballistics", "trust ballistics"): "../../Trust-Main/asset/java/ballisticVideoAnalysis",

    # Non-Ballistic Forensic AI, Scene Analysis & Physics (Trust-Main / asset / py / ferensics-ai)
    ("scene analysis", "forensic scene analysis", "scene reconstruction"): "../../Trust-Main/asset/py/ferensics-ai",
    ("forensic physics", "scene physics", "basic forensics", "physics"): "../../Trust-Main/asset/py/ferensics-ai/ferensics _physcs.py",
    ("forensic server", "annon ai server", "ferensics ai server"): "../../Trust-Main/asset/py/ferensics-ai/ferensicAIserver.py",
    ("video ballistics", "ballistics"): "../../Trust-Main/asset/py/ferensics-ai/video_ballistics.py",
    ("ballistics comparator",): "../../Trust-Main/asset/py/ferensics-ai/ballistics_comparator.py",
    ("train forensic slm", "train slm"): "../../Trust-Main/asset/py/ferensics-ai/train_forensic_slm.py",
    ("sft trainer", "trainer"): "../../Trust-Main/asset/py/ferensics-ai/SFTTrainer.py",

    # Local Fallback Forensics (Annon/scripts/ferensics-ai)
    ("local physics",): "ferensics-ai/ferensics _physcs.py",
    ("local forensic server",): "ferensics-ai/ferensicAIserver.py",

    # Field Operations & Web Integrations
    ("opensea", "open sea"): "opensea-agent-access.py",
    ("google drive", "drive"): "access-google-drive.py",
    ("secure google drive", "secure google"): "secure-googledive-access.py",
    ("sweep ellipal", "ellipal"): "sweep_to_ellipal.py",
    ("etherscan",): "etherscan-data-api.py",
    ("liquid",): "liquid-installer.py",
}


def normalize(val: str) -> str:
    """Strips voice command prefixes and standardizes input string."""
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
        build_script_index.cache_clear()
        print(f"🧠 Dynamic Learning Updated: '{cleaned}' ➔ {target_rel_path}")
    except Exception as e:
        print(f"❌ Failed to save learned vocabulary: {e}")


@lru_cache(maxsize=1)
def build_script_index() -> dict[str, Path]:
    """Indexes Annon scripts, Trust-Main Java controllers/ballistics, Python physics/scene assets, and dynamic vocabulary."""
    index: dict[str, Path] = {}

    # 1. Dynamically Learned Vocabulary (Highest Priority)
    for phrase, rel_p in load_learned_vocab().items():
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
            if child.is_file() and child.suffix.lower() in {".py", ".sh", ".java", ".jar"}:
                norm_stem = normalize(child.stem)
                if norm_stem not in index:
                    index[norm_stem] = child

    # 4. Java Assets & Security Scan (Trust-Main/asset/java)
    if JAVA_ASSET_DIR.exists():
        for child in JAVA_ASSET_DIR.rglob("*"):
            if child.is_file() and child.suffix.lower() in {".java", ".jar", ".class"}:
                norm_stem = normalize(child.stem)
                if norm_stem not in index:
                    index[norm_stem] = child

    # 5. Non-Ballistic Python Forensics & Scene Physics Scan (Trust-Main/asset/py/ferensics-ai)
    if FORENSICS_PY_DIR.exists():
        index["scene analysis"] = FORENSICS_PY_DIR
        index["forensic scene analysis"] = FORENSICS_PY_DIR
        index["scene reconstruction"] = FORENSICS_PY_DIR
        for child in FORENSICS_PY_DIR.iterdir():
            if child.is_file() and child.suffix.lower() in {".py", ".sh"}:
                norm_stem = normalize(child.stem)
                index[norm_stem] = child

    return index


def get_best_match(query: str, cutoff: float = 0.45) -> Path | None:
    """Exact lookup, substring matching, and fuzzy Levenshtein distance fallback."""
    cleaned = normalize(query)
    if not cleaned:
        return None

    index = build_script_index()

    # Direct or substring match
    if cleaned in index:
        return index[cleaned]
    for key, path in index.items():
        if key and (key in cleaned or cleaned in key):
            return path

    # Fuzzy match fallback
    matches = difflib.get_close_matches(cleaned, index.keys(), n=1, cutoff=cutoff)
    return index[matches[0]] if matches else None


def list_scripts() -> str:
    """Lists indexed scripts and external forensic/security tools."""
    unique_paths = sorted(set(build_script_index().values()))
    names = [
        p.relative_to(MODULES_ROOT).as_posix() if MODULES_ROOT in p.parents else p.name
        for p in unique_paths
    ]
    return "Available Annon Executables & Security/Forensic Tools:\n- " + "\n- ".join(names)


def run_target(target_path: Path) -> int:
    """Executes Python scripts, Shell scripts, or launches Java controllers and modules."""
    if not target_path.exists():
        print(f"❌ Target path not found: {target_path}")
        return 1

    # Handle directory execution (e.g., Java Ballistics or Python Scene Analysis Directory)
    if target_path.is_dir():
        py_files = list(target_path.glob("*.py"))
        java_files = list(target_path.glob("*.java")) + list(target_path.glob("*.jar"))

        if py_files:
            main_py = next((f for f in py_files if "server" in f.name.lower() or "physc" in f.name.lower()), py_files[0])
            print(f"⚡ Launching Forensic Scene Analysis Module: {main_py.relative_to(MODULES_ROOT)}")
            return subprocess.run([sys.executable, str(main_py)], cwd=str(target_path)).returncode

        if java_files:
            print(f"⚡ Launching Java Ballistic Video Analysis: {target_path.relative_to(MODULES_ROOT)}")
            main_target = next((f for f in java_files if "Main" in f.name or "Analysis" in f.name), java_files[0])
            if main_target.suffix == ".jar":
                cmd = ["java", "-jar", str(main_target)]
            else:
                cmd = ["java", str(main_target)]
            return subprocess.run(cmd, cwd=str(target_path)).returncode

    rel = target_path.relative_to(ANNON_ROOT) if ANNON_ROOT in target_path.parents else target_path
    print(f"⚡ Executing: {rel}")

    if target_path.suffix == ".sh":
        return subprocess.run(["bash", str(target_path)], cwd=str(ANNON_ROOT)).returncode
    if target_path.suffix == ".java":
        return subprocess.run(["java", str(target_path)], cwd=str(target_path.parent)).returncode

    return subprocess.run([sys.executable, str(target_path)], cwd=str(ANNON_ROOT)).returncode


def learn_interactive(last_heard: str) -> None:
    """Teaches Annon new vocal variations for security, forensic, or system scripts."""
    print(f"\n🎓 TEACH ANNON: What script or tool should '{last_heard}' run?")
    index = build_script_index()
    unique_paths = sorted(set(index.values()))

    for idx, path in enumerate(unique_paths, 1):
        rel = path.relative_to(MODULES_ROOT).as_posix() if MODULES_ROOT in path.parents else path.name
        print(f"  [{idx}] {rel}")

    choice = input("Enter number to link (or press Enter to cancel): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(unique_paths):
        selected_path = unique_paths[int(choice) - 1]
        rel_to_scripts = selected_path.relative_to(SCRIPTS_DIR).as_posix() if SCRIPTS_DIR in selected_path.parents else selected_path.as_posix()
        save_learned_phrase(last_heard, rel_to_scripts)


def handle_command(command: str) -> int:
    """Routes voice/text input to script execution or interactive training mode."""
    raw = command.strip()
    if not raw:
        return 1

    lowered = raw.lower()
    if lowered in {"help", "--help", "?"}:
        print(
            "Commands:\n"
            "  list | run <script_or_alias> | learn | quit\n"
            "Shortcuts:\n"
            "  'validate badge', 'badge controller', 'scene analysis', 'forensic physics', 'ballistic video analysis', 'train slm'"
        )
        return 0
    if lowered in {"list", "list scripts", "ls", "show scripts"}:
        print(list_scripts())
        return 0
    if lowered in {"quit", "exit", "stop"}:
        print("Annon router terminated.")
        return 0

    match = get_best_match(raw)
    if match:
        return run_target(match)

    print(f"❌ Command not recognized: '{raw}'")
    teach = input("Would you like to teach Annon this phrase? (y/N): ").strip().lower()
    if teach == 'y':
        learn_interactive(raw)
    return 1


def listen_for_voice() -> str | None:
    """Captures microphone input with noise suppression optimized for field environments."""
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
    parser = argparse.ArgumentParser(description="Adaptive Voice Router for Annon Security & Trust Forensics")
    parser.add_argument("--command", help="Direct text command")
    parser.add_argument("--voice", action="store_true", help="Listen for voice input")
    args = parser.parse_args()

    if args.voice:
        cmd = listen_for_voice()
        return handle_command(cmd) if cmd else 1
    if args.command:
        return handle_command(args.command)

    build_script_index()  # Pre-warm index cache
    print("Annon Voice Router [/modules/Annon/scripts/utils/voice_command_router.py]")
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
