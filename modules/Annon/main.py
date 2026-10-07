# main.py
import time
from scripts.integration.agency_bridge import AgencyBridge
from scripts.models.suggestion_engine import SuggestionEngine
from scripts.learning.feedback_learner import FeedbackLearner

def main():
    print("=== Trust Forensics Mobile Lab: Anon AI Active ===")
    
    bridge = AgencyBridge()
    suggester = SuggestionEngine()
    learner = FeedbackLearner()

    try:
        while True:
            # 1. Verbal Audio Input (Simulated text for pipeline execution)
            user_input = input("\n[Anon Listening... Speak your command]: ")
            if user_input.lower() in ["exit", "quit"]:
                break
                
            active_agency = input("Select Context Agency (POLICE / FIRE / EMS / HOSPITAL / DOT): ").upper()

            # 2. Pulling Data from Hospitals or Agencies
            if "pull" in user_input.lower() or "patient" in user_input.lower() or "victim" in user_input.lower():
                print(f"[Anon]: Pulling records from {active_agency}...")
                data = bridge.pull_data(active_agency, {"query": user_input})
                print(f"[Data Retrieved]: {data}")

            # 3. Generate Real-time Suggestions
            suggestions = suggester.evaluate_scene_context(user_input, active_agency)
            if suggestions:
                print("\n[Anon Suggestions]:")
                for s in suggestions:
                    print(f" -> {s}")

            # 4. Action Request (Pushing Reports)
            if "push report" in user_input.lower() or "send report" in user_input.lower():
                report_data = {
                    "incident_summary": user_input,
                    "timestamp": time.time()
                }
                success = bridge.push_report(active_agency, report_data)
                print(f"[Anon]: Report pushed to {active_agency}. Status: {success}")

            # 5. Continuous Learning / Feedback Loop
            feedback = input("\n[System]: Was Anon's response accurate? (Type 'y' or provide verbal correction): ")
            if feedback.lower() != 'y':
                learner.record_responder_feedback(
                    query=user_input, 
                    ai_response=str(suggestions), 
                    user_correction=feedback, 
                    agency=active_agency
                )
                print("[Anon]: Correction logged. I will apply this to future model fine-tuning.")

    except KeyboardInterrupt:
        print("\nShutting down Anon AI.")

if __name__ == "__main__":
    main()

# main.py
import time
from scripts.integration.agency_bridge import AgencyBridge
from scripts.models.suggestion_engine import SuggestionEngine
from scripts.models.threat_monitor import ThreatMonitor

def main():
    print("=== Trust Forensics Mobile Lab: Anon AI Active ===")
    
    bridge = AgencyBridge()
    suggester = SuggestionEngine()
    monitor = ThreatMonitor()

    try:
        while True:
            # 1. Background Threat Monitoring (Audio & Video)
            # Simulated ambient data streams
            ambient_audio = input("\n[Ambient Audio Stream]: ")
            ambient_decibels = 60  # Simulated normal talking volume
            camera_frame = []      # Simulated clean camera frame
            
            # 1a. Check Audio for Threats First
            audio_threat = monitor.scan_ambient_audio(ambient_audio, ambient_decibels)
            if audio_threat["threat_detected"]:
                print(f"\n[ANON SAFETY OVERRIDE]: {audio_threat['trigger']} detected!")
                if audio_threat["action"] == "ACTIVATE_CAMERA_AND_ALERT":
                    print("[Anon]: Activating 360-degree camera feed for visual confirmation.")
                    # Simulate pulling a frame where a weapon is visible
                    camera_frame = ["firearm"] 

            # 1b. Check Visuals for Threats
            visual_threat = monitor.analyze_camera_feed(camera_frame)
            if visual_threat["threat_detected"] or audio_threat.get("level") == "CRITICAL":
                print(f"\n[ANON CRITICAL ALERT]: Officer safety compromised. Initiating Auto-Dispatch.")
                alert_payload = {
                    "agent_id": "LAB_01",
                    "trigger": visual_threat.get("trigger", audio_threat.get("trigger")),
                    "timestamp": time.time(),
                    "gps_location": "CURRENT_GPS_COORDS"
                }
                bridge.broadcast_emergency_distress(alert_payload)
                continue # Skip standard processing until scene is clear

            # 2. Standard Verbal Commands (If no threat detected)
            if ambient_audio.lower().startswith("anon"):
                active_agency = "POLICE" # Assuming active context
                print(f"[Anon Processing Command]: {ambient_audio}")
                
                # Standard operations run here (Suggestions, Pulling Data, Pushing Reports)
                suggestions = suggester.evaluate_scene_context(ambient_audio, active_agency)
                if suggestions:
                    for s in suggestions:
                        print(f" -> {s}")

    except KeyboardInterrupt:
        print("\nShutting down Anon AI.")

if __name__ == "__main__":
    main()
