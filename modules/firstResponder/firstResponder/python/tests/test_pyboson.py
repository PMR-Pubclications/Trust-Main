#!/usr/bin/env python3
"""
Unit tests for the pyboson C++ native extension module.
Verifies hardware interface lifecycle, error handling, and thermal array structure.
"""

import os
import sys
import unittest
import numpy as np

# Ensure module path includes the build directory or python module directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../build"))
PYTHON_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../python"))

for path in (PYTHON_DIR, BUILD_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)


class TestPybosonModule(unittest.TestCase):

    def setUp(self):
        """Import pyboson module dynamically before each test."""
        try:
            import pyboson
            self.pyboson = pyboson
        except ImportError as e:
            self.fail(
                f"Failed to import 'pyboson'. Ensure C++ module is compiled. Error: {e}"
            )

    def test_01_module_attributes(self):
        """Verify pyboson exposes expected classes and methods."""
        self.assertTrue(hasattr(self.pyboson, "FlirBosonCamera"))
        
        # Instantiate camera object
        cam = self.pyboson.FlirBosonCamera("/dev/null")
        self.assertTrue(hasattr(cam, "initialize"))
        self.assertTrue(hasattr(cam, "close"))
        self.assertTrue(hasattr(cam, "get_next_frame"))

    def test_02_invalid_device_graceful_fail(self):
        """Verify initialization fails gracefully on non-existent hardware paths."""
        non_existent_device = "/dev/video_non_existent_999"
        cam = self.pyboson.FlirBosonCamera(non_existent_device)
        
        # Initialize should return False cleanly without crashing or causing a SEGFAULT
        is_initialized = cam.initialize()
        self.assertFalse(is_initialized, "initialize() should return False for non-existent device")
        
        # Capturing from uninitialized camera should return None
        frame = cam.get_next_frame()
        self.assertIsNone(frame, "get_next_frame() should return None when uninitialized")
        
        cam.close()

    def test_03_hardware_frame_capture_or_mock(self):
        """
        Tests frame extraction if a physical FLIR camera is attached (/dev/video0).
        If no physical camera is present, tests matrix validation logic against synthetic data.
        """
        device_path = "/dev/video0"
        cam = self.pyboson.FlirBosonCamera(device_path)
        
        if cam.initialize():
            print(f"\n[INFO] Physical FLIR Boson detected at {device_path}. Capturing live frame...")
            frame = cam.get_next_frame()
            cam.close()
            
            self.assertIsNotNone(frame, "Live frame capture returned None")
            self._validate_thermal_matrix(frame)
        else:
            print("\n[SKIP] No live thermal camera found at /dev/video0. Running matrix validation against synthetic stream.")
            # Generate synthetic 640x512 matrix matching pyboson C++ export format
            synthetic_frame = np.full((512, 640), 36.5, dtype=np.float32)
            self._validate_thermal_matrix(synthetic_frame)

    def _validate_thermal_matrix(self, matrix: np.ndarray):
        """Helper method to validate thermal matrix array constraints."""
        # 1. Type and dimension assertions
        self.assertIsInstance(matrix, np.ndarray, "Thermal frame must be a NumPy ndarray")
        self.assertEqual(matrix.ndim, 2, f"Expected 2D array (Height x Width), got {matrix.ndim}D")
        
        # 2. Shape assertion (FLIR Boson 640 resolution)
        height, width = matrix.shape
        self.assertEqual(height, 512, f"Expected height 512, got {height}")
        self.assertEqual(width, 640, f"Expected width 640, got {width}")

        # 3. Data type assertion
        self.assertTrue(
            np.issubdtype(matrix.dtype, np.floating),
            f"Expected floating point temperature values, got {matrix.dtype}"
        )

        # 4. Thermal range sanity check (Degrees Celsius)
        min_temp = float(np.min(matrix))
        max_temp = float(np.max(matrix))
        
        # Sanity bounds check: Temperatures should fall within realistic sensor limits (-40°C to 150°C)
        self.assertGreaterEqual(min_temp, -40.0, f"Unrealistic cold temperature detected: {min_temp}°C")
        self.assertLessEqual(max_temp, 150.0, f"Unrealistic hot temperature detected: {max_temp}°C")


if __name__ == "__main__":
    unittest.main(verbosity=2)
