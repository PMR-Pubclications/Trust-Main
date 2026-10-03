import audio_video_engine

class HardwareInterface:
    def __init__(self):
        self.engine = audio_video_engine.HardwareController()

    def start(self):
        self.engine.initialize_hardware()
        self.engine.start_capture()
