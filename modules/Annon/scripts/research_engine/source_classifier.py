import re
from urllib.parse import urlparse

class SourceClassifier:
    """
    Classifies incoming document sources into Epistemic Tiers (0-3)
    based on origin, cryptographic signatures, and structural signatures.
    """
    
    TIER_0_DOMAINS = ["clinicaltrials.gov", "ncbi.nlm.nih.gov", "courtlistener.com", "uspto.gov", "arxiv.org"]
    TIER_1_DOMAINS = ["sciencedirect.com", "ieeexplore.ieee.org", "springer.com", "nature.com", "pnas.org"]
    
    @classmethod
    def classify(cls, source_metadata: dict) -> int:
        url = source_metadata.get("url", "")
        domain = urlparse(url).netloc.lower()
        has_tee_signature = source_metadata.get("has_tee_signature", False)
        
        # Tier 0: Direct hardware logs, TEE-attested data, raw legal/trial records
        if has_tee_signature or any(d in domain for d in cls.TIER_0_DOMAINS):
            return 0
            
        # Tier 1: Peer-reviewed mechanics, engineering journals, patents
        if any(d in domain for d in cls.TIER_1_DOMAINS) or source_metadata.get("is_peer_reviewed"):
            return 1
            
        # Tier 2: Meta-analyses, clinical guidelines, formal statutes (e.g., 14 CFR)
        if domain.endswith(".gov") or domain.endswith(".edu") or "guidelines" in url:
            return 2
            
        # Tier 3: General web, corporate PR, landing pages, marketing
        return 3
