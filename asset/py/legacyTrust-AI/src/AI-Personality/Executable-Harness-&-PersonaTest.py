"""Backwards-compatible entrypoint; see test_persona.py."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("test_persona.py")), run_name="__main__")
