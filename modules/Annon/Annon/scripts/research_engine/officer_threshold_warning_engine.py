import json
import re
from typing import Dict, List, Optional

class OfficerThresholdWarningEngine:
    """
    Evaluates residential entry scenarios and warrant integrity against 
    black-letter Fourth Amendment protections, curtilage rules, and Castle Doctrine risks.
    
    Legal Foundations:
      - Payton v. New York (1980): The threshold of the home is the firm line drawn by 
        the Fourth Amendment. Warrantless entry is presumptively unconstitutional.
      - Franks v. Delaware (1978): Warrants based on false statements, material omissions, 
        or tainted affidavits are void ab initio.
      - Self-Defense & Castle Doctrine: An unlawful threshold breach strips the protection 
        of lawful entry, creating extreme physical jeopardy where occupants may lawfully 
        or foreseeably treat entering personnel as intruder-trespassers.
    """

    # Warrant Deficiencies that void lawful authority
    WARRANT_FLAW_TRIGGERS = [
        r"\b(stale information|informant hearsay|uncorroborated tip)\b",
        r"\b(reckless disregard|material omission|false affidavit|franks violation)\b",
        r"\b(lack of particularity|broad scope|overbroad search|general warrant)\b",
        r"\b(unsigned warrant|lack of probable cause|magistrate rubber stamp)\b"
    ]

    # Exigent circumstances required for warrantless threshold entry
    EXIGENT_CIRCUMSTANCES = [
        r"\b(hot pursuit|imminent destruction of evidence|active threat to life|emergency doctrine)\b"
    ]

    @classmethod
    def evaluate_entry_threat(cls, entry_scenario: Dict) -> Dict:
        """
        Evaluates the legal validity of a planned or active residential entry 
        and computes operational hazard warnings for officers.
        
        entry_scenario = {
            "has_warrant": bool,
            "warrant_affidavit_summary": str,
            "has_exigent_circumstances": bool,
            "exigent_narrative": str,
            "jurisdiction_castle_doctrine": bool,
            "knock_and_announce": bool
        }
        """
        warnings = []
        legal_violations = []
        tactical_hazard_level = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL

        has_warrant = entry_scenario.get("has_warrant", False)
        affidavit = entry_scenario.get("warrant_affidavit_summary", "")
        has_exigent = entry_scenario.get("has_exigent_circumstances", False)
        exigent_narrative = entry_scenario.get("exigent_narrative", "")
        castle_doctrine = entry_scenario.get("jurisdiction_castle_doctrine", True)
        knock_announce = entry_scenario.get("knock_and_announce", True)

        # 1. Warrant Integrity Analysis (Franks v. Delaware / Particularity Check)
        warrant_tainted = False
        if has_warrant:
            flaw_matches = [
                pattern for pattern in cls.WARRANT_FLAW_TRIGGERS 
                if re.search(pattern, affidavit, re.IGNORECASE)
            ]
            if flaw_matches:
                warrant_tainted = True
                legal_violations.append(
                    f"WARRANT VOID RISK: Affidavit contains potential defects ({', '.join(flaw_matches)}). "
                    "Entry based on a defective warrant places officers in the status of unlawful trespassers."
                )

        # 2. Warrantless Threshold Breach Analysis (Payton v. New York)
        valid_exigency = False
        if not has_warrant or warrant_tainted:
            if has_exigent:
                exigency_matches = [
                    pattern for pattern in cls.EXIGENT_CIRCUMSTANCES 
                    if re.search(pattern, exigent_narrative, re.IGNORECASE)
                ]
                if exigency_matches:
                    valid_exigency = True
                else:
                    legal_violations.append(
                        "UNLAWFUL ENTRY RISK: Stated exigency fails black-letter Fourth Amendment threshold tests. "
                        "Entry without a valid warrant or verified exigency is per se unconstitutional."
                    )
            else:
                legal_violations.append(
                    "CRITICAL CONSTITUTIONAL VIOLATION: Zero warrant and zero exigent circumstances. "
                    "Crossing the home threshold violates Payton v. New York."
                )

        # 3. Tactical Officer Hazard & Trespasser Classification
        is_unlawful_entry = (not has_warrant and not valid_exigency) or warrant_tainted

        if is_unlawful_entry:
            tactical_hazard_level = "CRITICAL"
            warnings.append(
                "OFFICER SAFETY WARNING: Threshold breach lacks legal authority. "
                "Under black-letter property and self-defense doctrine, occupants possess a legal and "
                "factual basis to perceive entering forces as armed trespassers/intruders."
            )
            
            if castle_doctrine:
                warnings.append(
                    "HIGH-LETHALITY HAZARD: Jurisdiction recognizes Castle Doctrine / Defense of Habitation. "
                    "Occupant force response risk is extreme. ABORT DYNAMIC ENTRY and establish perimeter pending valid judicial authorization."
                )

        elif not knock_announce and has_warrant:
            tactical_hazard_level = "HIGH"
            warnings.append(
                "TACTICAL WARNING: No-knock threshold breach increases intruder-misidentification risk. "
                "Ensure positive identification and immediate audible color-of-law announcement."
            )

        return {
            "tactical_hazard_level": tactical_hazard_level,
            "is_unlawful_threshold_breach": is_unlawful_entry,
            "warrant_void_flag": warrant_tainted,
            "legal_violations": legal_violations,
            "officer_advisories": warnings,
            "recommended_action": (
                "ABORT THRESHOLD BREACH - HOLD PERIMETER & VERIFY WARRANT" 
                if is_unlawful_entry else "PROCEED WITH COLOR-OF-LAW ANNOUNCEMENT"
            )
        }
