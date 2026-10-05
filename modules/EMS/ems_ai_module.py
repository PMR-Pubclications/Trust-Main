import time
import json
import numpy as np
from thermal_analyzer import ThermalBleedingDetector
from ems_voice_parser import EMSVoiceParser

class EMSAIModule:
    def __init__(self):
        self.thermal_detector = ThermalBleedingDetector(asymmetry_threshold_c=1.2)
        self.voice_parser = EMSVoiceParser()
        self.event_log = []

    def process_telemetry_frame(self, thermal_frame: np.ndarray, audio_transcript: str = "") -> Dict[str, Any]:
        current_time = time.time()
        
        # Process Thermal Input
        thermal_alerts = self.thermal_detector.analyze_frame(thermal_frame, current_time)
        
        # Process Audio Input
        action_records = []
        if audio_transcript.strip():
            action_records = self.voice_parser.parse_transcript(audio_transcript)

        # Assemble Unified Telemetry Payload
        payload = {
            "module": "EMS_AI_RESPONDER",
            "timestamp": current_time,
            "patient_status": {
                "thermal_anomalies_detected": len(thermal_alerts) > 0,
                "critical_bleeding_risk": any(a.confidence > 0.75 for a in thermal_alerts),
                "alerts": [
                    {
                        "zone": a.zone_name,
                        "type": a.anomaly_type,
                        "delta_c": a.delta_temp_celsius,
                        "confidence": a.confidence
                    } for a in thermal_alerts
                ]
            },
            "interventions": [
                {
                    "time": r.timestamp,
                    "type": r.category,
                    "item": r.entity,
                    "dose": f"{r.dosage} {r.unit}",
                    "route": r.route,
                    "raw": r.raw_transcript
                } for r in action_records
            ]
        }

        if thermal_alerts or action_records:
            self.event_log.append(payload)

        return payload

# Quick operational test
if __name__ == "__main__":
    ems_system = EMSAIModule()

    # Simulate 120x160 thermal matrix (Celsius) with a cold internal hemorrhage zone
    synthetic_thermal = np.full((120, 160), 36.5, dtype=float)
    # Simulate localized cooling from internal bleeding / disrupted microvascular flow
    synthetic_thermal[40:60, 50:70] = 34.2

    # Simulate transcript
    sample_speech = "Pushed 0.5 mg epinephrine IV push for severe trauma."

    telemetry = ems_system.process_telemetry_frame(synthetic_thermal, sample_speech)
    print(json.dumps(telemetry, indent=2))
