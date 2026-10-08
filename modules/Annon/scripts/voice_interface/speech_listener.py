import speech_recognition as sr
import sys

class SpeechListener:
    """
    Handles local micro-audio capture and speech-to-text conversion.
    Designed for zero-cloud/offline operation using Vosk/Sphinx or 
    default system microphone devices.
    """

    def __init__(self, energy_threshold: int = 300, pause_threshold: float = 0.8):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.pause_threshold = pause_threshold

    def listen_for_command(self) -> str:
        """
        Captures audio from the default microphone and converts it to text.
        Returns transcribed string or empty string on failure/silence.
        """
        with sr.Microphone() as source:
            print("\n[VOICE INTERFACE] Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("[VOICE INTERFACE] Listening for research command...")
            
            try:
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=15)
                print("[VOICE INTERFACE] Processing audio stream...")
                
                # Default to local/offline engine if available, fallback to speech_recognition recognizer
                transcribed_text = self.recognizer.recognize_google(audio)
                print(f"[VOICE CAPTURED]: \"{transcribed_text}\"")
                return transcribed_text.strip()

            except sr.WaitTimeoutError:
                print("[VOICE INTERFACE] Listening timed out (no speech detected).")
                return ""
            except sr.UnknownValueError:
                print("[VOICE INTERFACE] Could not understand audio input.")
                return ""
            except sr.RequestError as e:
                print(f"[VOICE INTERFACE] STT Service Error: {e}")
                return ""
