"""ONNX Runtime session setup and raw inference for Piper models."""
import time
from typing import Optional, Tuple

import numpy as np
import onnxruntime as ort


def create_optimized_piper_session(
    model_path: str,
    device: str = "cuda",
    cpu_threads: int = 4,
) -> ort.InferenceSession:
    """
    Creates an ONNX Runtime InferenceSession tailored for low-latency
    Piper TTS inference across CUDA, TensorRT, DirectML, OpenVINO, or CPU.
    """
    options = ort.SessionOptions()
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.intra_op_num_threads = cpu_threads
    options.inter_op_num_threads = 1

    providers = []
    dev = device.lower()
    if dev == "cuda":
        providers.append(("CUDAExecutionProvider", {
            "device_id": 0,
            "arena_extend_strategy": "kNextPowerOfTwo",
            "gpu_mem_limit": 2 * 1024 * 1024 * 1024,
            "cudnn_conv_algo_search": "EXHAUSTIVE",
            "do_copy_in_default_stream": True,
        }))
    elif dev == "tensorrt":
        providers.append(("TensorrtExecutionProvider", {
            "device_id": 0,
            "trt_max_workspace_size": 2147483648,
            "trt_fp16_enable": True,
            "trt_engine_cache_enable": True,
            "trt_engine_cache_path": "./trt_cache",
        }))
        providers.append(("CUDAExecutionProvider", {}))
    elif dev == "directml":
        providers.append(("DmlExecutionProvider", {"device_id": 0}))
    elif dev == "openvino":
        providers.append(("OpenVINOExecutionProvider", {"device_type": "CPU_FP32", "num_of_threads": cpu_threads}))
    providers.append(("CPUExecutionProvider", {}))

    # Drop providers this onnxruntime build doesn't offer (avoids load warnings/errors)
    available = set(ort.get_available_providers())
    providers = [p for p in providers if p[0] in available] or [("CPUExecutionProvider", {})]

    session = ort.InferenceSession(model_path, options, providers=providers)
    print(f"Loaded Piper session with active provider: {session.get_providers()[0]}")
    return session


def synthesize_phonemes(
    session: ort.InferenceSession,
    phoneme_ids: list,
    noise_scale: float = 0.667,
    length_scale: float = 1.0,
    noise_w: float = 0.8,
    speaker_id: Optional[int] = None,
) -> Tuple[np.ndarray, float]:
    """Runs Piper ONNX inference; returns (float32 audio, latency in ms)."""
    inputs = {
        "input": np.array([phoneme_ids], dtype=np.int64),
        "input_lengths": np.array([len(phoneme_ids)], dtype=np.int64),
        "scales": np.array([noise_scale, length_scale, noise_w], dtype=np.float32),
    }
    if "sid" in [i.name for i in session.get_inputs()] and speaker_id is not None:
        inputs["sid"] = np.array([speaker_id], dtype=np.int64)

    start = time.perf_counter()
    outputs = session.run(None, inputs)
    latency_ms = (time.perf_counter() - start) * 1000
    return outputs[0].squeeze(), latency_ms
