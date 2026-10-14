import numpy as np
import trimesh
from scipy.spatial import KDTree
import re

class FactualNounFilter:
    """
    Algorithmic filter designed to reject biased narrative framing and hyperbole 
    by stripping subjective adjectives and isolating strictly factual nouns and measurements.
    """
    def __init__(self):
        # Hyper-descriptive / emotional adjectives indicative of subjective bias or propaganda
        self.forbidden_hyperbole = {
            "brutal", "massive", "deadly", "shocking", "unprecedented", 
            "catastrophic", "horrific", "devastating", "extreme", "incredible", 
            "monstrous", "vicious", "historic", "miraculous", "terrifying", "epic"
        }
        # Verified objective technical and physical categories
        self.factual_vocabulary = {
            "velocity", "mass", "volume", "density", "energy", "joules", 
            "meters", "millimeters", "temperature", "acceleration", "force",
            "normal", "centroid", "coordinate", "vector", "mesh", "tensor",
            "penetration", "impact", "coordinate", "surface", "gradient"
        }

    def sanitize_input_text(self, text: str) -> dict:
        """
        Scans input descriptions, blocks hyperbole, and extracts pure factual nouns.
        """
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        numbers = re.findall(r'\d+\.?\d*', text)
        
        # Check for prohibited hyper-descriptive adjectives
        detected_bias = [w for w in words if w in self.forbidden_hyperbole]
        if len(detected_bias) > 0:
            return {
                "status": "REJECTED",
                "reason": f"Bias/Hyperbole detected. Unapproved modifiers: {detected_bias}",
                "filtered_nouns": [],
                "numeric_data": []
            }
        
        # Isolate strictly factual nouns and technical terms
        factual_nouns = [w for w in words if w in self.factual_vocabulary]
        
        return {
            "status": "ACCEPTED",
            "reason": "Input cleared. Passed factual purity and objective metric validation.",
            "filtered_nouns": list(set(factual_nouns)),
            "numeric_data": numbers
        }

class ForensicPhysicsEngine:
    """
    Advanced 3D Spatial & Forensic Analysis Engine integrated with a 
    pure factual data extraction and propaganda-rejection filter.
    """
    def __init__(self):
        self.filter = FactualNounFilter()

    def generate_surface_target(self, radius=2.0, height=0.5, density=7850.0):
        mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
        mesh.metadata['density'] = density
        return mesh

    def process_audited_event(self, description_text, computation_callback, *args, **kwargs):
        """
        Audits incoming text/metadata through the factual filter before executing 
        the core physics/forensic calculation.
        """
        audit_result = self.filter.sanitize_input_text(description_text)
        
        if audit_result["status"] == "REJECTED":
            return {
                "audit_status": "REJECTED",
                "filter_feedback": audit_result["reason"]
            }
        
        # Execute underlying mathematical/physics function if audit passes
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

    print("--- Testing Factual Filter & Forensic Engine ---")

    # Test 1: Input containing propaganda/hyper-descriptive adjectives (Should be rejected)
    biased_input = "A catastrophic and brutal massive high-velocity projectile impact destroyed the surface!"
    result_biased = engine.process_audited_event(
        biased_input, 
        engine.simulate_ballistic_impact, 
        mesh=target_barrier, 
        origin_vector=[0, 0, -5], 
        velocity_vector=[0, 0, 850]
    )
    print(f"\n[Test 1 - Biased Input]\nResult: {result_biased}")

    # Test 2: Clean, factual, metric-driven input (Should be accepted and processed)
    clean_input = "Velocity vector 850 meters per second mass 0.0095 kilograms impact coordinate surface normal."
    result_clean = engine.process_audited_event(
        clean_input, 
        engine.simulate_ballistic_impact, 
        mesh=target_barrier, 
        origin_vector=[0, 0, -5], 
        velocity_vector=[0, 0, 850],
        mass_proj=0.0095
    )
    print(f"\n[Test 2 - Clean Factual Input]\nResult: {result_clean}")
