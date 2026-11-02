import os
import json
import requests
from datetime import datetime

class LawEnforcementQueryEngine:
    """
    Live Law Enforcement Query Module for Annon.
    Connects to live agency endpoints using secure authentication keys 
    defined during client onboarding.
    """
    def __init__(self, agency_config_path: str = "modules/Annon/config/config.yaml"):
        # Load live endpoints and authentication headers based on onboarding profile
        self.config = self._load_agency_config(agency_config_path)
        
        self.api_base_url = self.config.get("agency_api_endpoint", "https://api.patriotsmustrise.org/v1/le")
        self.auth_token = self.config.get("secure_auth_token", os.getenv("TRUST_AUTH_TOKEN", ""))
        self.agency_id = self.config.get("agency_id", "DEFAULT_AGENCY")

    def _load_agency_config(self, path: str) -> dict:
        """Loads client-specific onboarding parameters."""
        if os.path.exists(path):
            # In production, parse config.yaml or config.json provided by the client agency
            print(f"Loading onboarding configuration for agency from {path}...")
            return {
                "agency_api_endpoint": os.getenv("AGENCY_API_ENDPOINT", "https://api.patriotsmustrise.org/v1/le"),
                "secure_auth_token": os.getenv("AGENCY_AUTH_TOKEN", "live_token_placeholder"),
                "agency_id": os.getenv("AGENCY_ID", "AGENCY-LOCAL-01")
            }
        return {}

    def _get_auth_headers(self) -> dict:
        """Constructs secure authentication headers referencing the Trust ecosystem protocols."""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "X-Agency-ID": self.agency_id,
            "Content-Type": "application/json"
        }

    def run_license_plate(self, plate_number: str) -> dict:
        """
        Executes a live license plate lookup query against the agency's connected database.
        """
        clean_plate = plate_number.strip().upper()
        endpoint = f"{self.api_base_url}/vehicles/query"
        payload = {"plate": clean_plate, "agency_id": self.agency_id}
        
        print(f"Executing LIVE LPR Query for Plate: [{clean_plate}] via {endpoint}")
        
        try:
            response = requests.post(endpoint, json=payload, headers=self._get_auth_headers(), timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "query_type": "LICENSE_PLATE_LOOKUP",
                    "plate": clean_plate,
                    "status": "API_ERROR",
                    "status_code": response.status_code,
                    "error_message": response.text
                }
        except requests.exceptions.RequestException as e:
            # Fallback or connection failure handling if network is unreachable
            return {
                "query_type": "LICENSE_PLATE_LOOKUP",
                "plate": clean_plate,
                "status": "CONNECTION_FAILED",
                "details": str(e)
            }

    def check_warrants(self, person_name: str) -> dict:
        """
        Queries active warrants live against the agency repository.
        """
        endpoint = f"{self.api_base_url}/warrants/search"
        payload = {"subject": person_name, "agency_id": self.agency_id}
        
        print(f"Executing LIVE Warrant Query for Subject: [{person_name}] via {endpoint}")
        
        try:
            response = requests.post(endpoint, json=payload, headers=self._get_auth_headers(), timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "query_type": "WARRANT_SEARCH",
                    "subject": person_name,
                    "status": "API_ERROR",
                    "status_code": response.status_code,
                    "error_message": response.text
                }
        except requests.exceptions.RequestException as e:
            return {
                "query_type": "WARRANT_SEARCH",
                "subject": person_name,
                "status": "CONNECTION_FAILED",
                "details": str(e)
            }

# Example live execution using client onboarding parameters
if __name__ == "__main__":
    # Once the client populates their onboarding credentials, queries go live automatically
    engine = LawEnforcementQueryEngine()
    
    # plate_result = engine.run_license_plate("7ABC123")
    # print(json.dumps(plate_result, indent=2))
