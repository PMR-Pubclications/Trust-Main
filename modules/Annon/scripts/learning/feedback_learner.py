# scripts/learning/feedback_learner.py
import json
from datetime import datetime

class FeedbackLearner:
    def __init__(self, annotations_path="data/Annotations/"):
        self.annotations_path = annotations_path

    def record_responder_feedback(self, query: str, ai_response: str, user_correction: str, agency: str):
        """Logs user corrections to refine model context and build dataset fine-tuning files."""
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "agency": agency,
            "input_query": query,
            "model_generated": ai_response,
            "corrected_output": user_correction
        }
        
        file_path = f"{self.annotations_path}feedback_log.jsonl"
        try:
            with open(file_path, "a") as f:
                f.write(json.dumps(feedback_entry) + "\n")
            return True
        except Exception as e:
            print(f"Error saving learning data: {e}")
            return False
