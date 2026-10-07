# scripts/integration/agency_bridge.py
import requests
import json
import logging

class AgencyBridge:
    def __init__(self, config_path="config/config.yaml"):
        # Load agency configurations and local routing endpoints[span_1](start_span)[span_1](end_span)
        self.endpoints = {
            "POLICE": "http://localhost:5001/api/police/receive",
            "FIRE": "http://localhost:5002/api/fire/receive",
            "EMS": "http://localhost:5003/api/ems/receive",
            "DOT": "http://localhost:5004/api/dot/receive",
            "HOSPITAL": "http://localhost:5005/api/health_records/receive"
        }

    def push_report(self, target_agency: str, report_payload: dict) -> bool:
        """Pushes structured forensic or medical reports directly to agency modules[span_2](start_span)[span_2](end_span)."""
        agency = target_agency.upper()
        if agency not in self.endpoints:
            logging.error(f"Unknown target agency: {agency}")
            return False
            
        try:
            response = requests.post(
                self.endpoints[agency], 
                json=report_payload, 
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Failed to push report to {agency}: {e}")
            return False

    def pull_data(self, target_agency: str, query_params: dict) -> dict:
        """Pulls victim, patient, or forensic data from agency databases, including hospitals."""
        agency = target_agency.upper()
        if agency not in self.endpoints:
            return {"error": "Unknown agency"}
            
        try:
            # Re-routes the receive endpoint to a query endpoint for data extraction
            query_url = self.endpoints[agency].replace("/receive", "/query")
            response = requests.get(query_url, params=query_params, timeout=5)
            if response.status_code == 200:
                return response.json()
            return {"error": "Data not found or access denied"}
        except Exception as e:
            return {"error": str(e)}

    def broadcast_hazmat_or_alert(self, alert_data: dict):
        """Broadcasts critical real-time alerts across all responder interfaces[span_3](start_span)[span_3](end_span)."""
        for agency, endpoint in self.endpoints.items():
            try:
                alert_url = endpoint.replace("/receive", "/alert")
                requests.post(alert_url, json=alert_data, timeout=2)
            except Exception:
                continue
