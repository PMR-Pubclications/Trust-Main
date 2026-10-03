from anon_piper_tts import AnonPiperEngine

# Load fine-tuned custom voice model
custom_tts = AnonPiperEngine(
    model_path="custom_voice.onnx",
    config_path="custom_voice.onnx.json",
    use_cuda=True
)

custom_tts.speak("Custom neural voice model loaded and verified.")
