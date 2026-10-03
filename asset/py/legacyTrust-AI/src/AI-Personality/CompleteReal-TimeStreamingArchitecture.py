import re
import json
import asyncio
from pathlib import Path

import numpy as np

import config
from audio_utils import chunk_text_stream
from piper_session import create_optimized_piper_session, synthesize_phonemes

CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit PCM (2 bytes per sample)

BOS, EOS, PAD = "^", "$", "_"


class PiperStreamingSynthesizer:
    """Streams Piper audio using the model's own .onnx.json (sample rate, phoneme map, scales)."""

    def __init__(self, model_path: str = config.PIPER_MODEL_PATH, config_path: str = None, device: str = "cuda"):
        config_path = config_path or f"{model_path}.json"
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Piper model config not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            self.model_config = json.load(f)

        self.sample_rate = int(self.model_config.get("audio", {}).get("sample_rate", config.DEFAULT_SAMPLE_RATE))
        self.phoneme_id_map = self.model_config["phoneme_id_map"]
        self.espeak_voice = self.model_config.get("espeak", {}).get("voice", "en-us")
        inference = self.model_config.get("inference", {})
        self.noise_scale = inference.get("noise_scale", 0.667)
        self.length_scale = inference.get("length_scale", 1.0)
        self.noise_w = inference.get("noise_w", 0.8)

        self.session = create_optimized_piper_session(model_path, device=device)

    def text_to_phoneme_ids(self, text: str) -> list:
        """Phonemizes with espeak (piper_phonemize) and maps to the model's phoneme IDs."""
        try:
            from piper_phonemize import phonemize_espeak
        except ImportError as e:
            raise RuntimeError("piper_phonemize is required for real Piper phonemization (pip install piper-phonemize)") from e

        ids = []
        for sentence in phonemize_espeak(text.strip(), self.espeak_voice):
            ids.extend(self.phoneme_id_map[BOS])
            for ph in sentence:
                if ph in self.phoneme_id_map:
                    ids.extend(self.phoneme_id_map[ph])
                    ids.extend(self.phoneme_id_map[PAD])
            ids.extend(self.phoneme_id_map[EOS])
        return ids

    def synthesize_chunk_to_pcm(self, text_chunk: str) -> bytes:
        """Runs ONNX inference on a text chunk and returns 16-bit PCM bytes."""
        phoneme_ids = self.text_to_phoneme_ids(text_chunk)
        if not phoneme_ids:
            return b""
        audio, _ = synthesize_phonemes(
            self.session, phoneme_ids, self.noise_scale, self.length_scale, self.noise_w
        )
        return (audio * 32767).clip(-32768, 32767).astype(np.int16).tobytes()


# =====================================================================
# OPTION A: LOCAL REAL-TIME PLAYBACK VIA PYAUDIO
# =====================================================================
def stream_to_local_speakers(synth: PiperStreamingSynthesizer, full_text: str):
    """Synthesizes and plays audio chunks progressively using PyAudio."""
    import pyaudio
    p = pyaudio.PyAudio()
    audio_stream = p.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=synth.sample_rate,
        output=True,
        frames_per_buffer=1024
    )

    print("\n--- Starting Local Audio Stream ---")
    for chunk_idx, text_chunk in enumerate(chunk_text_stream(full_text)):
        print(f"[Chunk {chunk_idx + 1}] Synthesizing: '{text_chunk}'")
        pcm_data = synth.synthesize_chunk_to_pcm(text_chunk)
        if pcm_data:
            audio_stream.write(pcm_data)

    audio_stream.stop_stream()
    audio_stream.close()
    p.terminate()
    print("--- Playback Complete ---")


# =====================================================================
# OPTION B: NETWORK STREAMING SERVER VIA WEBSOCKETS
# =====================================================================
async def websocket_handler(websocket, synth: PiperStreamingSynthesizer):
    """
    Listens for incoming text requests over WebSockets and streams back 
    raw PCM binary frames chunk-by-chunk as they finish inference.
    """
    async for message in websocket:
        try:
            data = json.loads(message)
            text = data.get("text", "")
            if not text:
                continue

            print(f"\n[WebSocket Client] Request received: {text[:40]}...")

            for chunk_idx, text_chunk in enumerate(chunk_text_stream(text)):
                pcm_bytes = synth.synthesize_chunk_to_pcm(text_chunk)
                if pcm_bytes:
                    # Send binary PCM frames progressively
                    await websocket.send(pcm_bytes)
                    await asyncio.sleep(0.001)  # Yield execution back to event loop

            # Send a zero-length EOF marker frame to notify the client stream ended
            await websocket.send(b"")
            print("[WebSocket Client] Stream finished.")

        except Exception as e:
            print(f"WebSocket Error: {e}")


async def start_websocket_server(synth: PiperStreamingSynthesizer, host="127.0.0.1", port=8765):
    """Launches an async WebSocket server for low-latency remote client streaming."""
    import websockets
    server = await websockets.serve(
        lambda ws: websocket_handler(ws, synth),
        host,
        port
    )
    print(f"Piper WebSocket Server listening on ws://{host}:{port}")
    await server.wait_closed()


if __name__ == "__main__":
    synthesizer = PiperStreamingSynthesizer()
    
    sample_text = (
        "Welcome to real-time speech synthesis! By chunking the input text into small clauses, "
        "the system begins generating audio almost instantaneously. "
        "This approach provides low latency over local speakers and WebSockets."
    )

    # Run Local Speaker Stream
    stream_to_local_speakers(synthesizer, sample_text)

    # To run WebSocket server instead, uncomment below:
    # asyncio.run(start_websocket_server(synthesizer))
