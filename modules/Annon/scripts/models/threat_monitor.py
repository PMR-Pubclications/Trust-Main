# scripts/models/threat_monitor.py
import logging

class ThreatMonitor:
    def __init__(self):
        # Initializing safety baselines based on config
        self.threat_keywords = ["gun", "help", "shots fired", "drop the weapon", "officer down", "cover"]
        self.camera_active = True

    def scan_ambient_audio(self, ambient_transcript: str, decibel_level: int) -> dict:
        """Continuously scans background audio for distress words or dangerous acoustic spikes."""
        transcript_lower = ambient_transcript.lower()
        
        # Immediate acoustic override (e.g., gunfire or explosion)
        if decibel_level >= 110:
            return {
                "threat_detected": True, 
                "level": "CRITICAL",
                "trigger": "ACOUSTIC_SPIKE", 
                "action": "AUTO_DISPATCH_BACKUP"
            }

        # Verbal threat keyword scanning
        for word in self.threat_keywords:
            if word in transcript_lower:
                return {
                    "threat_detected": True, 
                    "level": "HIGH",
                    "trigger": f"VERBAL_THREAT_{word.upper()}", 
                    "action": "ACTIVATE_CAMERA_AND_ALERT"
                }
                
        return {"threat_detected": False}

    def analyze_camera_feed(self, visual_data_frame: list) -> dict:
        """Evaluates live visual frames for drawn weapons, hostile approach, or downed agent."""
        if not self.camera_active:
            return {"threat_detected": False}
            
        # Simulated computer vision pipeline (e.g., checking bounding boxes for weapons/assault)
        if "firearm" in visual_data_frame or "knife" in visual_data_frame:
            return {
                "threat_detected": True, 
                "level": "CRITICAL",
                "trigger": "VISUAL_WEAPON_DETECTED", 
                "action": "AUTO_DISPATCH_BACKUP"
            }
            
        return {"threat_detected": False}
