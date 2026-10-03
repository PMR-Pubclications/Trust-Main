import io
import time
import torch
import logging
import numpy as np
import speech_recognition as sr
from typing import Optional
from faster_whisper import WhisperModel

logger = logging.getLogger("AnonCudaVoice")


class AnonCudaWhisperListener:
    """
    Sub-100ms local STT engine using faster-whisper compiled for CUDA / CTranslate2.
    """

    def __init__(
        self,
        model_size: str = "distil-small.en",  # Options: 'tiny.en', 'distil-small.en', 'small.en'
        device: str = "cuda",
        compute_type: str = "float16",        # FP16 utilizes NVIDIA Tensor Cores
        device_index: int = 0,
        energy_threshold: int = 300,
        pause_threshold: float = 0.5          # Tighter pause threshold for faster end-of-speech detection
    ):
        # 1. Verify CUDA availability
        if not torch.cuda.is_available() and device == "cuda":
            logger.warning("CUDA not detected by PyTorch! Falling back to CPU.")
            device = "cpu"
            compute_type = "int8"

        logger.info(f"Initializing CUDA Whisper engine ('{model_size}' on {device}:{device_index} [{compute_type}])...")
        
        # 2. Instantiate CTranslate2 CUDA pipeline
        self.model = WhisperModel(
            model_size_or_path=model_size,
            device=device,
            device_index=device_index,
            compute_type=compute_type
        )

        # 3. CUDA Kernel Warmup (Eliminates cold-start latency on first spoken command)
        self._warmup_gpu()

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.pause_threshold = pause_threshold
        self.microphone = sr.Microphone()

        logger.info("Calibrating mic ambient floor...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
        logger.info("CUDA Whisper listener primed and ready.")

    def _warmup_gpu(self):
        """Runs a 0.5s silent audio tensor through GPU pipeline to allocate VRAM and compile CUDA kernels."""
        start = time.perf_counter()
        dummy_pcm = np.zeros(8000, dtype=np.float32)  # 0.5s of 16kHz silence
        _, _ = self.model.transcribe(dummy_pcm, beam_size=1, language="en")
        warmup_ms = (time.perf_counter() - start) * 1000
        logger.info(f"CUDA kernel warmup completed in {warmup_ms:.1f} ms.")

    def listen(self) -> Optional[str]:
        """Listens for an utterance and executes high-speed GPU transcription."""
        with self.microphone as source:
            logger.info("Listening... (CUDA Engine Active)")
            try:
                # Capture audio stream
                audio_data = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                
                t_start = time.perf_counter()
                wav_buffer = io.BytesIO(audio_data.get_wav_data())

                # 4. Latency-optimized inference settings
                segments, info = self.model.transcribe(
                    wav_buffer,
                    beam_size=1,                       # Greedy decoding (Fastest execution)
                    best_of=1,                         # Disable sample candidate evaluation
                    temperature=0.0,                   # Deterministic greedy search
                    condition_on_previous_text=False,  # Prevents repetitive looping and cuts state overhead
                    vad_filter=True,                   # Silences non-speech frames before passing to transformer
                    vad_parameters=dict(
                        min_silence_duration_ms=300    # Cuts off processing quickly after user stops speaking
                    ),
                    language="en"
                )

                transcription = " ".join([s.text for s in segments]).strip()
                latency_ms = (time.perf_counter() - t_start) * 1000

                if transcription:
                    logger.info(f"Local STT ({latency_ms:.1f} ms): \"{transcription}\"")
                    return transcription
                return None

            except sr.WaitTimeoutError:
                return None
            except Exception as e:
                logger.error(f"CUDA transcription error: {e}")
                return None
