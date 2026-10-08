import re
from typing import Dict, List

class MechanisticExtractor:
    """
    Parses un-smoothed document text to extract raw physical parameters,
    equations, sample sizes, and statistical metrics.
    """
    
    # Regex patterns for empirical metrics
    METRIC_PATTERNS = {
        "frequencies": r"\b\d+(\.\d+)?\s*(Hz|kHz|MHz)\b",
        "pressures_spl": r"\b\d+(\.\d+)?\s*(dB|SPL|Pa|kPa|psi)\b",
        "forces_accel": r"\b\d+(\.\d+)?\s*(g|m/s²|N)\b",
        "sample_sizes": r"\b(n\s*=\s*\d+|sample size of \d+)\b",
        "p_values": r"\b(p\s*<\s*0\.\d+|p\s*=\s*0\.\d+)\b"
    }

    @classmethod
    def extract_ground_truth_metrics(cls, text: str) -> Dict[str, List[str]]:
        extracted_data = {}
        for category, pattern in cls.METRIC_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            # Flatten regex tuple matches if present
            extracted_data[category] = [m[0] if isinstance(m, tuple) else m for m in matches]
            
        return extracted_data
