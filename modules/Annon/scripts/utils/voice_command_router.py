#!/usr/bin/env python3
"""Unified, noise-resilient voice command router for Annon AI.

Mapped to Repository:
https://github.com/PMR-Pubclications/Trust-Main/tree/main/modules%2FAnnon%2Fscripts%2Fresearch_engine

Local Relative Location:
modules/Annon/scripts/utils/voice_command_router.py

Integrates:
- Badge Assignment & Authentication Controller (Trust-Main/asset/java/BadgeAssignmentController.java)
- Java Ballistic Video Analysis (Trust-Main/asset/java/ballisticVideoAnalysis)
- Python Forensic & Scene Physics Engine (Trust-Main/asset/py/ferensics-ai)
- Annon Research Engine Modules (modules/Annon/scripts/research_engine/)
  * Linguistic Propaganda & Rhetorical Epithet Analyzer
  * Constitutional & Textualist Legal Interpreter
  * Officer Threshold Breach & Warrant Safety Engine
- Dynamic Persistent Vocabulary Learning & Voice Routing via UmLanguageLibrary
"""

from __future__ import annotations

import argparse
import difflib
import json
import logging
import os
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

# ==============================================================================
# Directory Anchor Resolution (modules/Annon/scripts/utils/)
# Repository: https://github.com/PMR-Pubclications/Trust-Main/
# ==============================================================================
UTILS_DIR = Path(__file__).resolve().parent           # modules/Annon/scripts/utils/
SCRIPTS_DIR = UTILS_DIR.parent                         # modules/Annon/scripts/
RESEARCH_ENGINE_DIR = SCRIPTS_DIR / "research_engine" # modules/Annon/scripts/research_engine/
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

# Shared Language Library Dictionaries Path
LOCALES_DIR = TRUST_MAIN_DIR / "lib" / "LanguageLibrary" / "locales"


class UmLanguageLibrary:
    """Python counterpart for dynamic internationalization and locale resolution."""
    def __init__(self, default_locale='en', locales_dir=None):
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.dictionaries = {}
        self.locales_dir = Path(locales_dir) if locales_dir else LOCALES_DIR

    def load_locale(self, locale: str):
        """Load a locale JSON file from the shared LanguageLibrary directory."""
        file_path = self.locales_dir / f"{locale}.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.dictionaries[locale] = data
                logging.info(f"[UmLang-Py] Loaded locale '{locale}' successfully.")
        except Exception as e:
            logging.error(f"[UmLang-Py] Failed to load locale '{locale}' from {file_path}: {e}")

    def set_locale(self, locale: str):
        if locale in self.dictionaries:
            self.current_locale = locale
        else:
            logging.warning(f"[UmLang-Py] Locale '{locale}' not loaded. Retaining '{self.current_locale}'.")

    def t(self, path_str: str, params: dict = None) -> str:
        """Translate a dot-notation key with optional parameter interpolation."""
        if params is None:
            params = {}
            
        keys = path_str.split('.')
        
        # 1. Try current locale
        translation = self._resolve_key(self.dictionaries.get(self.current_locale), keys)
        
        # 2. Fall back to default locale
        if translation is None and self.current_locale != self.default_locale:
            translation = self._resolve_key(self.dictionaries.get(self.default_locale), keys)
            
        if translation is None:
            return f"[missing: {path_str}]"
            
        # 3. Interpolate parameters (e.g., {unit_id})
        for key, val in params.items():
            translation = translation.replace(f"{{{key}}}", str(val))
            
        return translation

    def _resolve_key(self, obj, keys):
        for key in keys:
            if isinstance(obj, dict) and key in obj:
                obj = obj[key]
            else:
                return None
        return obj


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

    # Annon Research Engine Modules
    ("propaganda analyzer", "linguistic analyzer", "propaganda filter", "analyze text"): "../research_engine/linguistic_propaganda_analyzer.py",
    ("legal interpreter", "constitutional interpreter", "textualist interpreter", "legal analysis"): "../research_engine/constitutional_legal_interpreter.py",
    ("threshold warning", "officer threshold warning", "warrant audit", "entry safety check", "threshold hazard"): "../research_engine/officer_threshold_warning_engine.py",

    # Java Ballistics Module (Trust-Main)
    ("ballistic video analysis", "java ballistics", "trust ballistics"): "../../Trust-Main/asset/java/ballisticVideoAnalysis",

    # Non-Ballistic Forensic AI, Scene Analysis & Physics
    ("scene analysis", "forensic scene analysis", "scene reconstruction"): "../../Trust-Main/asset/py/ferensics-ai",
    ("forensic physics", "scene physics", "basic forensics", "physics"): "../../Trust-Main/asset/py/ferensics-ai/ferensics _physcs.py",
    ("forensic server", "annon ai server", "ferensics ai server"): "../../Trust-Main/asset/py/ferensics-ai/ferensicAIserver.py",
    ("video ballistics", "ballistics"): "../../Trust-Main/asset/py/ferensics-ai/video_ballistics.py",
    ("ballistics comparator",): "../../Trust-Main/asset/py/ferensics-ai/ballistics_comparator.py",
    ("train forensic slm", "train slm"): "../../Trust-Main/asset/py/ferensics-ai/train_forensic_slm.py",
    ("sft trainer", "trainer"): "../../Trust-Main/asset/py/ferensics-ai/SFTTrainer.py",

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
            logging.warning(f"⚠️ Warning: Failed to load dynamic vocab: {e}")
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
        logging.info(f"🧠 Dynamic Learning Updated: '{cleaned}' ➔ {target_rel_path}")
    except Exception as e:
        logging.error(f"❌ Failed to save learned vocab: {e}")


@lru_cache(maxsize=1)
def build_script_index() -> dict[str, Path]:
    """Builds and caches the complete mapping of normalized phrases to absolute script Paths."""
    index: dict[str, Path] = {}

    # 1. Process static RAW_ALIAS_MAP
    for aliases, rel_path in RAW_ALIAS_MAP.items():
        resolved_path = (UTILS_DIR / rel_path).resolve()
        for alias in aliases:
            index[normalize(alias)] = resolved_path

    # 2. Process dynamic learned vocabulary
    learned = load_learned_vocab()
    for phrase, rel_path in learned.items():
        resolved_path = (UTILS_DIR / rel_path).resolve()
        index[normalize(phrase)] = resolved_path

    return index


class VoiceCommandRouter:
    """Unified voice command router integrating static aliases, dynamic learning, and UmLang."""
    def __init__(self, lang_library: UmLanguageLibrary | None = None):
        self.lang = lang_library or UmLanguageLibrary()
        self.commands = {}
        self._register_default_commands()

    def register_command(self, action_key: str, callback):
        """Register a programmatic action handler."""
        self.commands[action_key] = callback

    def handle_voice_input(self, spoken_text: str) -> bool:
        """Evaluates transcription against locale dictionaries or local script mappings."""
        cleaned_input = normalize(spoken_text)

        # 1. Check multi-language JSON schema via UmLang first
        for action_key in self.commands.keys():
            translation_key = f"voice.commands.{action_key}"
            localized_phrase = normalize(self.lang.t(translation_key))
            if localized_phrase and localized_phrase in cleaned_input:
                logging.info(f"[VoiceRouter] Matched action '{action_key}' via locale '{self.lang.current_locale}'")
                self.commands[action_key]()
                return True

        # 2. Check local script index and alias map
        script_index = build_script_index()
        if cleaned_input in script_index:
            target_path = script_index[cleaned_input]
            logging.info(f"[VoiceRouter] Executing script target: {target_path}")
            self._execute_target(target_path)
            return True

        # 3. Fuzzy match fallback
        matches = difflib.get_close_matches(cleaned_input, script_index.keys(), n=1, cutoff=0.75)
        if matches:
            best_match = matches[0]
            target_path = script_index[best_match]
            logging.info(f"[VoiceRouter] Fuzzy matched '{cleaned_input}' -> '{best_match}': {target_path}")
            self._execute_target(target_path)
            return True

        logging.warning(f'[VoiceRouter] Unrecognized voice command: "{spoken_text}"')
        return False

    def _execute_target(self, path: Path):
        if not path.exists():
            logging.error(f"❌ Target path does not exist: {path}")
            return
        
        if path.is_file():
            if path.suffix == ".py":
                subprocess.run([sys.executable, str(path)], check=False)
            else:
                logging.info(f"📁 Opening asset/file path: {path}")
        elif path.is_dir():
            logging.info(f"📂 Accessing directory module: {path}")

    def _register_default_commands(self):
        self.register_command('secure_device', lambda: logging.info("Executing: Lockdown unit and sealing telemetry."))
        self.register_command('save_evidence', lambda: logging.info("Executing: Capturing scene snapshot and recording chain of custody."))


if __name__ == "__main__":
    i18n = UmLanguageLibrary(default_locale='en')
    i18n.load_locale('en')
    i18n.load_locale('es')

    router = VoiceCommandRouter(i18n)
    
    # Test routing execution
    router.handle_voice_input("validate badge")
    router.handle_voice_input("Please lockdown unit immediately")
