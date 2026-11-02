#!/usr/bin/env python3
"""
/opt/annon-os/Trust-Main/scripts/hardware_layer/hardware_loader.py
Loads and interfaces with the compiled AudioVideoEngine-CPP shared library,
managing hardware sensor initialization and real-time thermal/telemetry streaming.
"""

import os
import sys
import logging
import numpy as np
from typing import Optional, List, Union

# Configure logging for forensic telemetry
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [HardwareLoader]: %(message)s'
)
logger = logging.getLogger(__name__)

class HardwareEngineInterface:
    def __init__(self, lib_path: str = "/opt/annon-os/AudioVideoEngine-CPP/build/"):
        self.lib_path = lib_path
        self.engine = None
        self.camera = None
        self._load_compiled_engine()

    def _load_compiled_engine(self) -> None:
        """
        Dynamically imports the compiled C++ pybind11 shared library.
        """
        logger.info("Loading compiled AudioVideoEngineCPP shared library...")
        try:
            # Ensure path to shared object is in sys.path
            if self.lib_path not in sys.path:
                sys.path.append(self.lib_path)
            
            import AudioVideoEngineCPP as ave
            
            # Instantiate core engine and FLIR Boson wrapper
            self.engine = ave.AudioVideoEngineCore()
            self.camera = ave.FlirBosonCamera("/dev/video0")
            logger.info("AudioVideoEngineCPP loaded and bound successfully.")
            
        except ImportError as e:
            logger.critical(f"Failed to import AudioVideoEngineCPP binary module: {e}")
            logger.critical("Ensure the C++ project has been built via CMake before starting the kernel.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error initializing hardware engine: {e}")
            sys.exit(1)

    def initialize_system_sensors(self) -> bool:
        """
        Triggers low-level SPI/I2C register locks via the C++ engine.
        """
        logger.info("Initializing tactical hardware sensor buses...")
        if self.engine and self.engine.initialize_sensors():
            logger.info("Sensor buses initialized and locked.")
            return True
        return False

    def start_thermal_camera(self) -> bool:
        """
        Initializes the FLIR Boson thermal core stream.
        """
        logger.info("Initializing FLIR Boson thermal camera interface...")
        if self.camera and self.camera.initialize():
            logger.info("FLIR Boson thermal stream active.")
            return True
        logger.warning("Failed to initialize FLIR Boson camera.")
        return False

    def fetch_thermal_frame(self) -> Optional[np.ndarray]:
        """
        Captures the next high-resolution thermal frame as a direct NumPy array
        with zero-copy overhead.
        """
        if not self.camera:
            return None
        return self.camera.get_next_frame()

    def get_telemetry_burst(self) -> List[float]:
        """
        Retrieves high-frequency physical telemetry values.
        """
        if self.engine:
            return self.engine.capture_telemetry_frame()
        return []

if __name__ == "__main__":
    hw = HardwareEngineInterface()
    if hw.initialize_system_sensors():
        hw.start_thermal_camera()
        frame = hw.fetch_thermal_frame()
        if frame is not None:
            logger.info(f"Captured thermal frame dimensions: {frame.shape}, Mean Temp: {np.mean(frame):.2f}°C")
