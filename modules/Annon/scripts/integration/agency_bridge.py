# scripts/integration/agency_bridge.py
import requests
import logging

class AgencyBridge:
    def __init__(self):
        # Local routing endpoints for all connected agencies and hospitals
        self.endpoints = {
            "POLICE": "http://localhost:5001/api/police",
            "FIRE": "http://localhost:5002/api/fire",
            "EMS": "http://localhost:5003/api/ems",
            "DOT": "http://localhost:5004/api/dot",
            "HOSPITAL": "http://localhost:5005/api/health_records"
        }

    def push_report(self, target_agency: str, report_payload: dict) -> bool:
        """Pushes structured forensic reports directly to agency modules."""
        agency = target_agency.upper()
        if agency not in self.endpoints:
            logging.error(f"Unknown target agency: {agency}")
            return False
            
        try:
            response = requests.post(f"{self.endpoints[agency]}/receive", json=report_payload, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Failed to push report to {agency}: {e}")
            return False

    def pull_data(self, target_agency: str, query_params: dict) -> dict:
        """Pulls victim, patient, or forensic data from agency and hospital databases."""
        agency = target_agency.upper()
        if agency not in self.endpoints:
            return {"error": "Unknown agency or hospital endpoint"}
            
        try:
            response = requests.get(f"{self.endpoints[agency]}/query", params=query_params, timeout=5)
            if response.status_code == 200:
                return response.json()
            return {"error": "Data not found or access denied"}
        except Exception as e:
            return {"error": str(e)}
