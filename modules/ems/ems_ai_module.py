import sys
import os
import time
import json
import numpy as np

# Dynamically resolve import path to sibling module: modules/firstResponder
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIRST_RESPONDER_PY_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../firstResponder/python"))
FIRST_RESPONDER_BUILD_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../firstResponder/build"))

for path in (FIRST_RESPONDER_PY_DIR, FIRST_RESPONDER_BUILD_DIR):
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

# Import local EMS engines
from thermal_analyzer import ThermalBleedingDetector
from ems_voice_parser import EMSVoiceParser

class EMSAIResponder:
    def __init__(self, device_path: str = "/dev/video0"):
        self.device_path = device_path
        self.detector = ThermalBleedingDetector(asymmetry_threshold_c=1.2)
        self.parser = EMSVoiceParser()
        self.camera = None

        # Attempt pyboson C++ native driver import from modules/firstResponder
        try:
            import pyboson
            self.camera = pyboson.FlirBosonCamera(self.device_path)
            print("[EMS_MODULE] Successfully linked C++ pyboson driver from modules/firstResponder.")
        except ImportError:
            print("[EMS_MODULE_WARN] pyboson C++ driver not found. Running in telemetry-only / synthetic mode.")

    def run_live_cycle(self, voice_input: str = "") -> dict:
        """Executes a single processing cycle on incoming thermal frame and voice stream."""
        current_time = time.time()
        thermal_matrix = None

        if self.camera and self.camera.initialize():
            thermal_matrix = self.camera.get_next_frame()

        if thermal_matrix is None:
            # Fallback synthetic matrix (36.5°C baseline) if hardware is unavailable
            thermal_matrix = np.full((512, 640), 36.5, dtype=np.float32)

        # Analyze thermal anomalies and voice actions
        thermal_alerts = self.detector.analyze_frame(thermal_matrix, current_time)
        voice_records = self.parser.parse_transcript(voice_input) if voice_input else []

        payload = {
            "module": "EMS",
            "timestamp": current_time,
            "status": "ACTIVE",
            "thermal_alerts": [
                {
                    "zone": a.zone_name,
                    "type": a.anomaly_type,
                    "delta_c": a.delta_temp_celsius,
                    "confidence": round(a.confidence, 2)
                } for a in thermal_alerts
            ],
            "treatments_recorded": [
                {
                    "item": r.entity,
                    "dose": f"{r.dosage} {r.unit}",
                    "route": r.route,
                    "raw": r.raw_transcript
                } for r in voice_records
            ]
        }
        return payload

if __name__ == "__main__":
    ems_node = EMSAIResponder()
    sample_telemetry = ems_node.run_live_cycle("Administered 100 mcg fentanyl IV push.")
    print(json.dumps(sample_telemetry, indent=2))
