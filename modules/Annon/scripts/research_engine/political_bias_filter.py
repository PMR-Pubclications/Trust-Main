import re
from typing import Dict, Union

class PoliticalBiasFilter:
    """
    Evaluates source bias on a normalized spectrum from -1.0 (Far Left) 
    to +1.0 (Far Right), where 0.0 represents Moderate/Centrist.
    
    Applies a triangular decay function that devalues political extremes to 0.0 
    and maximizes Moderate/Neutral sources at 1.0.
    """
    
    # Static lookup database for known domain political leanings
    # -1.0 = Far Left | 0.0 = Moderate / Neutral | +1.0 = Far Right
    BIAS_DATABASE = {
        # Moderate / Neutral / Technical Sources
        "reuters.com": 0.0,
        "apnews.com": 0.0,
        "c-span.org": 0.0,
        "nature.com": 0.0,
        "ncbi.nlm.nih.gov": 0.0,
        "courtlistener.com": 0.0,
        "uspto.gov": 0.0,
        "arxiv.org": 0.0,
        
        # Leaning Left / Far Left
        "msnbc.com": -0.85,
        "edition.cnn.com": -0.60,
        "huffpost.com": -0.90,
        "theguardian.com": -0.55,
        "jacobin.com": -1.0,
        
        # Leaning Right / Far Right
        "foxnews.com": 0.75,
        "breitbart.com": 0.95,
        "thegatewaypundit.com": 1.0,
        "nypost.com": 0.50,
        "dailywire.com": 0.80
    }

    # Keyword indicators for dynamic text bias fallback
    LEFT_KEYWORDS = [r"\b(far-left|socialist|progressive_agenda|marxist)\b"]
    RIGHT_KEYWORDS = [r"\b(far-right|alt-right|reactionary|ultra-conservative)\b"]

    @classmethod
    def get_bias_score(cls, domain: str, text: str = "") -> float:
        """
        Returns the raw political bias position between -1.0 and +1.0.
        Defaults to 0.0 (Moderate) for unknown academic or raw data sources.
        """
        for known_domain, bias in cls.BIAS_DATABASE.items():
            if known_domain in domain.lower():
                return bias
                
        # Heuristic fallback based on text indicators if domain is unknown
        left_hits = sum(len(re.findall(p, text, re.IGNORECASE)) for p in cls.LEFT_KEYWORDS)
        right_hits = sum(len(re.findall(p, text, re.IGNORECASE)) for p in cls.RIGHT_KEYWORDS)
        
        if left_hits > right_hits:
            return -0.8
        elif right_hits > left_hits:
            return 0.8
            
        return 0.0  # Default to Moderate/Neutral if no partisan markers detected

    @classmethod
    def calculate_bias_multiplier(cls, bias_value: float) -> float:
        """
        Triangular Devaluation Curve:
        - Bias = 0.0 (Moderate)  => Multiplier = 1.0 (Maximum Value)
        - Bias = -1.0 (Far Left) => Multiplier = 0.0 (Completely Devalued)
        - Bias = +1.0 (Far Right)=> Multiplier = 0.0 (Completely Devalued)
        """
        # Linear decay from center: 1.0 - |bias|
        multiplier = 1.0 - abs(bias_value)
        return max(0.0, min(1.0, multiplier))

    @classmethod
    def apply_bias_devaluation(cls, document: Dict) -> Dict:
        """
        Modifies the document's epistemic score and re-evaluates Tier position 
        based on political neutrality.
        """
        url = document.get("metadata", {}).get("url", "")
        text = document.get("content", "")
        
        # 1. Determine political bias (-1.0 to 1.0)
        raw_bias = cls.get_bias_score(url, text)
        
        # 2. Compute devaluation multiplier (Moderate = 1.0, Extremes = 0.0)
        bias_multiplier = cls.calculate_bias_multiplier(raw_bias)
        
        # 3. Apply multiplier to current score
        original_score = document.get("epistemic_score", 1.0)
        adjusted_score = original_score * bias_multiplier
        
        document["political_bias_raw"] = raw_bias
        document["bias_multiplier"] = bias_multiplier
        document["epistemic_score"] = adjusted_score
        
        # 4. Demote Tier if political bias reduces score significantly
        if bias_multiplier == 0.0:
            document["tier"] = 3  # Force extreme bias into propaganda/lowest tier
            
        return document
