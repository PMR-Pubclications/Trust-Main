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
