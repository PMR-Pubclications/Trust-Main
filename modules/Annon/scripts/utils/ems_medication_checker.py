#!/usr/bin/env python3
"""EMS Clinical Decision Support & Pre-Hospital Medication Safety System.

Mapped to: modules/Annon/scripts/utils/ems_medication_checker.py
Cross-checks proposed emergency field medications against hospital EHR records,
active prescriptions, and known patient allergies to flag fatal contraindications.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


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


# Common EMS Emergency Drugs & Clinical Knowledge Base
# Standardized against RxNorm / NEMSIS clinical safety protocols
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

    def evaluate_safety(self, proposed_medication: str, patient: PatientEHR) -> List[SafetyAlert]:
        alerts: List[SafetyAlert] = []
        target_info = self.find_drug_entry(proposed_medication)

        norm_target = self.normalize_name(proposed_medication)
        
        # 1. Direct & Class Allergy Check
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
            return alerts

        primary_name, drug_data = target_info

        # 2. Drug-Drug Interaction Check against Hospital EHR Active Meds
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

        return alerts


def format_field_display(alerts: List[SafetyAlert], patient: PatientEHR) -> str:
    """Renders high-visibility terminal alerts for paramedics in field conditions."""
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
    # Example Hospital EHR Record (Retrieved via HL7 FHIR / Health Information Exchange)
    sample_ehr = PatientEHR(
        patient_id="EHR-88392",
        name="John Doe",
        age=58,
        allergies=["Penicillin", "Salicylate Allergy"],
        active_medications=["Sildenafil 50mg", "Lisinopril 10mg", "Warfarin 5mg"],
        medical_conditions=["Coronary Artery Disease", "Severe Asthma"]
    )

    checker = PreHospitalMedicationChecker()

    # Scenario 1: Paramedic prepares to give Nitroglycerin for chest pain (CONFLICT: Sildenafil)
    print(format_field_display(checker.evaluate_safety("Nitroglycerin", sample_ehr), sample_ehr))

    # Scenario 2: Paramedic prepares to give Aspirin for chest pain (CONFLICT: Salicylate Allergy & Warfarin)
    print(format_field_display(checker.evaluate_safety("Aspirin", sample_ehr), sample_ehr))
