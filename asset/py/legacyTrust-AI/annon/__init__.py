from .hardware.bridge import HardwareBridge
from .core.personality import AIPersonality

class AnnonEngine:
    def __init__(self, config_path: str = None):
        self.hardware = HardwareBridge()
        self.ai = AIPersonality(config_path=config_path)
        self._is_running = False

    def initialize(self) -> bool:
        """Initialize C++ hardware engine and load AI models."""
        hw_ok = self.hardware.init_devices()
        ai_ok = self.ai.load_models()
        self._is_running = hw_ok and ai_ok
        return self._is_running

    def process_frame(self, frame_data):
        """Pass video/audio telemetry into Annon core."""
        if not self._is_running:
            raise RuntimeError("AnnonEngine is not initialized.")
        return self.ai.evaluate(frame_data)

    def shutdown(self):
        self.hardware.release()
        self._is_running = False
