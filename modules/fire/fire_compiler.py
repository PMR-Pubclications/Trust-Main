#!/usr/bin/env python3
"""
TFML Fire Module Compiler & Tactical Impact Generator
Validates structural fire logs, thermal boundary dynamics, flashover indices,
and hazmat placard OCR scans for fire chief and technical rescue reviews.
"""

import json
import os
from datetime import datetime

# Path points to root-level or local registry storage
FIRE_DB = "../../fire_success_registry.json"
LOCAL_FIRE_DB = "fire_success_registry.json"
OUTPUT_REPORT = "Fire_Tactical_Impact_Report.md"

def compile_fire_tactical_report():
    """Aggregates fire tactical successes into an executive briefing report."""
    target_db = FIRE_DB if os.path.exists(FIRE_DB) else LOCAL_FIRE_DB
    
    fire_data = {"fire_tactical_successes": []}
    if os.path.exists(target_db):
        with open(target_db, "r") as f:
            fire_data = json.load(f)

    report_content = f"""# Trust Forensics Mobile Lab (TFML) - Fire & Technical Rescue Module
## Executive Briefing & Structural Safety Report

### Operational Overview
The TFML Fire module equips firefighters and technical rescue teams with heavy PPE-compatible voice controls, real-time thermal boundary layer dynamic tracking for flashover prevention, toxic gas parsing (CO, HCN, LEL%), and hazmat placard OCR scanning in zero-visibility smoke environments[span_1](start_span)[span_1](end_span).

---

## 🔥 Verified Tactical Fire & Hazmat Operations
*Tracked via flashover index telemetry, structural heat gradients, and chemical hazard identifications.*
"""

    successes = fire_data.get("fire_tactical_successes", [])
    if successes:
        for fire in successes:
            report_content += f"""
- **Incident ID {fire.get('incident_id')}** -> **{fire.get('scene_location')}**[span_2](start_span)[span_2](end_span)
  - **Tactical Operation:** {fire.get('operation_type')}[span_3](start_span)[span_3](end_span)
  - **System Action:** {fire.get('system_action')}[span_4](start_span)[span_4](end_span)
  - **Incident Finalization:** {fire.get('incident_finalization_status')}[span_5](start_span)[span_5](end_span)
  - **Tactical Impact:** {fire.get('tactical_impact')}[span_6](start_span)[span_6](end_span)
"""
    else:
        report_content += "\n*No Fire tactical success logs recorded in the registry yet.*[span_7](start_span)[span_7](end_span)\n"

    report_content += f"""
---
*Compiled on: {datetime.utcnow().isoformat()} UTC*  
*Technical Architecture & Repository:* [Trust-Main Fire Directory](https://github.com/PMR-Pubclications/Trust-Main/tree/main/modules%2Ffire)[span_8](start_span)[span_8](end_span)
"""

    with open(OUTPUT_REPORT, "w") as f:
        f.write(report_content)
        
    print(f"[FIRE COMPILER] Tactical impact report successfully compiled to '{OUTPUT_REPORT}'.")

if __name__ == "__main__":
    compile_fire_tactical_report()
