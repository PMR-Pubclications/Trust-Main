#!/usr/bin/env python3
import socket
import json
import struct
import os
import time
import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, Any, List

SOCKET_PATH = "/tmp/trust_first_responder.sock"

@dataclass
class HazmatReadings:
    co_ppm: float       # Carbon Monoxide (ppm)
    hcn_ppm: float      # Hydrogen Cyanide (ppm)
    lel_percent: float  # Lower Explosive Limit (%)
    o2_percent: float   # Oxygen (%)

class FireService:
    def __init__(self, temp_critical_c: float = 500.0):
        self.temp_critical_c = temp_critical_c

    def _fetch_first_responder_telemetry(self) -> dict:
        """Reads stream payload from independent firstResponder daemon over IPC."""
        if not os.path.exists(SOCKET_PATH):
            return {"status": "OFFLINE", "reason": "firstResponder daemon not running"}

        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(SOCKET_PATH)
            
            raw_len = client.recv(4)
            if not raw_len:
                return {"status": "ERROR", "reason": "Empty socket response"}
            payload_len = struct.unpack('!I', raw_len)[0]

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

    def evaluate_thermal_hazards(self, thermal_matrix: np.ndarray) -> dict:
        """Analyzes upper-layer boundary thermal saturation and localized hotspots."""
        max_temp = float(np.max(thermal_matrix))
        mean_temp = float(np.mean(thermal_matrix))
        
        # Calculate localized flashover risk index
        flashover_risk = min(1.0, max_temp / self.temp_critical_c)
        
        # Detect hotspots exceeding structural structural tolerance (> 300°C)
        hotspot_pixels = np.sum(thermal_matrix > 300.0)
        
        return {
            "max_surface_temp_c": round(max_temp, 2),
            "mean_ambient_temp_c": round(mean_temp, 2),
            "flashover_risk_index": round(flashover_risk, 3),
            "critical_hotspot_detected": max_temp >= 300.0,
            "hotspot_area_pixels": int(hotspot_pixels)
        }

    def process_hazmat_sensors(self, raw_gas_payload: Dict[str, float]) -> dict:
        """Evaluates atmospheric toxic gas telemetry against OSHA/NIOSH emergency limits."""
        readings = HazmatReadings(
            co_ppm=raw_gas_payload.get("co", 0.0),
            hcn_ppm=raw_gas_payload.get("hcn", 0.0),
            lel_percent=raw_gas_payload.get("lel", 0.0),
            o2_percent=raw_gas_payload.get("o2", 20.9)
        )

        alerts = []
        if readings.co_ppm > 35.0:
            alerts.append(f"CO WARNING: {readings.co_ppm} ppm (Pel Limit Exceeded)")
        if readings.hcn_ppm > 10.0:
            alerts.append(f"HCN TOXIC ALERT: {readings.hcn_ppm} ppm")
        if readings.lel_percent > 10.0:
            alerts.append(f"EXPLOSIVE ATMOSPHERE: LEL at {readings.lel_percent}%")
        if readings.o2_percent < 19.5:
            alerts.append(f"OXYGEN DEFICIENCY: O2 at {readings.o2_percent}%")

        return {
            "readings": asdict(readings),
            "hazmat_alerts": alerts,
            "environment_idlh": readings.co_ppm > 1200.0 or readings.hcn_ppm > 50.0 or readings.lel_percent > 25.0
        }

    def process_cycle(self, gas_telemetry: Dict[str, float] = None) -> dict:
        telemetry = self._fetch_first_responder_telemetry()
        current_time = time.time()

        if "frame_flat" in telemetry:
            matrix = np.array(telemetry["frame_flat"], dtype=np.float32)
            thermal_status = self.evaluate_thermal_hazards(matrix)
        else:
            thermal_status = {"status": "NO_THERMAL_FEED"}

        gas_status = self.process_hazmat_sensors(gas_telemetry or {})

        return {
            "module": "FIRE",
            "timestamp": current_time,
            "status": "ONLINE" if "frame_flat" in telemetry else telemetry.get("status"),
            "thermal_analysis": thermal_status,
            "hazmat_analysis": gas_status
        }

if __name__ == "__main__":
    fire_node = FireService()
    # Test execution with sample gas sensor stream
    sample_gas = {"co": 45.0, "hcn": 12.0, "lel": 5.0, "o2": 20.1}
    print(json.dumps(fire_node.process_cycle(sample_gas), indent=2))
