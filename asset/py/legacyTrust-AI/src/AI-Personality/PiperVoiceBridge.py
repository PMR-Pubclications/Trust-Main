import config
from anon_piper_tts import AnonPiperEngine

if __name__ == "__main__":
    custom_tts = AnonPiperEngine(
        model_path=config.PIPER_MODEL_PATH,
        config_path=config.PIPER_CONFIG_PATH,
        use_cuda=True,
    )
    custom_tts.speak("Custom neural voice model loaded and verified.")
