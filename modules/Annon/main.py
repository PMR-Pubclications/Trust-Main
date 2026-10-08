# main.py
import sys
import time
from scripts.integration.agency_bridge import AgencyBridge
from scripts.models.suggestion_engine import SuggestionEngine
from scripts.learning.feedback_learner import FeedbackLearner

def main():
    print("=== Trust Forensics Mobile Lab AI Assistant Active ===")
    
    bridge = AgencyBridge()
    suggester = SuggestionEngine()
    learner = FeedbackLearner()

    # Simulation loop for live incident voice processing[span_11](start_span)[span_11](end_span)
    try:
        while True:
            # 1. Listen to verbal input (Simulated text for pipeline verification)[span_12](start_span)[span_12](end_span)
            user_input = input("\n[Verbal Audio Input]: ")
            if user_input.lower() in ["exit", "quit"]:
                break
                
            active_agency = input("Select Agency Context (POLICE / FIRE / EMS / DOT / HOSPITAL): ").upper()
            
            # 2. Pull Request Check (specifically useful for hospitals)
            if "pull" in user_input.lower() or "records" in user_input.lower():
                print(f"\n[AI Assistant]: Querying {active_agency} databases for matching records...")
                data = bridge.pull_data(active_agency, {"query": user_input})
                print(f"[Data Retrieved]: {data}")

            # 3. Generate Real-time Suggestions[span_13](start_span)[span_13](end_span)
            suggestions = suggester.evaluate_scene_context(user_input, active_agency)
            if suggestions:
                print("\n[AI Verbal Response & Suggestions]:")
                for s in suggestions:
                    print(f" -> {s}")

            # 4. Action Request (Pushing Reports)[span_14](start_span)[span_14](end_span)
            if "push report" in user_input.lower():
                report_data = {
                    "incident_summary": user_input,
                    "suggestions_offered": suggestions,
                    "timestamp": time.time()
                }
                success = bridge.push_report(active_agency, report_data)
                print(f"[Push Dispatcher]: Report pushed to {active_agency}. Status: {success}[span_15](start_span)[span_15](end_span)")

            # 5. Interactive Feedback & Learning[span_16](start_span)[span_16](end_span)
            feedback = input("\nWas this response accurate? (y/n/correction): ")
            if feedback.lower() != 'y':
                learner.record_responder_feedback(
                    query=user_input, 
                    ai_response=str(suggestions), 
                    user_correction=feedback, 
                    agency=active_agency
                )
                print("[Continuous Learning]: Correction logged to data/Annotations/ for retraining[span_17](start_span)[span_17](end_span).")

    except KeyboardInterrupt:
        print("\nShutting down AI Assistant Core.")

if __name__ == "__main__":
    main()

import sys
from scripts.hardware_layer.bus_interceptor import DirectBusReader
from scripts.hardware_layer.tee_signer import HardwareAttestor
from scripts.zero_smoothing.wave_preserver import TransientPreserver
from scripts.deterministic_eval.physics_verifier import DeterministicGatekeeper
from scripts.chain_of_custody.merkle_builder import ForensicLedger

def execute_ground_truth_pipeline():
    # 1. Direct Hardware Capture
    raw_buffer = DirectBusReader.read_i2c_registers(bus=1, address=0x68, bytes=64)
    
    # 2. Hardware Cryptographic Signing
    signed_event = HardwareAttestor.sign_payload(raw_buffer)
    
    # 3. Preserve Raw Physical Outliers (No Smoothing)
    TransientPreserver.evaluate_and_store_outlier(signed_event)
    
    # 4. Deterministic Physics Validation (Must pass hard limits)
    is_valid_physics = DeterministicGatekeeper.verify_constraints(signed_event)
    
    if not is_valid_physics:
        sys.stderr.write("[FAULT] Hardware telemetry violates physical constraints or model bounds.\n")
        
    # 5. Commit to Immutable Chain-of-Custody
    ForensicLedger.append_event(signed_event)

if __name__ == "__main__":
    execute_ground_truth_pipeline()

