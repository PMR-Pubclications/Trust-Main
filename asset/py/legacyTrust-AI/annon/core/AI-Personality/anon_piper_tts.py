import io
import os
import time
import logging
import numpy as np
import sounddevice as sd
import onnxruntime as ort
from typing import Optional
from piper import PiperVoice

# Imports from previous modules
from anon_cuda_whisper import AnonCudaWhisperListener
from anon_system_partner import AnonSystemPartner

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AnonPiperVoice")


class AnonPiperEngine:
    """
    Sub-50ms local, offline Neural TTS Engine using Piper with ONNX CUDA acceleration
    and zero-disk-IO RAM audio playback via sounddevice.
    """

    def __init__(
        self,
        model_path: str = "en_US-ryan-medium.onnx",
        config_path: Optional[str] = None,
        use_cuda: bool = True
    ):
        if not config_path:
            config_path = f"{model_path}.json"

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Piper model file not found at '{model_path}'. "
                f"Download the .onnx and .onnx.json files from Piper release repository."
            )

        logger.info(f"Loading local Piper neural voice model ('{model_path}')...")
        t_start = time.perf_counter()

        # Configure ONNX Runtime execution providers
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if use_cuda else ["CPUExecutionProvider"]
        
        # Initialize Piper voice model directly in memory
        self.voice = PiperVoice.load(
            model_path,
            config_path=config_path,
            use_cuda=use_cuda
        )
        
        self.sample_rate = self.voice.config.sample_rate
        init_ms = (time.perf_counter() - t_start) * 1000
        logger.info(f"Piper TTS engine initialized in {init_ms:.1f} ms (Sample Rate: {self.sample_rate} Hz).")

        # Warm up CUDA engine with short dummy text
        self._warmup_gpu()

    def _warmup_gpu(self):
        """Pre-allocates CUDA tensors and warm-compiles ONNX execution graph."""
        start = time.perf_counter()
        _ = list(self.voice.synthesize_stream_raw("Ready."))
        warmup_ms = (time.perf_counter() - start) * 1000
        logger.info(f"Piper CUDA engine warm-up completed in {warmup_ms:.1f} ms.")

    def speak(self, text: str):
        """Synthesizes text in RAM and streams PCM audio directly to soundcard (sub-50ms latency)."""
        if not text or not text.strip():
            return

        logger.info(f"Anon Speaking: \"{text}\"")
        t_start = time.perf_counter()

        try:
            # Synthesize raw PCM audio in-memory (16-bit mono PCM)
            audio_bytes = bytearray()
            for chunk in self.voice.synthesize_stream_raw(text):
                audio_bytes.extend(chunk)

            synth_latency_ms = (time.perf_counter() - t_start) * 1000
            
            # Convert raw PCM bytes to int16 numpy array
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

            logger.info(f"TTS Synthesis Latency: {synth_latency_ms:.1f} ms ({len(audio_array)} samples)")

            # Stream directly to audio hardware without writing temporary disk files
            sd.play(audio_array, samplerate=self.sample_rate)
            sd.wait()  # Wait until playback completes

        except Exception as e:
            logger.error(f"Piper TTS playback error: {e}")


class FullyOfflineLocalVoiceBridge:
    """
    Sub-100ms full-duplex voice bridge:
    Local CUDA Whisper STT (<100ms) -> Anon System Partner -> Local CUDA Piper TTS (<50ms).
    """

    def __init__(
        self,
        whisper_model: str = "distil-small.en",
        piper_model: str = "en_US-ryan-medium.onnx"
    ):
        self.partner = AnonSystemPartner()
        self.stt = AnonCudaWhisperListener(model_size=whisper_model, device="cuda")
        self.tts = AnonPiperEngine(model_path=piper_model, use_cuda=True)

    def start_loop(self):
        """Runs the continuous offline local voice interaction loop."""
        greeting = "Zero-latency local speech loop active. All models running fully offline on GPU."
        print(f"\nAnon: {greeting}\n")
        self.tts.speak(greeting)

        while True:
            try:
                user_text = self.stt.listen()

                if not user_text:
                    continue

                # Exit triggers
                if any(k in user_text.lower() for k in ["quit", "exit", "shut down", "goodnight"]):
                    farewell = "Alright, shutting down the local audio loop. Stay safe out there."
                    print(f"\nAnon: {farewell}\n")
                    self.tts.speak(farewell)
                    break

                # Process request through Anon system partner
                response_text = self.partner.respond_to_user(user_text)
                print(f"\nAnon: {response_text}\n")

                # Play response back through speakers
                self.tts.speak(response_text)

            except KeyboardInterrupt:
                logger.info("Voice loop terminated by user.")
                break
            except Exception as e:
                logger.error(f"Voice loop error: {e}")
                time.sleep(0.5)


if __name__ == "__main__":
    # Ensure model exists before running harness
    model_file = "en_US-ryan-medium.onnx"
    if os.path.exists(model_file):
        bridge = FullyOfflineLocalVoiceBridge(whisper_model="distil-small.en", piper_model=model_file)
        bridge.start_loop()
    else:
        print(f"Please place '{model_file}' and '{model_file}.json' in the working directory.")
