import json
import os
import re
from typing import Dict, List, Set, Tuple

class LinguisticPropagandaAnalyzer:
    """
    Evaluates text objectivity and computes a Propaganda Score (0.0 to 1.0 / 0% to 100%).
    
    Enforces a strict 20% Hard Rejection Threshold. Contextually differentiates between
    empirical/legal noun usage and copular rhetorical adjectival smears.
    
    Dynamic Learning Integration:
      - Persists active lexicon state to local JSON (`Annon/data/lexicon_state.json`).
      - Dynamically compiles regex patterns from the live lexicon at runtime.
      - Automatically extracts candidate loaded nouns and empirical anchors from analyzed
        corpora via syntax pattern recognition and updates word frequencies.
    """

    PROPAGANDA_THRESHOLD = 0.20  # Max allowable propaganda probability (20%)
    STATE_FILE_PATH = os.path.join("Annon", "data", "lexicon_state.json")

    # Seed Defaults (fallback if no persistent state exists)
    DEFAULT_LOADED_NOUNS = {
        "nazi", "communist", "fascist", "traitor", "puppet", 
        "shill", "criminal", "tyrant", "extremist", "crook", "grifter"
    }

    DEFAULT_EMPIRICAL_ANCHORS = {
        "party", "member", "official", "candidate", "regime", "ideology", "movement",
        "charged", "convicted", "indicted", "statute", "under", "court", "docket",
        "law", "article", "history", "historical", "era", "definition", "defined",
        "registered", "affiliated"
    }

    DEFAULT_COPULAR_TRIGGERS = {
        r"\b(is|are|was|were|became|turns? into)\b",
        r"\b(nothing but|clearly|obviously|basically|just|a total|a complete)\b"
    }

    DEFAULT_PURE_EPITHETS = {
        "radical", "corrupt", "bootlicker", "denier", "warmonger", 
        "alarmist", "zealot", "pawn", "bigot", "huckster", "charlatan"
    }

    DEFAULT_EMOTIONAL_TRIGGERS = {
        "devastating", "outrageous", "terrifying", "tragic", "heartbreaking", "shocking",
        "unconscionable", "disgraceful", "horrific", "reprehensible", "evil", "monstrous",
        "unprecedented", "existential threat", "disaster", "catastrophe", "crisis",
        "slammed", "blasted", "eviscerated"
    }

    def __init__(self, state_path: str = None):
        self.state_file_path = state_path or self.STATE_FILE_PATH
        
        # State containers
        self.loaded_nouns: Set[str] = set()
        self.empirical_anchors: Set[str] = set()
        self.copular_triggers: Set[str] = set()
        self.pure_epithets: Set[str] = set()
        self.emotional_triggers: Set[str] = set()
        
        # Candidate tracking for dynamic auto-learning (word -> observed count)
        self.candidate_nouns: Dict[str, int] = {}
        self.candidate_anchors: Dict[str, int] = {}

        self.load_state()

    def load_state(self) -> None:
        """Loads active lexicon and learned weights from persistent storage."""
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.loaded_nouns = set(data.get("loaded_nouns", self.DEFAULT_LOADED_NOUNS))
                    self.empirical_anchors = set(data.get("empirical_anchors", self.DEFAULT_EMPIRICAL_ANCHORS))
                    self.copular_triggers = set(data.get("copular_triggers", self.DEFAULT_COPULAR_TRIGGERS))
                    self.pure_epithets = set(data.get("pure_epithets", self.DEFAULT_PURE_EPITHETS))
                    self.emotional_triggers = set(data.get("emotional_triggers", self.DEFAULT_EMOTIONAL_TRIGGERS))
                    self.candidate_nouns = data.get("candidate_nouns", {})
                    self.candidate_anchors = data.get("candidate_anchors", {})
                    return
            except Exception as e:
                print(f"[LEXICON WARNING] Failed to load state: {e}. Falling back to default seed.")

        # Fallback to defaults
        self.loaded_nouns = set(self.DEFAULT_LOADED_NOUNS)
        self.empirical_anchors = set(self.DEFAULT_EMPIRICAL_ANCHORS)
        self.copular_triggers = set(self.DEFAULT_COPULAR_TRIGGERS)
        self.pure_epithets = set(self.DEFAULT_PURE_EPITHETS)
        self.emotional_triggers = set(self.DEFAULT_EMOTIONAL_TRIGGERS)

    def save_state(self) -> None:
        """Persists the updated active lexicon and candidate tracking back to disk."""
        os.makedirs(os.path.dirname(self.state_file_path), exist_ok=True)
        data = {
            "loaded_nouns": list(self.loaded_nouns),
            "empirical_anchors": list(self.empirical_anchors),
            "copular_triggers": list(self.copular_triggers),
            "pure_epithets": list(self.pure_epithets),
            "emotional_triggers": list(self.emotional_triggers),
            "candidate_nouns": self.candidate_nouns,
            "candidate_anchors": self.candidate_anchors
        }
        with open(self.state_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def register_term(self, category: str, term: str, auto_save: bool = True) -> None:
        """Dynamically expands the live lexicon with new terms as Annon learns."""
        term_clean = term.strip().lower()
        if not term_clean:
            return

        if category == "loaded_noun":
            self.loaded_nouns.add(term_clean)
        elif category == "empirical_anchor":
            self.empirical_anchors.add(term_clean)
        elif category == "pure_epithet":
            self.pure_epithets.add(term_clean)
        elif category == "emotional_trigger":
            self.emotional_triggers.add(term_clean)

        if auto_save:
            self.save_state()

    def _compile_loaded_noun_regex(self) -> str:
        escaped = [re.escape(w) for w in sorted(self.loaded_nouns, key=len, reverse=True)]
        return r"\b(" + "|".join(escaped) + r")\s*(s|es)?\b" if escaped else r"$^"

    def _compile_empirical_regex(self) -> str:
        escaped = [re.escape(w) for w in sorted(self.empirical_anchors, key=len, reverse=True)]
        return r"\b(" + "|".join(escaped) + r")\b" if escaped else r"$^"

    def _compile_pure_epithet_regex(self) -> str:
        escaped = [re.escape(w) for w in sorted(self.pure_epithets, key=len, reverse=True)]
        return r"\b(" + "|".join(escaped) + r")\b" if escaped else r"$^"

    def _compile_emotional_regex(self) -> str:
        escaped = [re.escape(w) for w in sorted(self.emotional_triggers, key=len, reverse=True)]
        return r"\b(" + "|".join(escaped) + r")\b" if escaped else r"$^"

    def auto_learn_from_text(self, text: str, promotion_threshold: int = 3) -> List[str]:
        """
        Scans text for novel terms functioning as predicate epithets in copular structures
        ([copula] + a/an + [noun]) and promotes them to the active lexicon once seen 
        beyond the threshold count.
        """
        learned_terms = []
        sentences = re.split(r"[.!?]+", text.lower())

        # Pattern targeting copular noun slots: e.g. "is a [unknown_word]"
        candidate_pattern = r"\b(?:is|are|was|were|became)\s+(?:a|an|total|complete)\s+([a-z]{3,18})\b"

        for sentence in sentences:
            matches = re.findall(candidate_pattern, sentence)
            for word in matches:
                if (word not in self.loaded_nouns and 
                    word not in self.pure_epithets and 
                    word not in self.empirical_anchors):
                    
                    self.candidate_nouns[word] = self.candidate_nouns.get(word, 0) + 1
                    
                    # Auto-promote once candidate crosses frequency threshold
                    if self.candidate_nouns[word] >= promotion_threshold:
                        self.register_term("loaded_noun", word, auto_save=False)
                        learned_terms.append(word)

        if learned_terms or self.candidate_nouns:
            self.save_state()

        return learned_terms

    def _evaluate_loaded_nouns(self, text: str) -> Tuple[int, int]:
        sentences = re.split(r"[.!?]+", text.lower())
        empirical_count = 0
        rhetorical_count = 0

        loaded_regex = self._compile_loaded_noun_regex()
        empirical_regex = self._compile_empirical_regex()

        for sentence in sentences:
            matches = re.findall(loaded_regex, sentence)
            if not matches:
                continue

            has_empirical_anchor = bool(re.search(empirical_regex, sentence))
            has_copular_attack = any(re.search(pat, sentence) for pat in self.copular_triggers)

            for _ in matches:
                if has_empirical_anchor and not has_copular_attack:
                    empirical_count += 1
                elif has_copular_attack and not has_empirical_anchor:
                    rhetorical_count += 1
                elif has_empirical_anchor and has_copular_attack:
                    if re.search(r"\b(charged|convicted|indicted|statute|docket|party)\b", sentence):
                        empirical_count += 1
                    else:
                        rhetorical_count += 1
                else:
                    empirical_count += 1

        return empirical_count, rhetorical_count

    def analyze_text(self, text: str, enable_auto_learning: bool = True) -> Dict:
        words = re.findall(r"\b\w+\b", text.lower())
        total_words = len(words)

        if total_words == 0:
            return {
                "propaganda_probability": 1.0,
                "is_rejected": True,
                "rejection_reason": "Empty text body"
            }

        # 1. Execute auto-learning on incoming raw stream
        newly_learned = []
        if enable_auto_learning:
            newly_learned = self.auto_learn_from_text(text)

        # 2. Contextual evaluation using compiled live regex state
        empirical_loaded_nouns, rhetorical_smears = self._evaluate_loaded_nouns(text)

        pure_epithet_regex = self._compile_pure_epithet_regex()
        emotional_regex = self._compile_emotional_regex()

        pure_epithets_count = len(re.findall(pure_epithet_regex, text, re.IGNORECASE))
        emotional_count = len(re.findall(emotional_regex, text, re.IGNORECASE))
        descriptive_count = len(re.findall(r"\b\w+(ous|ful|less|able|ible|ive|ic|al|ish)\b|\b\w+ly\b", text, re.IGNORECASE))
        
        base_noun_count = len(re.findall(r"\b\d+(\.\d+)?\b|\b[A-Z][a-z]+\b|\b\w+(tion|ment|ence|ance|ity|ship|hood|dom)\b", text))
        total_noun_count = base_noun_count + empirical_loaded_nouns

        total_epithet_hits = pure_epithets_count + rhetorical_smears
        noun_descriptive_ratio = total_noun_count / (descriptive_count + 1.0)
        emotional_density = (total_epithet_hits + emotional_count) / float(total_words)

        # Composite score calculation
        epithet_score = min(1.0, (total_epithet_hits * 2.5) / max(1, total_words * 0.02))
        emotional_score = min(1.0, emotional_density / 0.03)
        fluff_score = max(0.0, 1.0 - (noun_descriptive_ratio / 2.0))

        propaganda_probability = round(
            (emotional_score * 0.45) + (epithet_score * 0.35) + (fluff_score * 0.20), 
            4
        )

        is_rejected = propaganda_probability > self.PROPAGANDA_THRESHOLD

        return {
            "total_words": total_words,
            "empirical_nouns_retained": empirical_loaded_nouns,
            "rhetorical_smears_penalized": rhetorical_smears,
            "newly_learned_terms": newly_learned,
            "propaganda_probability": propaganda_probability,
            "propaganda_pct": f"{round(propaganda_probability * 100, 2)}%",
            "is_rejected": is_rejected,
            "rejection_reason": (
                f"Propaganda probability {round(propaganda_probability * 100, 1)}% "
                f"exceeds 20.0% max limit." if is_rejected else "Passed threshold"
            )
        }

    def filter_propaganda_sources(self, search_results: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        retained, rejected = [], []
        for doc in search_results:
            content = doc.get("content", "")
            analysis = self.analyze_text(content)
            doc["propaganda_analysis"] = analysis

            if analysis["is_rejected"]:
                url = doc.get("metadata", {}).get("url", "unknown")
                print(f"[REJECTED - PROPAGANDA > 20%] Discarding '{url}' | Score: {analysis['propaganda_pct']}")
                rejected.append(doc)
            else:
                retained.append(doc)

        return retained, rejected
