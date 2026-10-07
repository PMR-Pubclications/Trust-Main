#!/usr/bin/env python3
"""EMS Real-Time Medication Execution Interceptor.

Provides an immediate binary gate check (PROCEED vs. ABORT) based on hospital 
EHR conflict analysis to physically/programmatically lock or allow field drug administration.
"""

from __future__ import annotations

import subprocess
import sys
from enum import Enum
from typing import Dict, Any


class ActionDecision(Enum):
    PROCEED = "PROCEED"
    STOP_ABORT = "STOP_ABORT"


def trigger_voice_command(decision: ActionDecision, med_name: str, reason: str = "") -> None:
    """Delivers unambiguous field audio instructions to the medic."""
    if decision == ActionDecision.STOP_ABORT:
        phrase = f"Stop! Don't administer {med_name}! {reason}"
    else:
        phrase = f"Good to go. {med_name} is clear to administer."

    print(f"\n🔊 [VOICE ALERT]: \"{phrase}\"")

    # Audio synthesis execution
    try:
        if sys.platform == "darwin":
            subprocess.run(["say", phrase], check=False)
        elif sys.platform.startswith("linux"):
            subprocess.run(["espeak", phrase], stderr=subprocess.DEVNULL, check=False)
        elif sys.platform == "win32":
            ps_cmd = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{phrase}");'
            subprocess.run(["powershell", "-Command", ps_cmd], check=False)
    except Exception as e:
        print(f"⚠️ Audio output unavailable: {e}")


def verify_and_authorize_medication(proposed_med: str, patient_ehr: Dict[str, Any]) -> bool:
    """Core decision gate for EMS field tools and smart IV pumps.
    
    Returns:
        True  -> Action Authorized (PROCEED)
        False -> Action Blocked (STOP / ABORT)
    """
    target_med = proposed_med.strip().lower()
    allergies = [a.lower() for a in patient_ehr.get("allergies", [])]
    active_meds = [m.lower() for m in patient_ehr.get("active_medications", [])]

    # 1. Direct Allergy Intercept
    for allergy in allergies:
        if target_med in allergy or allergy in target_med:
            reason = f"Documented direct allergy: {allergy.title()}."
            trigger_voice_command(ActionDecision.STOP_ABORT, proposed_med, reason)
            return False

    # 2. Known Fatal High-Risk Conflicts Matrix
    critical_conflicts = {
        "nitroglycerin": ["sildenafil", "tadalafil", "vardenafil", "viagra", "cialis"],
        "aspirin": ["warfarin", "coumadin", "apixaban", "eliquis"],
        "morphine": ["fentanyl", "alprazolam", "xanax"],
        "epinephrine": ["propranolol"]
    }

    if target_med in critical_conflicts:
        blocked_drugs = critical_conflicts[target_med]
        for active in active_meds:
            if any(blocked in active for blocked in blocked_drugs):
                reason = f"Fatal interaction with patient's active prescription: {active.title()}."
                trigger_voice_command(ActionDecision.STOP_ABORT, proposed_med, reason)
                return False

    # 3. Clear to Administer
    trigger_voice_command(ActionDecision.PROCEED, proposed_med)
    return True


# ==============================================================================
# Usage Example / Integration Point
# ==============================================================================
if __name__ == "__main__":
    # Simulated FHIR Patient EHR payload retrieved from hospital database
    patient_record = {
        "patient_id": "EHR-99402",
        "allergies": ["Penicillin", "Salicylates"],
        "active_medications": ["Sildenafil 50mg", "Lisinopril 10mg"]
    }

    # Case 1: High-risk call -> Blocks administration & triggers "STOP" alert
    is_safe = verify_and_authorize_medication("Nitroglycerin", patient_record)
    print(f"Execution Gate Status: {'[AUTHORIZED]' if is_safe else '[BLOCKED]'}")

    # Case 2: Safe call -> Authorizes administration & triggers "Good to go"
    is_safe = verify_and_authorize_medication("Epinephrine", patient_record)
    print(f"Execution Gate Status: {'[AUTHORIZED]' if is_safe else '[BLOCKED]'}")
