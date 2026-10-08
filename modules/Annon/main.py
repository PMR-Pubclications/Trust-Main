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

import json
import sys
import os
from scripts.research_engine.pipeline_orchestrator import GroundTruthResearchEngine
from scripts.research_engine.query_decomposer import QueryDecomposer
from scripts.research_engine.multi_tier_crawler import MultiTierCrawler

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<Research Question or Policy Claim>\"")
        sys.exit(1)

    user_query = sys.argv[1]
    
    # 1. Load physical constraints config
    config_path = "config/physical_constraints.json"
    if not os.path.exists(config_path):
        print(f"[ERROR] Missing physical constraints file at {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        physical_constraints = json.load(f)

    print(f"\n==================================================")
    print(f"[ANNON RESEARCH ENGINE INITIATED]")
    print(f"Target Query: \"{user_query}\"")
    print(f"==================================================\n")

    # 2. Decompose query into mechanistic parameters
    decomposed = QueryDecomposer.decompose(user_query)
    print(f"[1/4] Decomposed Queries Generated:")
    for q in decomposed["tier_0_1_queries"]:
        print(f"  - {q}")

    # 3. Fetch web/API search payloads
    print(f"\n[2/4] Executing Multi-Tier Data Crawler...")
    raw_hits = MultiTierCrawler.fetch_raw_hits(decomposed)
    print(f"  - Retained {len(raw_hits)} search payloads for verification.")

    # 4. Instantiate and execute the pipeline orchestrator
    print(f"\n[3/4] Running Epistemic Pipeline & Cross-Validation...")
    engine = GroundTruthResearchEngine(physical_constraints=physical_constraints)
    results = engine.execute_research(user_query, raw_hits)

    # 5. Output Results
    print(f"\n[4/4] RESEARCH EXECUTION COMPLETE")
    print(f"--------------------------------------------------")
    
    consensus = results.get("consensus_validation_report", {})
    verified = consensus.get("verified_truth_findings", [])
    unverified = consensus.get("unverified_hypotheses", [])

    print(f"\nVERIFIED TRUTH FINDINGS ({len(verified)} Clusters Passed 5-Source Rule):")
    for v in verified:
        print(f"  [STATUS]: {v.get('verification_status')}")
        print(f"  [SOURCES]: {v.get('sources_list')}")

    print(f"\nUNVERIFIED / DROPPED HYPOTHESES ({len(unverified)} Clusters Failed):")
    for u in unverified:
        print(f"  [STATUS]: {u.get('verification_status')}")

    audit = results.get("contradiction_audit", {})
    if audit.get("contradiction_detected"):
        print(f"\n[CONTRADICTION AUDIT FAULT DETECTED]:")
        for violation in audit.get("physical_violations", []):
            print(f"  ! {violation}")
    else:
        print(f"\n[CONTRADICTION AUDIT]: No physical boundary violations detected in top policy claims.")

if __name__ == "__main__":
    main()
