import re
from typing import Dict, List

class EpistemicRanker:
    """
    Ranks search results by physical truth and mechanistic density
    rather than domain authority or PageRank.
    """
    
    # High-density truth markers (Mechanisms, Metrics, Raw Data)
    TRUTH_MARKERS = [
        r"\b\d+\s*(Hz|dB|kPa|m/s²|mg/dL)\b",  # Physical units
        r"\b(ephaptic|demyelination|axonal|ion_channel|voltage-gated)\b", # Mechanics
        r"\b(p-value|confidence_interval|sample_size_n=)\b",              # Empirical stats
        r"\b(statute|deposition|subpoena|exhibit_\w+)\b"                  # Legal records
    ]
    
    # Propaganda & Surface-level markers (Policy fluff, PR, Marketing)
    PROPAGANDA_MARKERS = [
        r"\b(committed to accessibility|customer satisfaction|general policy)\b",
        r"\b(in most cases|generally speaking|statistically rare|safe for all)\b",
        r"\b(terms and conditions apply|fly with confidence)\b"
    ]

    @classmethod
    def calculate_epistemic_score(cls, document: Dict) -> float:
        text = document.get("content", "")
        tier = document.get("tier", 3) # Default to Tier 3 (Surface)
        
        # Base weight derived from Epistemic Tier
        tier_weights = {0: 1.0, 1: 0.8, 2: 0.3, 3: 0.05}
        base_score = tier_weights.get(tier, 0.05)
        
        # Calculate Mechanistic Density
        truth_hits = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in cls.TRUTH_MARKERS)
        propaganda_hits = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in cls.PROPAGANDA_MARKERS)
        
        # Density equation: Truth hits boost score; propaganda fluff penalizes it
        density_score = (truth_hits * 1.5) / (propaganda_hits + 1.0)
        
        final_epistemic_score = base_score * (1.0 + density_score)
        return final_epistemic_score

    @classmethod
    def rank_results(cls, search_results: List[Dict]) -> List[Dict]:
        """Sorts search hits so empirical truth rises to the top."""
        for doc in search_results:
            doc["epistemic_score"] = cls.calculate_epistemic_score(doc)
            
        return sorted(search_results, key=lambda x: x["epistemic_score"], reverse=True)
