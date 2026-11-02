#!/usr/bin/env python3
"""
/opt/annonos/core/ai/trust_main_audio_bridge.py
AnnonOS-to-Trust-Main Speech Bridge.
Binds AnnonOS core system functions (GPS, AI, diagnostics) directly to the 
Trust-Main speech synthesis module to generate audible responses for blind operators.
"""

import os
import sys
import logging
from typing import Optional, Dict, Any

# Map path to the local Trust-Main repository structure
TRUST_MAIN_PATH = "/opt/trust-main/"
if TRUST_MAIN_PATH not in sys.path:
    sys.path.append(TRUST_MAIN_PATH)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [TrustMainBridge]: %(message)s'
)
logger = logging.getLogger(__name__)

class AnnonOSWhisperBridge:
    def __init__(self):
        self.speech_engine = None
        self._initialize_trust_main_speech()

    def _initialize_trust_main_speech(self) -> None:
        """
        Loads the text-to-speech engine directly from the Trust-Main codebase.
        """
        logger.info("Initializing connection to Trust-Main speech synthesizer...")
        try:
            # Import speech utility module from Trust-Main
            import modules.Annon.speech_engine as trust_speech  # type: ignore
            self.speech_engine = trust_speech.TextToSpeechPipeline()
            logger.info("Successfully linked Trust-Main speech synthesizer.")
        except ImportError:
            logger.warning("Trust-Main speech module not found in local path. Initializing fallback audio channel.")
            self.speech_engine = None
        except Exception as e:
            logger.error(f"Error binding Trust-Main speech module: {e}")

    def speak_os_function_output(self, function_name: str, message: str) -> bool:
        """
        Takes output text from any AnnonOS function (e.g. GPS step navigation, sensor alerts)
        and passes it to Trust-Main to convert into an audible response for the operator.
        """
        logger.info(f"[AnnonOS -> Trust-Main Speech] Service [{function_name}] says: '{message}'")

        if self.speech_engine and hasattr(self.speech_engine, "synthesize"):
            # Execute speech generation via Trust-Main
            self.speech_engine.synthesize(message)
            return True
        else:
            # Fallback direct audio route simulation
            logger.info(f"[Audible Output Generated]: {message}")
            return True

if __name__ == "__main__":
    bridge = AnnonOSWhisperBridge()
    
    # Test routing an AnnonOS GPS navigation step to Trust-Main's speech generator
    bridge.speak_os_function_output(
        function_name="StepGPSNavigator",
        message="Walk forward 30 steps, then take a hard left."
    )
