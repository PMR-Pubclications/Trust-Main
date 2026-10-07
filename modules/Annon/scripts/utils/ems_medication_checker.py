#!/usr/bin/env python3
"""EMS Clinical Decision Support & Pre-Hospital Medication Safety System.

Mapped to: modules/Annon/scripts/utils/ems_medication_checker.py
Features real-time text-to-speech (TTS) voice alerts ("Good to go" vs "Don't administer that")
optimized for noisy field conditions and immediate paramedic decision support.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Initialize Text-to-Speech Engine (pyttsx3 or System Voice Fallback)
try:
    import pyttsx3  # type: ignore
    TTS_ENGINE = pyttsx3.init()
    TTS_ENGINE.setProperty('rate', 160)  # Paced speaking rate for high-noise field environments
    TTS_ENGINE.setProperty('volume', 1.0)
except Exception:
    TTS_ENGINE = None


class AlertSeverity(Enum):
    SAFE = "SAFE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL_CONTRAINDICATION"


@dataclass
class PatientEHR:
    patient_id: str
    name: str
    age: int
    allergies: List[str] = field(default_factory=list)
    active_medications: List[str] = field(default_factory=list)
    medical_conditions: List[str] = field(default_factory=list)


@dataclass
class SafetyAlert:
    severity: AlertSeverity
    target_medication: str
    conflict_type: str  # ALLERGY, DRUG_INTERACTION, CONDITION_CONTRAINDICATION
    conflicting_agent: str
    description: str
    clinical_risk: str


EMERGENCY_DRUG_DATABASE: Dict[str, dict] = {
    "nitroglycerin": {
        "rxnorm_id": "7052",
        "aliases": ["nitro", "nitrostat", "nitroglycerine"],
        "drug_class": "nitrates",
        "contraindicated_drugs": {
            "sildenafil": "Fatal Hypotension Risk: Severe blood pressure drop when combined with PDE5 inhibitors (Viagra).",
            "tadalafil": "Fatal Hypotension Risk: Severe prolonged hypotension when combined with PDE5 inhibitors (Cialis).",
            "vardenafil": "Fatal Hypotension Risk: Severe blood pressure collapse."
        },
        "contraindicated_conditions": {
            "severe hypotension": "Systolic blood pressure < 90 mmHg.",
            "right ventricular infarction": "Preload dependence; can trigger fatal cardiovascular collapse."
        }
    },
    "epinephrine": {
        "rxnorm_id": "3992",
        "aliases": ["epi", "adrenalin"],
        "drug_class": "sympathomimetic",
        "contraindicated_drugs": {
            "propranolol": "Severe Hypertension & Reflex Bradycardia: Unopposed alpha-adrenergic vasoconstriction from non-selective beta-blockers."
        },
        "contraindicated_conditions": {}
    },
    "morphine": {
        "rxnorm_id": "7052",
        "aliases": ["ms contin", "morphine sulfate"],
        "drug_class": "opioids",
        "contraindicated_drugs": {
            "fentanyl": "Synergistic Respiratory Depression: Severe overdose and hypoventilation risk.",
            "alprazolam": "Profound Sedation & Respiratory Arrest: Central nervous system depression."
        },
        "contraindicated_conditions": {
            "severe asthma": "Histamine release triggering severe bronchospasm.",
            "respiratory depression": "Exacerbates respiratory failure."
        }
    },
    "aspirin": {
        "rxnorm_id": "1191",
        "aliases": ["asa", "acetylsalicylic acid"],
        "drug_class": "nsaids",
        "contraindicated_drugs": {
            "warfarin": "Lethal Bleeding Risk: Compound anticoagulation effect.",
            "apixaban": "Severe Internal Hemorrhage Risk."
        },
        "contraindicated_conditions": {
            "active gastrointestinal bleed": "Exacerbates major internal bleeding.",
            "salicylate allergy": "Anaphylaxis / severe airway compromise."
        }
    }
}


def speak_alert(alerts: List[SafetyAlert], target_medication: str) -> None:
    """Triggers instant audible voice alerts through system audio."""
    has_critical = any(a.severity == AlertSeverity.CRITICAL_CONTRAINDICATION for a in alerts)

    if has_critical:
        phrase = f"Stop! Don't administer that! Critical contraindication detected for {target_medication}."
    elif any(a.severity == AlertSeverity.WARNING for a in alerts):
        phrase = f"Caution. Review warning for {target_medication}."
    else:
        phrase = f"Good to go! {target_medication} is clear."

    print(f"\n🔊 AUDIBLE ALERT: \"{phrase}\"\n")

    # Primary TTS via pyttsx3
    if TTS_ENGINE:
        try:
            TTS_ENGINE.say(phrase)
            TTS_ENGINE.runAndWait()
            return
        except Exception:
            pass

    # Native OS fallback voice commands (macOS say, Linux espeak, Windows PowerShell SAPI)
    try:
        if sys.platform == "darwin":
            subprocess.run(["say", phrase], check=False)
        elif sys.platform.startswith("linux"):
            subprocess.run(["espeak", phrase], stderr=subprocess.DEVNULL, check=False)
        elif sys.platform == "win32":
            ps_cmd = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{phrase}");'
            subprocess.run(["powershell", "-Command", ps_cmd], check=False)
    except Exception as e:
        print(f"⚠️ Unable to render audio alert: {e}")


class PreHospitalMedicationChecker:
    """Evaluates field drug administration against patient records in real-time."""

    def __init__(self, drug_db: Optional[Dict[str, dict]] = None):
        self.drug_db = drug_db or EMERGENCY_DRUG_DATABASE

    def normalize_name(self, name: str) -> str:
        return name.lower().strip()

    def find_drug_entry(self, med_name: str) -> Optional[Tuple[str, dict]]:
        norm = self.normalize_name(med_name)
        for primary_name, data in self.drug_db.items():
            if norm == primary_name or norm in data.get("aliases", []):
                return primary_name, data
        return None

    def evaluate_safety(self, proposed_medication: str, patient: PatientEHR, speak: bool = True) -> List[SafetyAlert]:
        alerts: List[SafetyAlert] = []
        target_info = self.find_drug_entry(proposed_medication)
        norm_target = self.normalize_name(proposed_medication)

        # 1. Direct Allergy Check
        for allergy in patient.allergies:
            norm_allergy = self.normalize_name(allergy)
            if norm_target in norm_allergy or norm_allergy in norm_target:
                alerts.append(
                    SafetyAlert(
                        severity=AlertSeverity.CRITICAL_CONTRAINDICATION,
                        target_medication=proposed_medication,
                        conflict_type="ALLERGY",
                        conflicting_agent=allergy,
                        description=f"Patient has a documented direct allergy to {allergy}.",
                        clinical_risk="HIGH RISK OF ANAPHYLACTIC SHOCK OR AIRWAY COMPROMISE."
                    )
                )

        if not target_info:
            if not alerts:
                alerts.append(
                    SafetyAlert(
                        severity=AlertSeverity.WARNING,
                        target_medication=proposed_medication,
                        conflict_type="UNKNOWN_DRUG",
                        conflicting_agent="N/A",
                        description=f"'{proposed_medication}' not found in local EMS database.",
                        clinical_risk="Proceed with caution. Verify manually with On-Duty Medical Control."
                    )
                )
            if speak:
                speak_alert(alerts, proposed_medication)
            return alerts

        primary_name, drug_data = target_info

        # 2. Drug-Drug Interaction Check
        active_meds = [self.normalize_name(m) for m in patient.active_medications]
        for contraindicated_drug, risk_desc in drug_data.get("contraindicated_drugs", {}).items():
            for active_med in active_meds:
                if contraindicated_drug in active_med:
                    alerts.append(
                        SafetyAlert(
                            severity=AlertSeverity.CRITICAL_CONTRAINDICATION,
                            target_medication=proposed_medication,
                            conflict_type="DRUG_INTERACTION",
                            conflicting_agent=active_med,
                            description=f"Interaction between {proposed_medication.title()} and active prescription {active_med.title()}.",
                            clinical_risk=risk_desc
                        )
                    )

        # 3. Medical Condition Contraindications
        patient_conditions = [self.normalize_name(c) for c in patient.medical_conditions]
        for condition, risk_desc in drug_data.get("contraindicated_conditions", {}).items():
            for patient_cond in patient_conditions:
                if condition in patient_cond:
                    alerts.append(
                        SafetyAlert(
                            severity=AlertSeverity.CRITICAL_CONTRAINDICATION,
                            target_medication=proposed_medication,
                            conflict_type="CONDITION_CONTRAINDICATION",
                            conflicting_agent=patient_cond,
                            description=f"{proposed_medication.title()} is contraindicated for patient condition: {patient_cond.title()}.",
                            clinical_risk=risk_desc
                        )
                    )

        if not alerts:
            alerts.append(
                SafetyAlert(
                    severity=AlertSeverity.SAFE,
                    target_medication=proposed_medication,
                    conflict_type="NONE",
                    conflicting_agent="NONE",
                    description="No direct contraindications found in hospital record.",
                    clinical_risk="Safe to administer per standard local EMS protocols."
                )
            )

        # Trigger Audio Output
        if speak:
            speak_alert(alerts, proposed_medication)

        return alerts


def format_field_display(alerts: List[SafetyAlert], patient: PatientEHR) -> str:
    """Renders high-visibility terminal text for field tablet screens."""
    output = []
    output.append("================================================================================")
    output.append(f" 🚨 PRE-HOSPITAL MEDICATION SAFETY CHECK | PATIENT: {patient.name.upper()} (ID: {patient.patient_id})")
    output.append("================================================================================")

    has_critical = any(a.severity == AlertSeverity.CRITICAL_CONTRAINDICATION for a in alerts)

    if has_critical:
        output.append(" 🔴 [ALERT: DO NOT ADMINISTER - FATAL CONTRAINDICATION DETECTED] 🔴\n")
    else:
        output.append(" 🟢 [CLEAR: NO CRITICAL CONFLICTS DETECTED] 🟢\n")

    for idx, alert in enumerate(alerts, 1):
        output.append(f"  Alert #{idx} [{alert.severity.value}]")
        output.append(f"  - Proposed Drug:   {alert.target_medication.upper()}")
        output.append(f"  - Conflict Type:   {alert.conflict_type}")
        output.append(f"  - Conflicting Item:{alert.conflicting_agent}")
        output.append(f"  - Clinical Risk:   {alert.clinical_risk}")
        output.append(f"  - Details:         {alert.description}")
        output.append("  " + "-" * 70)

    return "\n".join(output)


if __name__ == "__main__":
    sample_ehr = PatientEHR(
        patient_id="EHR-88392",
        name="John Doe",
        age=58,
        allergies=["Penicillin", "Salicylate Allergy"],
        active_medications=["Sildenafil 50mg", "Lisinopril 10mg"],
        medical_conditions=["Coronary Artery Disease"]
    )

    checker = PreHospitalMedicationChecker()

    # TEST 1: Dangerous Call -> Triggers "Stop! Don't administer that!"
    print("--- SCENARIO 1: NITROGLYCERIN CHECK ---")
    alerts_1 = checker.evaluate_safety("Nitroglycerin", sample_ehr, speak=True)
    print(format_field_display(alerts_1, sample_ehr))

    # TEST 2: Safe Call -> Triggers "Good to go!"
    print("\n--- SCENARIO 2: EPINEPHRINE CHECK ---")
    alerts_2 = checker.evaluate_safety("Epinephrine", sample_ehr, speak=True)
    print(format_field_display(alerts_2, sample_ehr))
