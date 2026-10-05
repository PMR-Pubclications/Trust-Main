import sys
import os
import time
import json

# Include compiled dynamic library path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../build")))

import pyboson
from thermal_analyzer import ThermalBleedingDetector
from ems_voice_parser import EMSVoiceParser

class FirstResponderEMSLoop:
    def __init__(self, dev_path="/dev/video0"):
        self.camera = pyboson.FlirBosonCamera(dev_path)
        self.detector = ThermalBleedingDetector(asymmetry_threshold_c=1.2)
        self.parser = EMSVoiceParser()
        
    def start_monitoring(self):
        if not self.camera.initialize():
            print("[ERROR] Could not connect to FLIR Boson thermal hardware.")
            return

        print("[TRUST_EMS] FLIR Boson radiometry active. Live thermal pipeline running...")
        
        try:
            while True:
                # 1. Grab 2D numpy array directly from C++ V4L2 stream
                thermal_matrix = self.camera.get_next_frame()
                if thermal_matrix is None:
                    time.sleep(0.01)
                    continue

                # 2. Execute thermal asymmetry / internal hemorrhage check
                current_time = time.time()
                alerts = self.detector.analyze_frame(thermal_matrix, current_time)

                for alert in alerts:
                    print(f"[CRITICAL_ALERT] {alert.anomaly_type} at {alert.zone_name} | "
                          f"ΔT: {alert.delta_temp_celsius}°C | Confidence: {alert.confidence*100:.1f}%")

                time.sleep(0.033) # ~30 FPS loop

        except KeyboardInterrupt:
            print("\n[TRUST_EMS] Shutting down sensor loop...")
        finally:
            self.camera.close()

if __name__ == "__main__":
    app = FirstResponderEMSLoop(dev_path="/dev/video0")
    app.start_monitoring()
