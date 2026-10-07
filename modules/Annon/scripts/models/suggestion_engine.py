# scripts/models/suggestion_engine.py

class SuggestionEngine:
    def __init__(self):
        pass

    def evaluate_scene_context(self, transcript: str, agency: str) -> list:
        """Generates immediate action suggestions based on speech transcript."""
        suggestions = []
        transcript_lower = transcript.lower()

        if agency.upper() in ["FIRE", "EMS"]:
            if "chemical" in transcript_lower or "fumes" in transcript_lower:
                suggestions.append("SOP ALERT: Establish 300ft perimeter. Request Hazmat Unit.")
            if "unconscious" in transcript_lower or "victim" in transcript_lower:
                suggestions.append("ACTION: Pulling nearest hospital availability and patient medical history.")

        elif agency.upper() == "POLICE":
            if "weapon visible" in transcript_lower or "hostile" in transcript_lower:
                suggestions.append("PROTOCOL: Request back-up. Establish command post perimeter.")

        return suggestions
