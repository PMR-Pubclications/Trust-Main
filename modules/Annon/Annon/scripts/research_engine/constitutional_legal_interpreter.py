import json
import os
import re
from typing import Dict, List, Set, Tuple

class ConstitutionalLegalInterpreter:
    """
    Enforces Strict Textualism (Plain Meaning Rule) as the baseline legal logic engine.
    
    Architecture Rules:
      1. Plain Meaning Priority: Words are parsed strictly by their literal, statutory,
         or enactment-era definitions.
      2. Judicial Drift Penalty: Opinions/sources that attempt subjective re-interpretation 
         or policy-driven deviation from black-letter text are flagged and penalized.
      3. Dynamic Casework Ingestion: Ingests new court dockets, statutory updates, and 
         verified holdings, persisting them into 'Annon/data/legal_casework_state.json'.
      4. Case vs. Search Alignment: Compares live search results against active case 
         parameters to verify statutory applicability and empirical alignment.
    """

    STATE_FILE_PATH = os.path.join("Annon", "data", "legal_casework_state.json")
    DRIFT_THRESHOLD = 0.25  # Max allowable judicial/interpretive drift (25%)

    # Core Constitutional & Statutory Text Baselines (Extendable via state)
    DEFAULT_STATUTORY_DEFINITIONS = {
        "shall": "Mandatory requirement leaving no room for discretion.",
        "may": "Permissive authorization granting discretion.",
        "person": "Individual human being or legally recognized entity under explicit statute.",
        "arms": "Weapons and defensive equipment suited for individual self-defense or militia duty.",
        "search": "Government intrusion into a reasonable expectation of privacy or physical trespass.",
        "seizure": "Meaningful interference with an individual's possessory interest in property or liberty."
    }

    # Linguistic markers indicating non-textual / policy-driven judicial drift
    JUDICIAL_DRIFT_TRIGGERS = [
        r"\b(living constitution|evolving standards|spirit of the law|penumbra|balancing test)\b",
        r"\b(public policy interest|pragmatic approach|modern context|judicial discretion)\b",
        r"\b(legislative intent|intent of the framers|broad interpretation|flexible standard)\b"
    ]

    # Markers indicating strict textualist / originalist fidelity
    TEXTUALIST_ANCHORS = [
        r"\b(plain meaning|textual text|black-letter|express terms|statutory text)\b",
        r"\b(as written|original public meaning|strict construction|unambiguous|letter of the law)\b",
        r"\b(four corners|statutory definition|dictionary definition|enactment)\b"
    ]

    def __init__(self, state_path: str = None):
        self.state_file_path = state_path or self.STATE_FILE_PATH
        
        self.statutory_definitions: Dict[str, str] = {}
        self.case_precedents: Dict[str, Dict] = {}  # Citation -> Holding/Facts
        self.active_casework: Dict[str, Dict] = {}   # Case_ID -> Active Case Details
        
        self.load_state()

    def load_state(self) -> None:
        """Loads active statutory definitions, precedents, and casework state from disk."""
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.statutory_definitions = data.get("statutory_definitions", self.DEFAULT_STATUTORY_DEFINITIONS)
                    self.case_precedents = data.get("case_precedents", {})
                    self.active_casework = data.get("active_casework", {})
                    return
            except Exception as e:
                print(f"[LEGAL ENGINE WARNING] Failed to load legal state: {e}. Reverting to defaults.")

        self.statutory_definitions = dict(self.DEFAULT_STATUTORY_DEFINITIONS)
        self.case_precedents = {}
        self.active_casework = {}

    def save_state(self) -> None:
        """Persists legal state to local JSON storage."""
        os.makedirs(os.path.dirname(self.state_file_path), exist_ok=True)
        data = {
            "statutory_definitions": self.statutory_definitions,
            "case_precedents": self.case_precedents,
            "active_casework": self.active_casework
        }
        with open(self.state_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def ingest_casework(self, case_id: str, case_data: Dict) -> None:
        """
        Dynamically ingests a new active case or precedent docket into Annon's core state.
        
        case_data structure:
          {
            "title": str,
            "statutes_involved": List[str],
            "key_facts": List[str],
            "defined_terms": Dict[str, str], # Any explicit statutory definitions
            "holding": str
          }
        """
        self.active_casework[case_id] = case_data
        
        # Merge any newly defined statutory terms directly into the plain-meaning dictionary
        new_terms = case_data.get("defined_terms", {})
        for term, definition in new_terms.items():
            self.statutory_definitions[term.lower()] = definition

        self.save_state()
        print(f"[CASEWORK INGESTED] Case ID '{case_id}' active. Integrated {len(new_terms)} new term definitions.")

    def evaluate_legal_text(self, text: str) -> Dict:
        """
        Evaluates legal text or court opinions for adherence to strict textualism versus judicial drift.
        """
        words = re.findall(r"\b\w+\b", text.lower())
        total_words = len(words)

        if total_words == 0:
            return {"drift_score": 1.0, "is_rejected": True, "reason": "Empty document"}

        drift_hits = sum(len(re.findall(p, text, re.IGNORECASE)) for p in self.JUDICIAL_DRIFT_TRIGGERS)
        textualist_hits = sum(len(re.findall(p, text, re.IGNORECASE)) for p in self.TEXTUALIST_ANCHORS)

        # Compute drift probability
        # High drift hits increase score; textualist anchors offset drift
        raw_drift = (drift_hits * 3.0) / max(1, total_words * 0.01)
        anchor_offset = (textualist_hits * 1.5) / max(1, total_words * 0.01)
        
        drift_score = round(max(0.0, min(1.0, raw_drift - anchor_offset)), 4)
        is_rejected = drift_score > self.DRIFT_THRESHOLD

        return {
            "total_words": total_words,
            "judicial_drift_hits": drift_hits,
            "textualist_anchor_hits": textualist_hits,
            "drift_score": drift_score,
            "drift_pct": f"{round(drift_score * 100, 2)}%",
            "is_rejected": is_rejected,
            "rejection_reason": (
                f"Judicial drift score {round(drift_score * 100, 1)}% "
                f"exceeds {self.DRIFT_THRESHOLD * 100}% strict limit." if is_rejected else "Passed textualist baseline"
            )
        }

    def compare_search_against_active_case(self, case_id: str, search_results: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Cross-validates live search results against an active case file.
        
        Filters out search results that:
          1. Exhibit high judicial drift (>25%).
          2. Contradict established black-letter terms or case facts.
        """
        if case_id not in self.active_casework:
            raise ValueError(f"Case ID '{case_id}' not found in active casework database.")

        case = self.active_casework[case_id]
        key_terms = set(case.get("statutes_involved", []) + list(case.get("defined_terms", {}).keys()))

        aligned_results = []
        rejected_results = []

        for doc in search_results:
            content = doc.get("content", "")
            
            # Step 1: Textual drift evaluation
            eval_res = self.evaluate_legal_text(content)
            doc["legal_text_analysis"] = eval_res

            if eval_res["is_rejected"]:
                doc["rejection_cause"] = f"Judicial Drift ({eval_res['drift_pct']})"
                rejected_results.append(doc)
                continue

            # Step 2: Key term and fact alignment
            content_lower = content.lower()
            matched_terms = [term for term in key_terms if term.lower() in content_lower]
            doc["matched_statutory_terms"] = matched_terms

            # Require at least one direct statutory or fact alignment match if key terms exist
            if key_terms and not matched_terms:
                doc["rejection_cause"] = "No direct statutory term alignment with active case"
                rejected_results.append(doc)
            else:
                aligned_results.append(doc)

        return aligned_results, rejected_results
