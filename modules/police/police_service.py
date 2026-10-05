#!/usr/bin/env python3
import socket
import json
import struct
import os
import time
import math
import hashlib
import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Tuple

SOCKET_PATH = "/tmp/trust_first_responder.sock"

@dataclass
class BallisticTrajectory:
    impact_id: str
    entry_point_xyz: Tuple[float, float, float]
    impact_angle_deg: float
    azimuth_deg: float
    calibrated_vector: Tuple[float, float, float]

class PoliceService:
    def __init__(self, db_path: str = "police_evidence.db"):
        self.db_path = db_path

    def _fetch_first_responder_telemetry(self) -> dict:
        """Reads camera/sensor feed from firstResponder over IPC."""
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

    def calculate_ballistic_impact(
        self, 
        minor_axis_mm: float, 
        major_axis_mm: float, 
        azimuth_deg: float, 
        surface_xyz: Tuple[float, float, float]
    ) -> BallisticTrajectory:
        """
        Calculates impact angle and 3D vector from ballistic impact ellipse dimensions.
        """
        if major_axis_mm <= 0 or minor_axis_mm <= 0 or minor_axis_mm > major_axis_mm:
            impact_angle = 90.0  # Perpendicular default
        else:
            impact_angle = math.degrees(math.asin(minor_axis_mm / major_axis_mm))

        # Convert spherical vector angles to normalized 3D Cartesian trajectory vector
        rad_angle = math.radians(impact_angle)
        rad_azimuth = math.radians(azimuth_deg)

        vx = math.cos(rad_angle) * math.sin(rad_azimuth)
        vy = math.cos(rad_angle) * math.cos(rad_azimuth)
        vz = math.sin(rad_angle)

        impact_id = f"IMP_{int(time.time())}_{int(minor_axis_mm*100)}"

        return BallisticTrajectory(
            impact_id=impact_id,
            entry_point_xyz=surface_xyz,
            impact_angle_deg=round(impact_angle, 2),
            azimuth_deg=round(azimuth_deg, 2),
            calibrated_vector=(round(vx, 4), round(vy, 4), round(vz, 4))
        )

    def log_chain_of_custody_evidence(self, item_description: str, officer_badge: str) -> dict:
        """Generates cryptographic proof hash for forensic scene evidence."""
        timestamp = time.time()
        payload = f"{item_description}:{officer_badge}:{timestamp}"
        evidence_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()

        return {
            "evidence_id": f"EVID_{int(timestamp)}",
            "description": item_description,
            "logging_officer": officer_badge,
            "timestamp": timestamp,
            "chain_hash": evidence_hash
        }

    def process_cycle(self, pending_impact: Dict[str, Any] = None) -> dict:
        telemetry = self._fetch_first_responder_telemetry()
        current_time = time.time()

        trajectories = []
        if pending_impact:
            traj = self.calculate_ballistic_impact(
                minor_axis_mm=pending_impact.get("minor_axis_mm", 9.0),
                major_axis_mm=pending_impact.get("major_axis_mm", 12.0),
                azimuth_deg=pending_impact.get("azimuth", 45.0),
                surface_xyz=pending_impact.get("xyz", (0.0, 1.5, 2.0))
            )
            trajectories.append(asdict(traj))

        return {
            "module": "POLICE",
            "timestamp": current_time,
            "status": "ONLINE" if "frame_flat" in telemetry else telemetry.get("status"),
            "ballistics_engine": "ACTIVE",
            "calculated_trajectories": trajectories
        }

if __name__ == "__main__":
    police_node = PoliceService()
    # Test execution with sample ballistic impact measurement
    sample_impact = {
        "minor_axis_mm": 9.1,
        "major_axis_mm": 14.2,
        "azimuth": 112.5,
        "xyz": (1.2, 0.8, 1.75)
    }
    print(json.dumps(police_node.process_cycle(sample_impact), indent=2))
