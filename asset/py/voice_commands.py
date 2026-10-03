#!/usr/bin/env python3
"""Folder-scoped voice command router for the asset/py directory.

This script exposes a simple voice/text command interface for the Python tools
stored under this folder. It allows one to say or type commands such as:

- "list scripts"
- "run agent loop"
- "run opensea agent access"
- "run secure google drive"
- "help"

The commands operate from the asset/py folder instead of the repo root.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


FOLDER = Path(__file__).resolve().parent
REPO_ROOT = FOLDER.parent.parent


def normalize(value: str) -> str:
    return "".join(ch.lower() for ch in value if ch.isalnum() or ch in {"-", "_", " "}).replace("  ", " ").strip()


def script_catalog() -> list[Path]:
    files: list[Path] = []
    for child in sorted(FOLDER.iterdir()):
        if child.is_dir():
            continue
        if child.suffix.lower() in {".py", ".sh"}:
            files.append(child)
    return files


def get_script_matches(query: str) -> list[Path]:
    cleaned = normalize(query)
    matches: list[Path] = []

    for path in script_catalog():
        target = normalize(path.stem)
        if not cleaned:
            continue
        if cleaned in target or target in cleaned:
            matches.append(path)
        elif "agent" in cleaned and "agent" in target:
            matches.append(path)
        elif "google" in cleaned and "google" in target:
            matches.append(path)
        elif "opensea" in cleaned and "opensea" in target:
            matches.append(path)
        elif "secure" in cleaned and "secure" in target:
            matches.append(path)

    # Fallback: treat command words as alias-based matches for filenames.
    if not matches:
        alias_map = {
            "agent loop": FOLDER / "agent_loop.py",
            "opensea": FOLDER / "opensea-agent-access.py",
            "google drive": FOLDER / "access-google-drive.py",
            "secure google drive": FOLDER / "secure-googledive-access.py",
            "sweep ellipal": FOLDER / "sweep_to_ellipal.py",
            "etherscan": FOLDER / "etherscan-data-api.py",
            "liquid": FOLDER / "liquid-installer.py",
        }
        for alias, path in alias_map.items():
            if cleaned == alias or alias in cleaned:
                if path.exists():
                    matches.append(path)

    return matches


def list_scripts() -> str:
    names = [p.name for p in script_catalog()]
    return "Scripts available in asset/py:\n- " + "\n- ".join(names)


def run_script(script_path: Path) -> int:
    if not script_path.exists():
        print(f"Script not found: {script_path}")
        return 1

    print(f"Running: {script_path.relative_to(REPO_ROOT)}")
    result = subprocess.run([sys.executable, str(script_path)], cwd=str(FOLDER))
    return result.returncode


def handle_command(command: str) -> int:
    value = command.strip()
    if not value:
        print("No command received.")
        return 1

    lowered = value.lower()
    if lowered in {"help", "--help", "?"}:
        print(
            "Available commands:\n"
            "  list scripts\n"
            "  run agent loop\n"
            "  run opensea agent access\n"
            "  run google drive\n"
            "  run secure google drive\n"
            "  run sweep ellipal\n"
            "  run etherscan\n"
            "  quit"
        )
        return 0

    if lowered in {"list", "list scripts", "ls", "show scripts"}:
        print(list_scripts())
        return 0

    if lowered in {"quit", "exit", "stop"}:
        print("Voice command session ended.")
        return 0

    if lowered.startswith("run "):
        query = lowered[4:].strip()
    else:
        query = lowered

    matches = get_script_matches(query)
    if not matches:
        print(f"No matching script found for: {value}")
        print("Try: help")
        return 1

    if len(matches) > 1:
        print("Multiple matches found:")
        for match in matches:
            print(f"- {match.name}")
        return 1

    return run_script(matches[0])


def listen_for_voice() -> str | None:
    try:
        import speech_recognition as sr  # type: ignore
    except Exception:
        print("SpeechRecognition is not installed. Use text input instead.")
        return None

    recognizer = sr.Recognizer()
    print("Listening for a voice command in asset/py...")
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, timeout=8, phrase_time_limit=8)

    try:
        text = recognizer.recognize_google(audio)
        print(f"Heard: {text}")
        return text
    except Exception as exc:  # pragma: no cover - depends on runtime environment
        print(f"Voice recognition failed: {exc}")
        return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Voice command router for asset/py")
    parser.add_argument("--command", help="Run a direct command as text")
    parser.add_argument("--voice", action="store_true", help="Listen for a spoken command")
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

    while True:
        try:
            text = input("asset/py> ")
        except EOFError:
            print()
            return 0

        if text.strip() == "":
            continue
        result = handle_command(text)
        if result == 0 and text.strip().lower() in {"quit", "exit", "stop"}:
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
