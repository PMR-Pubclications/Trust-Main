import numpy as np
import trimesh
import re
import json
import os
from datetime import datetime

class SelfLearningFactualFilter:
    """
    Filters subjective bias/propaganda, extracts factual nouns, 
    and maintains a persistent dynamic database of rejected patterns.
    """
    def __init__(self, db_filepath="rejection_database.json"):
        self.db_filepath = db_filepath
        self.forbidden_hyperbole = {
            "brutal", "massive", "deadly", "shocking", "unprecedented", 
            "catastrophic", "horrific", "devastating", "extreme", "incredible", 
            "monstrous", "vicious", "historic", "miraculous", "terrifying", "epic"
        }
        self.factual_vocabulary = {
            "velocity", "mass", "volume", "density", "energy", "joules", 
            "meters", "millimeters", "temperature", "acceleration", "force",
            "normal", "centroid", "coordinate", "vector", "mesh", "tensor",
            "penetration", "impact", "surface", "gradient"
        }
        self.rejection_db = self._load_rejection_database()

    def _load_rejection_database(self) -> list:
        """Loads previously logged propaganda/biased entries from disk."""
        if os.path.exists(self.db_filepath):
            try:
                with open(self.db_filepath, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_rejection_database(self):
        """Persists updated rejection records to disk."""
        with open(self.db_filepath, 'w') as f:
            json.dump(self.rejection_db, f, indent=4)

    def log_rejection(self, raw_text: str, detected_triggers: list):
        """Logs newly identified propaganda or biased entries into the database."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "raw_text": raw_text,
            "triggers": detected_triggers,
            "status": "BLACKLISTED"
        }
        # Prevent exact duplicate logging
        if not any(item['raw_text'] == raw_text for item in self.rejection_db):
            self.rejection_db.append(entry)
            self._save_rejection_database()

    def is_blacklisted(self, raw_text: str) -> bool:
        """Checks if input matches any previously logged propaganda text."""
        return any(item['raw_text'].lower() == raw_text.lower() for item in self.rejection_db)

    def sanitize_input_text(self, text: str) -> dict:
        """
        Scans input against history and linguistic rules, logging violations.
        """
        # Check dynamic blacklist database first
        if self.is_blacklisted(text):
            return {
                "status": "REJECTED",
                "reason": "Input matches existing entry in the persistent propaganda rejection database."
            }

        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        numbers = re.findall(r'\d+\.?\d*', text)
        
        # Check for prohibited hyper-descriptive adjectives
        detected_bias = [w for w in words if w in self.forbidden_hyperbole]
        if len(detected_bias) > 0:
            # Automatically record into the rejection database
            self.log_rejection(text, detected_bias)
            return {
                "status": "REJECTED",
                "reason": f"Bias/Propaganda detected. Logged to database. Unapproved modifiers: {detected_bias}",
                "filtered_nouns": [],
                "numeric_data": []
            }
        
        factual_nouns = [w for w in words if w in self.factual_vocabulary]
        return {
            "status": "ACCEPTED",
            "reason": "Input cleared. Passed factual purity and database verification.",
            "filtered_nouns": list(set(factual_nouns)),
            "numeric_data": numbers
        }

class ForensicPhysicsEngine:
    """
    3D Forensic Engine integrated with dynamic propaganda rejection logging.
    """
    def __init__(self):
        self.filter = SelfLearningFactualFilter()

    def generate_surface_target(self, radius=2.0, height=0.5, density=7850.0):
        mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
        mesh.metadata['density'] = density
        return mesh

    def process_audited_event(self, description_text, computation_callback, *args, **kwargs):
        audit_result = self.filter.sanitize_input_text(description_text)
        
        if audit_result["status"] == "REJECTED":
            return {
                "audit_status": "REJECTED",
                "filter_feedback": audit_result["reason"]
            }
        
        computation_output = computation_callback(*args, **kwargs)
        return {
            "audit_status": "ACCEPTED",
            "extracted_factual_nouns": audit_result["filtered_nouns"],
            "computation_results": computation_output
        }

    def simulate_ballistic_impact(self, mesh, origin_vector, velocity_vector, mass_proj=0.01):
        ray_origins = np.array([origin_vector])
        ray_directions = np.array([velocity_vector / np.linalg.norm(velocity_vector)])
        
        intersections, _, tri_indices = mesh.ray.intersects_location(
            ray_origins=ray_origins, ray_directions=ray_directions
        )
        
        if len(intersections) == 0:
            return {"impact": False}
        
        v_mag = np.linalg.norm(velocity_vector)
        kinetic_energy = 0.5 * mass_proj * (v_mag ** 2)
        density = mesh.metadata.get('density', 1000.0)
        penetration_depth = kinetic_energy / (density * 0.1 + 1e-5)
        
        return {
            "impact": True,
            "impact_point": intersections[0].tolist(),
            "kinetic_energy_joules": kinetic_energy,
            "estimated_penetration_mm": penetration_depth * 1000.0
        }

# --- Execution Demonstration ---
if __name__ == "__main__":
    engine = ForensicPhysicsEngine()
    target_barrier = engine.generate_surface_target()

    print("--- Testing Self-Learning Propaganda Rejection Database ---")

    # Test 1: First-time exposure to biased text (Will be rejected and logged to `rejection_database.json`)
    propaganda_input = "A catastrophic and unprecedented massive impact occurred!"
    res1 = engine.process_audited_event(propaganda_input, engine.simulate_ballistic_impact, target_barrier, [0,0,-5], [0,0,850])
    print(f"\n[Test 1 - Initial Exposure]:\n{res1}")

    # Test 2: Re-submitting the exact same propaganda text (Caught instantly by the database lookup)
    res2 = engine.process_audited_event(propaganda_input, engine.simulate_ballistic_impact, target_barrier, [0,0,-5], [0,0,850])
    print(f"\n[Test 2 - Subsequent Exposure (Database Match)]:\n{res2}")

    # Test 3: Factual input (Clears successfully)
    clean_input = "Velocity vector 850 meters per second mass 0.0095 kilograms impact coordinate surface normal."
    res3 = engine.process_audited_event(clean_input, engine.simulate_ballistic_impact, target_barrier, [0,0,-5], [0,0,850], mass_proj=0.0095)
    print(f"\n[Test 3 - Clean Factual Input]:\n{res3}")
