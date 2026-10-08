import re
from typing import Dict, List

class QueryDecomposer:
    """
    Translates high-level policy questions into bottom-up physical,
    mechanistic, and forensic legal search queries.
    """

    MECHANISTIC_MAP = {
        "ms": '("demyelination" OR "multiple sclerosis" OR "axonal") AND ("vibration" OR "ectopic firing" OR "ephaptic")',
        "fly": '("cabin altitude" OR "hypoxia" OR "barometric pressure" OR "14 CFR 382")',
        "heart": '("arrhythmia" OR "cardiac arrest" OR "myocardial") AND ("altitude" OR "hypoxemia")',
        "breathing": '("portable oxygen concentrator" OR "POC" OR "150% battery rule" OR "continuous positive airway pressure")'
    }

    @classmethod
    def decompose(cls, user_query: str) -> Dict[str, List[str]]:
        tokens = re.findall(r"\w+", user_query.lower())
        mechanistic_terms = []

        for token in tokens:
            if token in cls.MECHANISTIC_MAP:
                mechanistic_terms.append(cls.MECHANISTIC_MAP[token])

        if not mechanistic_terms:
            # Fallback string if no mapped keywords match
            mechanistic_terms.append(f'("{user_query}") AND ("data" OR "metrics" OR "trial" OR "statute")')

        return {
            "raw_user_query": user_query,
            "tier_0_1_queries": [
                " AND ".join(mechanistic_terms) + " site:ncbi.nlm.nih.gov",
                " AND ".join(mechanistic_terms) + " site:courtlistener.com",
                " AND ".join(mechanistic_terms) + " site:clinicaltrials.gov"
            ],
            "tier_2_3_queries": [
                f'"{user_query}" policy regulation FAA DOT'
            ]
        }
