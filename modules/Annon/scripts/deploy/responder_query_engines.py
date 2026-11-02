import os
import sqlite3
from datetime import datetime

class BaseResponderDatabase:
    """Base class handling individual SQLite database connections per first responder module."""
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_local_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_local_db(self):
        """Creates the local isolated database if it does not exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        # Implementation-specific table creation is handled by subclasses


class LEODatabaseEngine(BaseResponderDatabase):
    """Isolated database engine for Law Enforcement & Forensics (Warrants, LPR, Ballistics)."""
    def __init__(self):
        super().__init__("modules/Annon/data/databases/leo_forensics.db")

    def _initialize_local_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS warrants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_name TEXT,
                    warrant_id TEXT,
                    offense TEXT,
                    status TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vehicle_registry (
                    plate TEXT PRIMARY KEY,
                    make_model TEXT,
                    owner TEXT,
                    stolen_status TEXT
                )
            """)
            conn.commit()

    def query_warrant(self, subject_name: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT warrant_id, offense, status FROM warrants WHERE subject_name LIKE ?", (f"%{subject_name}%",))
            return cursor.fetchall()


class FireDatabaseEngine(BaseResponderDatabase):
    """Isolated database engine for Fire Department (Hazardous Materials, Hydrant Maps, Incident Logs)."""
    def __init__(self):
        super().__init__("modules/Annon/data/databases/fire_department.db")

    def _initialize_local_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS hazmat_sites (
                    site_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    address TEXT,
                    material_type TEXT,
                    max_capacity TEXT
                )
            """)
            conn.commit()

    def query_hazmat(self, address: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT material_type, max_capacity FROM hazmat_sites WHERE address LIKE ?", (f"%{address}%",))
            return cursor.fetchall()


class EMSDatabaseEngine(BaseResponderDatabase):
    """Isolated database engine for Emergency Medical Services (Triage Records, Hospital Bed Availability)."""
    def __init__(self):
        super().__init__("modules/Annon/data/databases/ems_medical.db")

    def _initialize_local_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS hospital_capacity (
                    hospital_name TEXT PRIMARY KEY,
                    available_trauma_beds INTEGER,
                    icu_status TEXT
                )
            """)
            conn.commit()

    def get_hospital_status(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hospital_name, available_trauma_beds, icu_status FROM hospital_capacity")
            return cursor.fetchall()


class RescueDatabaseEngine(BaseResponderDatabase):
    """Isolated database engine for Specialized Rescue / County Lifeguards (Water Rescue Logs, Tide Data)."""
    def __init__(self):
        super().__init__("modules/Annon/data/databases/specialized_rescue.db")

    def _initialize_local_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS marine_incidents (
                    incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location TEXT,
                    vessel_type TEXT,
                    status TEXT
                )
            """)
            conn.commit()

    def query_incidents(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT location, vessel_type, status FROM marine_incidents")
            return cursor.fetchall()

# Example testing execution
if __name__ == "__main__":
    leo_db = LEODatabaseEngine()
    fire_db = FireDatabaseEngine()
    ems_db = EMSDatabaseEngine()
    rescue_db = RescueDatabaseEngine()
    
    print("All individual first responder database engines initialized successfully in Python.")
