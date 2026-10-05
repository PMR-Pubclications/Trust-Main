#!/usr/bin/env python3
import json
import time
from datetime import datetime, timezone

class ShiftPayrollExporter:
    def __init__(self, badge_id: str, agency_id: str, module_name: str):
        self.badge_id = badge_id
        self.agency_id = agency_id
        self.module_name = module_name.upper()
        self.clock_in_time = None
        self.clock_out_time = None
        self.breaks = []

    def clock_in(self):
        self.clock_in_time = datetime.now(timezone.utc)

    def start_break(self, break_type: str = "MEAL"):
        self.breaks.append({
            "break_type": break_type,
            "start": datetime.now(timezone.utc).isoformat(),
            "end": None,
            "duration_minutes": 0
        })

    def end_break(self):
        if self.breaks and self.breaks[-1]["end"] is None:
            end_dt = datetime.now(timezone.utc)
            start_dt = datetime.fromisoformat(self.breaks[-1]["start"])
            dur = (end_dt - start_dt).total_seconds() / 60.0
            
            self.breaks[-1]["end"] = end_dt.isoformat()
            self.breaks[-1]["duration_minutes"] = round(dur, 2)

    def clock_out(self, module_reports: dict) -> dict:
        self.clock_out_time = datetime.now(timezone.utc)
        
        total_seconds = (self.clock_out_time - self.clock_in_time).total_seconds() if self.clock_in_time else 0
        total_break_minutes = sum(b.get("duration_minutes", 0) for b in self.breaks)
        net_payable_hours = max(0.0, (total_seconds / 3600.0) - (total_break_minutes / 60.0))

        shift_id = f"SHF_{self.clock_in_time.strftime('%Y%m%d')}_{self.badge_id}"

        payload = {
            "module": self.module_name,
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "timecard": {
                "shift_id": shift_id,
                "badge_id": self.badge_id,
                "agency_id": self.agency_id,
                "clock_in": self.clock_in_time.isoformat() if self.clock_in_time else None,
                "clock_out": self.clock_out_time.isoformat(),
                "total_shift_seconds": int(total_seconds),
                "breaks": self.breaks,
                "net_payable_hours": round(net_payable_hours, 2)
            },
            "shift_activity_reports": module_reports
        }
        
        return payload

# Quick usage demonstration
if __name__ == "__main__":
    exporter = ShiftPayrollExporter(badge_id="BDG-102", agency_id="VANCOUVER_PD", module_name="POLICE")
    exporter.clock_in()
    time.sleep(1) # Simulate shift
    
    # Generate payroll package with attached shift activity
    shift_summary = exporter.clock_out(module_reports={
        "evidence_items_logged": 2,
        "cases_touched": ["CASE-2026-881"]
    })
    
    print(json.dumps(shift_summary, indent=2))
