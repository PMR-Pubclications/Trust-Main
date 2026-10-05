#!/usr/bin/env python3
import socket
import json
import struct
import time
import numpy as np
from thermal_analyzer import ThermalBleedingDetector
from ems_voice_parser import EMSVoiceParser

SOCKET_PATH = "/tmp/trust_first_responder.sock"

class EMSService:
    def __init__(self):
        self.detector = ThermalBleedingDetector(asymmetry_threshold_c=1.2)
        self.parser = EMSVoiceParser()

    def fetch_telemetry_frame(self) -> dict:
        """Fetch frame buffer from independent firstResponder service over IPC."""
        if not os.path.exists(SOCKET_PATH):
            return {"status": "OFFLINE", "reason": "firstResponder daemon not running"}

        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(SOCKET_PATH)
            
            # Read 4-byte payload length prefix
            raw_len = client.recv(4)
            if not raw_len:
                return {"status": "ERROR", "reason": "Empty payload received"}
            payload_len = struct.unpack('!I', raw_len)[0]

            # Read full JSON frame
            data = bytearray()
            while len(data) < payload_len:
                packet = client.recv(4096)
                if not packet:
                    break
                data.extend(packet)

            client.close()
            return json.loads(data.decode('utf-8'))
        except Exception as ex:
            return {"status": "ERROR", "reason": str(ex)}

    def process_cycle(self, voice_transcript: str = "") -> dict:
        telemetry = self.fetch_telemetry_frame()
        current_time = time.time()

        if "frame_flat" in telemetry:
            # Reconstruct 2D thermal matrix independently
            matrix = np.array(telemetry["frame_flat"], dtype=np.float32)
            alerts = self.detector.analyze_frame(matrix, current_time)
        else:
            alerts = []

        treatments = self.parser.parse_transcript(voice_transcript) if voice_transcript else []

        return {
            "module": "EMS",
            "timestamp": current_time,
            "status": "ONLINE" if "frame_flat" in telemetry else telemetry.get("status"),
            "critical_bleeding_detected": any(a.confidence > 0.75 for a in alerts),
            "alerts": [
                {"zone": a.zone_name, "type": a.anomaly_type, "delta_c": a.delta_temp_celsius}
                for a in alerts
            ],
            "treatments": [
                {"item": t.entity, "dose": f"{t.dosage} {t.unit}", "route": t.route}
                for t in treatments
            ]
        }

if __name__ == "__main__":
    ems = EMSService()
    print(json.dumps(ems.process_cycle("Pushed 1 mg epinephrine IV."), indent=2))
