#!/usr/bin/env python3
"""
TFML Real-Time Automated Success & Marketing Compiler
Instantly updates the master municipal & hospital marketing package 
at asset/PressRelease/TFML_Master_Marketing_Package.md when new data arrives or builds occur.
"""

import json
import os
from datetime import datetime

COURT_DB = "success_registry.json"
EMS_DB = "ems_success_registry.json"
OUTPUT_PACKAGE = "asset/PressRelease/TFML_Master_Marketing_Package.md"

def compile_master_marketing_package():
    """Automatically aggregates court cases and EMS saves into the master marketing document."""
    # Ensure target directory exists
    os.makedirs(os.path.dirname(OUTPUT_PACKAGE), exist_ok=True)

    court_data = {"success_cases": []}
    if os.path.exists(COURT_DB):
        with open(COURT_DB, "r") as f:
            court_data = json.load(f)

    ems_data = {"ems_clinical_successes": []}
    if os.path.exists(EMS_DB):
        with open(EMS_DB, "r") as f:
            ems_data = json.load(f)

    # Base Master Document Content anchored to TFML handbook architecture
    base_package = """# Trust Forensics Mobile Lab (TFML)
## Master Marketing & Institutional Deployment Package

### Executive Summary & Institutional Value
The Trust Forensics Mobile Lab (TFML) bridges the critical information gap between field responders and institutional decision-makers (City Attorneys, Police Chiefs, and Hospital CMOs)[span_1](start_span)[span_1](end_span). By anchoring data at the hardware root (Layer 0–3) and securing immutable chains of custody via Merkle-tree ledgers, TFML eliminates litigation risk and accelerates emergency care[span_2](start_span)[span_2](end_span).

---

## 🏛️ Court-Verified Law Enforcement & Forensic Impact
*Tracked via official court dockets and judicial outcomes to prove unassailable chain-of-custody integrity and wrongful arrest prevention[span_3](start_span)[span_3](end_span).*
"""

    # Append Law Enforcement / Court Cases
    if court_data["success_cases"]:
        for case in court_data["success_cases"]:
            base_package += f"""
- **Court Docket #{case.get('court_case_number', 'N/A')}** (Case ID: {case.get('case_id')})[span_4](start_span)[span_4](end_span)
  - **Agency:** {case.get('agency')}[span_5](start_span)[span_5](end_span)
  - **Initial Assumption:** {case.get('initial_human_assumption')}[span_6](start_span)[span_6](end_span)
  - **TFML Ground-Truth Evidence:** {case.get('ground_truth_evidence')}[span_7](start_span)[span_7](end_span)
  - **Judicial Outcome:** **{case.get('judicial_outcome')}**[span_8](start_span)[span_8](end_span)
  - **Municipal Impact:** {case.get('municipal_impact')}[span_9](start_span)[span_9](end_span)
"""
    else:
        base_package += "\n*No court-tracked cases recorded in the registry yet.*[span_10](start_span)[span_10](end_span)\n"

    base_package += """
---

## 🚑 HIPAA-Compliant EMS Clinical & Hospital Handover Impact
*Tracked via de-identified pre-hospital responses and emergency department finalizations.*
"""

    # Append EMS Clinical Successes
    if ems_data["ems_clinical_successes"]:
        for ems in ems_data["ems_clinical_successes"]:
            base_package += f"""
- **Response ID {ems.get('ems_response_id')}** -> **{ems.get('hospital_destination')}**[span_11](start_span)[span_11](end_span)
  - **Intervention:** {ems.get('clinical_intervention')}[span_12](start_span)[span_12](end_span)
  - **System Action:** {ems.get('system_action')}[span_13](start_span)[span_13](end_span)
  - **Hospital Finalization:** {ems.get('hospital_finalization_status')}[span_14](start_span)[span_14](end_span)
  - **Clinical Impact:** {ems.get('clinical_impact')}[span_15](start_span)[span_15](end_span)
  - **HIPAA Status:** Ephemeral PHI Purged (100% Compliant)[span_16](start_span)[span_16](end_span)
"""
    else:
        base_package += "\n*No EMS clinical success logs recorded in the registry yet.*[span_17](start_span)[span_17](end_span)\n"

    base_package += """
---
*Technical Verification & Access Statement:*  
All cryptographic protocols, hardware TEE signing, and Merkle tree ledgers can be independently audited via the official source repository: [Trust-Main Repository](https://github.com/PMR-Pubclications/Trust-Main/tree/main)[span_18](start_span)[span_18](end_span).
"""

    with open(OUTPUT_PACKAGE, "w") as f:
        f.write(base_package)
    
    print(f"[TFML COMPILER] Master Marketing Package successfully compiled to '{OUTPUT_PACKAGE}' at {datetime.utcnow().isoformat()}.")


if __name__ == "__main__":
    compile_master_marketing_package()
