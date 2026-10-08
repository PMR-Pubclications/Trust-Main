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
- Dynamic Persistent Vocabulary Learning & Voice Routing
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
# Repository: https://github.com/PMR-Pubclications/Trust-Main/
# ==============================================================================
UTILS_DIR = Path(__file__).resolve().parent           # modules/Annon/scripts/utils/
SCRIPTS_DIR = UTILS_DIR.parent                         # modules/Annon/scripts/
RESEARCH_ENGINE_DIR = SCRIPTS_DIR / "research_engine" # modules/Annon/scripts/research_engine/
ANNON_ROOT = SCRIPTS_DIR.parent                        # modules/Annon/
MODULES_ROOT = ANNON_ROOT.parent                       # modules/

# External Forensics & Authentication Asset Paths (Trust-Main Repository)
# Note: Root directory uses single 'asset' folder convention (Trust-Main/asset/)
TRUST_MAIN_DIR = MODULES_ROOT / "Trust-Main"
JAVA_ASSET_DIR = TRUST_MAIN_DIR / "asset" / "java"
BALLISTIC_JAVA_DIR = JAVA_ASSET_DIR / "ballisticVideoAnalysis"
BADGE_CONTROLLER_FILE = JAVA_ASSET_DIR / "BadgeAssignmentController.java"
FORENSICS_PY_DIR = TRUST_MAIN_DIR / "asset" / "py" / "ferensics-ai"

# Dynamic Learning Storage File
LEARNED_VOCAB_FILE = UTILS_DIR / "learned_vocab.json"

# GitHub Remote Reference URI
RESEARCH_ENGINE_URL = "https://github.com/PMR-Pubclications/Trust-Main/tree/main/modules%2FAnnon%2Fscripts%2Fresearch_engine"

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

    # Annon Research Engine Modules (modules/Annon/scripts/research_engine/)
    ("propaganda analyzer", "linguistic analyzer", "propaganda filter", "analyze text"): "../research_engine/linguistic_propaganda_analyzer.py",
    ("legal interpreter", "constitutional interpreter", "textualist interpreter", "legal analysis"): "../research_engine/constitutional_legal_interpreter.py",
    ("threshold warning", "officer threshold warning", "warrant audit", "entry safety check", "threshold hazard"): "../research_engine/officer_threshold_warning_engine.py",

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
        print(f"❌ Failed to save
