import sys
import os
import time
import asyncio
import logging
import tempfile
import pygame
import speech_recognition as sr
from typing import Optional

# Import Anon system partner from previous module
from anon_system_partner import AnonSystemPartner

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AnonVoice")


class AnonVoiceEngine:
    """
    Handles Text-to-Speech synthesis tuned for Anon's voice profile:
    Young male, Midwestern timber, steady pace.
    """

    def __init__(
        self,
        voice_id: str = "en-US-GuyNeural",  # Alternative: "en-US-ChristopherNeural"
        rate: str = "-5%",                   # Slightly relaxed pace
        pitch: str = "-4Hz",                 # Natural, grounded low-mid resonance
        volume: str = "+0%"
    ):
        self.voice_id = voice_id
        self.rate = rate
        self.pitch = pitch
        self.volume = volume

        # Initialize pygame audio mixer
        pygame.mixer.init()

    async def _generate_audio_file(self, text: str, output_path: str):
        """Synthesizes speech using edge-tts with custom pitch and rate SSML settings."""
        import edge_tts

        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice_id,
            rate=self.rate,
            pitch=self.pitch,
            volume=self.volume
        )
        await communicate.save(output_path)

    def speak(self, text: str):
        """Renders text to audio and plays it through the primary default output device (speakers)."""
        if not text or not text.strip():
            return

        logger.info(f"Anon Speaking: \"{text}\"")

        # Create temporary MP3 file for playback
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_filename = fp.name

        try:
            # Run async TTS generator in sync wrapper
            asyncio.run(self._generate_audio_file(text, temp_filename))

            # Play back audio via Pygame
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.unload()

        except Exception as e:
            logger.error(f"Failed to synthesize or play audio: {e}")
        finally:
            if os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                except Exception:
                    pass


class AnonMicrophoneListener:
    """
    Captures live audio from default microphone, applies background ambient noise calibration,
    and converts speech to text.
    """

    def __init__(self, energy_threshold: int = 300, pause_threshold: float = 0.8):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.pause_threshold = pause_threshold
        self.microphone = sr.Microphone()

        logger.info("Calibrating microphone for ambient background noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
        logger.info("Microphone calibrated and ready.")

    def listen(self) -> Optional[str]:
        """Listens for an utterance and returns recognized plain text."""
        with self.microphone as source:
            logger.info("Listening... (Speak into your mic)")
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                logger.info("Processing speech input...")
                text = self.recognizer.recognize_google(audio)
                logger.info(f"You said: \"{text}\"")
                return text
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                logger.warning("Could not understand audio input.")
                return None
            except sr.RequestError as e:
                logger.error(f"Speech recognition service error: {e}")
                return None


class AnonHardwareBridge:
    """
    Full-duplex loop linking Microphone Input -> Anon Persona Brain -> Speaker Output.
    """

    def __init__(self):
        self.partner = AnonSystemPartner()
        self.voice = AnonVoiceEngine()
        self.listener = AnonMicrophoneListener()

    def start_voice_loop(self):
        """Starts continuous interactive voice loop."""
        greeting = "Speaker and mic are online. I'm listening—what are we working on today?"
        print(f"\nAnon: {greeting}\n")
        self.voice.speak(greeting)

        while True:
            try:
                user_text = self.listener.listen()

                if not user_text:
                    continue

                # Exit trigger
                if any(k in user_text.lower() for k in ["quit", "exit", "shut down", "goodnight"]):
                    farewell = "Alright, shutting down the mic loop. Stay safe out there."
                    print(f"\nAnon: {farewell}\n")
                    self.voice.speak(farewell)
                    break

                # Process user request through Anon's system partner
                response_text = self.partner.respond_to_user(user_text)
                print(f"\nAnon: {response_text}\n")

                # Output response to speakers
                self.voice.speak(response_text)

            except KeyboardInterrupt:
                logger.info("Voice bridge terminated by user.")
                break
            except Exception as e:
                logger.error(f"Error in voice loop: {e}")
                time.sleep(1)


if __name__ == "__main__":
    bridge = AnonHardwareBridge()
    bridge.start_voice_loop()
