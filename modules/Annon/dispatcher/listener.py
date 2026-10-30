#!/usr/bin/env python3
# ==========================================
# TRUST-MAIN AUDIO DISPATCH LISTENER
# ==========================================
# Bridges Trust-Main command inputs over to the 
# standalone diagnostic repository's bash script.

import os
import sys
import subprocess
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TrustMainDispatcher")

class AnnonCommandDispatcher:
    """Listens for or receives commands in Trust-Main and dispatches them to the diagnostic core."""
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        # Resolve path to the sibling diagnostic repository (assuming standard workspace layout)
        self.workspace_root = os.path.abspath(os.path.join(self.script_dir, "..", "..", ".."))
        
        # Look for the diagnostic repo's bash trigger (adjust folder name if your diagnostic repo has a specific name)
        # Assuming the diagnostic repo is a sibling folder in the workspace root
        self.diagnostic_script = self._locate_diagnostic_script()

    def _locate_diagnostic_script(self) -> str:
        # Search workspace directories for the listen_and_execute script
        for root, dirs, files in os.walk(self.workspace_root):
            if "listen_and_execute.sh" in files:
                return os.path.join(root, "listen_and_execute.sh")
        return ""

    def dispatch(self, spoken_command: str):
        """Sends the command to the standalone diagnostic core's bash execution script."""
        cleaned_command = spoken_command.strip()
        logger.info(f"Trust-Main received command: '{cleaned_command}'")

        if not self.diagnostic_script or not os.path.exists(self.diagnostic_script):
            logger.error("Could not find 'listen_and_execute.sh' in the diagnostic repository.")
            print(f"[Audio Feedback]: Error. Diagnostic execution bridge not found.")
            return False

        # Execute the diagnostic repo's bash script via subprocess
        try:
            logger.info(f"Dispatching to diagnostic core: {self.diagnostic_script}")
            result = subprocess.run(
                [self.diagnostic_script, cleaned_command],
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Diagnostic dispatch failed: {e.stderr.strip()}")
            return False


if __name__ == "__main__":
    dispatcher = AnnonCommandDispatcher()
    
    # Example test call simulating a voice input picked up by Trust-Main
    test_input = sys.argv[1] if len(sys.argv) > 1 else "annon, how are you feeling?"
    dispatcher.dispatch(test_input)
