import os
import json
from datetime import datetime

class LawEnforcementQueryEngine:
    """
    Simulated Law Enforcement Query Module for Annon.
    Handles License Plate Queries (ALPR/Vehicle Lookup) and Warrant Checks.
    Designed for integration into CAD/RMS or LEO / Forensics sub-modules.
    """
    def __init__(self, cjis_authorized: bool = True):
        self.cjis_authorized = cjis_authorized
        
        # Mock database representing registered agency records / NCIC bridge
        self._mock_vehicle_db = {
            "7ABC123": {
                "make": "Ford",
                "model": "Explorer",
                "year": 2021,
                "color": "Black",
                "status": "CLEAR",
                "registered_owner": "John Doe",
                "warrants_active": False
            },
            "9XYZ890": {
                "make": "Dodge",
                "model": "Charger",
                "year": 2019,
                "color": "White",
                "status": "STOLEN VEHICLE",
                "registered_owner": "Jane Smith",
                "warrants_active": True,
                "warrant_details": {
                    "warrant_id": "WARR-2026-0941",
                    "offense": "Grand Theft Auto / Felony Warrant",
                    "issuing_agency": "Clark County Sheriff's Office",
                    "extradition": "Statewide"
                }
            }
        }

    def run_license_plate(self, plate_number: str) -> dict:
        """
        Runs a license plate lookup against the vehicle repository.
        """
        clean_plate = plate_number.strip().upper()
        timestamp = datetime.now().isoformat()
        
        print(f"Executing LPR Query for Plate: [{clean_plate}] at {timestamp}")
        
        if clean_plate in self._mock_vehicle_db:
            record = self._mock_vehicle_db[clean_plate]
            response = {
                "query_type": "LICENSE_PLATE_LOOKUP",
                "plate": clean_plate,
                "timestamp": timestamp,
                "status": "MATCH_FOUND",
                "vehicle_info": record,
                "alert": record["status"] != "CLEAR" or record["warrants_active"]
            }
        else:
            response = {
                "query_type": "LICENSE_PLATE_LOOKUP",
                "plate": clean_plate,
                "timestamp": timestamp,
                "status": "NO_RECORD_FOUND",
                "alert": False
            }
            
        return response

    def check_warrants(self, person_name: str) -> dict:
        """
        Queries active warrant status for a subject name.
        """
        timestamp = datetime.now().isoformat()
        print(f"Executing Active Warrant Query for Subject: [{person_name}] at {timestamp}")
        
        # Cross-reference mock database for active warrants
        warrants_found = []
        for plate, data in self._mock_vehicle_db.items():
            if data.get("registered_owner", "").lower() == person_name.lower():
                if data.get("warrants_active"):
                    warrants_found.append(data.get("warrant_details"))

        return {
            "query_type": "WARRANT_SEARCH",
            "subject": person_name,
            "timestamp": timestamp,
            "has_active_warrants": len(warrants_found) > 0,
            "warrant_count": len(warrants_found),
            "records": warrants_found
        }

# Example execution within the Annon framework
if __name__ == "__main__":
    query_engine = LawEnforcementQueryEngine(cjis_authorized=True)
    
    # 1. Run a license plate check
    plate_results = query_engine.run_license_plate("9XYZ890")
    print("\n[Plate Query Output]:")
    print(json.dumps(plate_results, indent=2))
    
    # 2. Check for active warrants on a subject
    warrant_results = query_engine.check_warrants("Jane Smith")
    print("\n[Warrant Search Output]:")
    print(json.dumps(warrant_results, indent=2))
