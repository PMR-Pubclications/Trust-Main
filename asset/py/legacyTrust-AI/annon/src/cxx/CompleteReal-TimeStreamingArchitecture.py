import re
import asyncio
import json
import numpy as np
import onnxruntime as ort
import pyaudio
import websockets

# ==========================================
# CONFIGURATION
# ==========================================
MODEL_PATH = "my_custom_voice.onnx"
SAMPLE_RATE = 22050  # Must match Piper model config (usually 16000 or 22050 Hz)
CHANNELS = 1
SAMPLE_WIDTH = 2     # 16-bit PCM (2 bytes per sample)
# ==========================================


class PiperStreamingSynthesizer:
    def __init__(self, model_path: str):
        # Configure ONNX Runtime session for fast GPU/CPU inference
        opts = ort.SessionOptions()
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        self.session = ort.InferenceSession(model_path, opts, providers=providers)
        
        # Simple character/phoneme ID map stub (replace with piper_phonemize/espeak)
        # In production, use `piper_phonemize.phonemize_espeak(text, 'en-us')`
        self.phoneme_id_map = {c: idx + 1 for idx, c in enumerate("abcdefghijklmnopqrstuvwxyz .?!,")}

    def text_to_phoneme_ids(self, text: str) -> list[int]:
        """Converts text string to sequence of phoneme IDs."""
        text_clean = text.lower().strip()
        return [self.phoneme_id_map.get(char, 1) for char in text_clean]

    def synthesize_chunk_to_pcm(self, text_chunk: str) -> bytes:
        """Runs ONNX inference on a text chunk and returns 16-bit PCM bytes."""
        phoneme_ids = self.text_to_phoneme_ids(text_chunk)
        if not phoneme_ids:
            return b""

        x = np.array([phoneme_ids], dtype=np.int64)
        x_lengths = np.array([len(phoneme_ids)], dtype=np.int64)
        scales = np.array([0.667, 1.0, 0.8], dtype=np.float32)

        inputs = {
            "input": x,
            "input_lengths": x_lengths,
            "scales": scales,
        }

        outputs = self.session.run(None, inputs)
        audio_float32 = outputs[0].squeeze()

        # Scale float32 (-1.0 to 1.0) to 16-bit signed PCM integers
        audio_int16 = (audio_float32 * 32767).clip(-32768, 32767).astype(np.int16)
        return audio_int16.tobytes()


def chunk_text_stream(text: str, min_words: int = 3):
    """
    Splits text on clause and sentence boundaries (. , ! ? ; :)
    to yield short phrases suitable for sub-200ms latency synthesis.
    """
    pattern = re.compile(r'(?<=[.!?;,:])\s+')
    parts = pattern.split(text)

    buffer = ""
    for part in parts:
        buffer = f"{buffer} {part}".strip() if buffer else part
        # Yield if we have reached a reasonable word threshold
        if len(buffer.split()) >= min_words:
            yield buffer
            buffer = ""

    if buffer:
        yield buffer


# =====================================================================
# OPTION A: LOCAL REAL-TIME PLAYBACK VIA PYAUDIO
# =====================================================================
def stream_to_local_speakers(synth: PiperStreamingSynthesizer, full_text: str):
    """Synthesizes and plays audio chunks progressively using PyAudio."""
    p = pyaudio.PyAudio()
    audio_stream = p.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
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


async def start_websocket_server(synth: PiperStreamingSynthesizer, host="0.0.0.0", port=8765):
    """Launches an async WebSocket server for low-latency remote client streaming."""
    server = await websockets.serve(
        lambda ws: websocket_handler(ws, synth), 
        host, 
        port
    )
    print(f"Piper WebSocket Server listening on ws://{host}:{port}")
    await server.wait_closed()


if __name__ == "__main__":
    synthesizer = PiperStreamingSynthesizer(MODEL_PATH)
    
    sample_text = (
        "Welcome to real-time speech synthesis! By chunking the input text into small clauses, "
        "the system begins generating audio almost instantaneously. "
        "This approach provides low latency over local speakers and WebSockets."
    )

    # Run Local Speaker Stream
    stream_to_local_speakers(synthesizer, sample_text)

    # To run WebSocket server instead, uncomment below:
    # asyncio.run(start_websocket_server(synthesizer))
