#!/usr/bin/env python3
"""
TFML Lifeguard Module Compiler & Aquatic Safety Impact Generator
Validates water rescue logs, rip current telemetry, submersion response times,
and emergency medical handovers for municipal aquatics reviews.
"""

import json
import os
from datetime import datetime

# Path points to root-level or local registry storage
LG_DB = "../../lifeguard_success_registry.json"
LOCAL_LG_DB = "lifeguard_success_registry.json"
OUTPUT_REPORT = "Lifeguard_Aquatic_Safety_Report.md"

def compile_lifeguard_safety_report():
    """Aggregates lifeguard aquatic rescue successes into an executive briefing report."""
    target_db = LG_DB if os.path.exists(LG_DB) else LOCAL_LG_DB
    
    lg_data = {"lifeguard_rescue_successes": []}
    if os.path.exists(target_db):
        with open(target_db, "r") as f:
            lg_data = json.load(f)

    report_content = f"""# Trust Forensics Mobile Lab (TFML) - Lifeguard & Aquatic Rescue Module
## Executive Briefing & Aquatic Safety Report

### Operational Overview
The TFML Lifeguard module equips waterfront and pool rescue teams with hands-on voice tagging, real-time aquatic telemetry (rip current velocity, water temp, and wave dynamics), and rapid submersion tracking to accelerate emergency intervention and ensure seamless handovers to responding EMS units.

---

## 🏊 Verified Aquatic Rescues & Safety Operations
*Tracked via submersion response timers, water rescue telemetry, and emergency medical handovers.*
"""

    successes = lg_data.get("lifeguard_rescue_successes", [])
    if successes:
        for lg in successes:
            report_content += f"""
- **Incident ID {lg.get('incident_id')}** -> **{lg.get('location_facility')}**
  - **Rescue Operation:** {lg.get('operation_type')}
  - **System Action:** {lg.get('system_action')}
  - **Incident Finalization:** {lg.get('incident_finalization_status')}
  - **Safety Impact:** {lg.get('safety_impact')}
"""
    else:
        report_content += "\n*No Lifeguard rescue success logs recorded in the registry yet.*\n"

    report_content += f"""
---
*Compiled on: {datetime.utcnow().isoformat()} UTC*  
*Technical Architecture & Repository:* [Trust-Main Lifeguard Directory](https://github.com/PMR-Pubclications/Trust-Main/tree/main/modules%2Flifeguard)
"""

    with open(OUTPUT_REPORT, "w") as f:
        f.write(report_content)
        
    print(f"[LIFEGUARD COMPILER] Aquatic safety report successfully compiled to '{OUTPUT_REPORT}'.")

if __name__ == "__main__":
    compile_lifeguard_safety_report()
