# scripts/models/suggestion_engine.py
from typing import Dict, List

class SuggestionEngine:
    def __init__(self):
        # Load tactical protocols, SOPs, and hazardous chemical rules[span_4](start_span)[span_4](end_span)
        pass

    def evaluate_scene_context(self, transcript: str, agency: str) -> List[str]:
        """Generates immediate action suggestions based on speech transcript and target agency[span_5](start_span)[span_5](end_span)."""
        suggestions = []
        transcript_lower = transcript.lower()

        if agency.upper() == "FIRE" or agency.upper() == "EMS":
            if "chemical" in transcript_lower or "fumes" in transcript_lower:
                suggestions.append("SOP ALERT: Establish 300ft perimeter. Request Hazmat Unit[span_6](start_span)[span_6](end_span).")
                suggestions.append("EMS ACTION: Prepare administration of oxygen and secondary decontamination protocol[span_7](start_span)[span_7](end_span).")

        elif agency.upper() == "DOT":
            if "blocking lane" in transcript_lower or "structural damage" in transcript_lower:
                suggestions.append("DOT ACTION: Issue digital dynamic message sign (DMS) detour 2 miles prior[span_8](start_span)[span_8](end_span).")
                suggestions.append("TRAFFIC CONTROL: Deploy secondary crash suppression truck[span_9](start_span)[span_9](end_span).")

        elif agency.upper() == "POLICE":
            if "eviction" in transcript_lower or "weapon visible" in transcript_lower:
                suggestions.append("POLICE PROTOCOL: Request back-up unit. Establish command post perimeter[span_10](start_span)[span_10](end_span).")
                
        elif agency.upper() == "HOSPITAL":
            if "incoming" in transcript_lower or "trauma" in transcript_lower:
                suggestions.append("HOSPITAL PROTOCOL: Alerting Level 1 Trauma bay and paging on-call surgical team.")
            if "blood" in transcript_lower or "transfusion" in transcript_lower:
                suggestions.append("ACTION: Querying universal O-negative blood supply availability from blood bank.")

        return suggestions
