"""
Module: Integrated Forensic & Research Engine Pipeline
Location: modules/Annon/scripts/models/ & modules/Annon/scripts/research_engine/
Description: Combines the Standalone Forensic Engine with the Research Engine 
             module to ingest spatial parameters, process physics/ballistics, 
             and query research data streams as a unified system.

Linked Modules:
- Research Engine: https://github.com/PMR-Pubclications/Trust-Main/tree/main/modules%2FAnnon%2Fscripts%2Fresearch_engine
- Propaganda Rejection Filter: https://github.com/PMR-Pubclications/Trust-Main/blob/main/modules%2FAnnon%2Fscripts%2Fmodels%2FSelf-LearningForensic%26PropagandaRejectionEngine.py
"""

import numpy as np
import trimesh
from scipy.spatial import KDTree

class ResearchEngineInterface:
    """
    Interfaces with the research engine repository module to query 
    pure physical, mathematical, and spatial datasets.
    """
    def __init__(self, repository_path="modules/Annon/scripts/research_engine"):
        self.repository_path = repository_path
        self.active_datasets = []

    def fetch_physical_constants(self, material_name: str) -> dict:
        """Simulates fetching deterministic material constants from the research engine repository."""
        constants = {
            "steel": {"density": 7850.0, "yield_strength_mpa": 250.0},
            "aluminum": {"density": 2700.0, "yield_strength_mpa": 95.0},
            "titanium": {"density": 4506.0, "yield_strength_mpa": 880.0}
        }
        return constants.get(material_name.lower(), {"density": 7850.0, "yield_strength_mpa": 250.0})

class StandaloneForensicEngine:
    """
    Executes objective spatial, ballistics, and thermal computations 
    on 3D mesh geometries using parameters supplied by the research engine.
    """
    def __init__(self):
        self.research_bridge = ResearchEngineInterface()

    def generate_surface_target(self, material="steel", radius=2.0, height=0.5):
        """Generates a structural barrier using material properties fetched from the research engine."""
        material_props = self.research_bridge.fetch_physical_constants(material)
        mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
        mesh.metadata['density'] = material_props["density"]
        mesh.metadata['yield_strength'] = material_props["yield_strength_mpa"]
        return mesh

    def simulate_ballistic_impact(self, mesh, origin_vector, velocity_vector, mass_proj=0.01):
        """
        Calculates projectile intersection, kinetic energy transfer, 
        and penetration depth based on research-backed material density.
        """
        ray_origins = np.array([origin_vector])
        ray_directions = np.array([velocity_vector / np.linalg.norm(velocity_vector)])
        
        intersections, _, tri_indices = mesh.ray.intersects_location(
            ray_origins=ray_origins,
            ray_directions=ray_directions
        )
        
        if len(intersections) == 0:
            return {"impact": False, "message": "Trajectory missed target geometry."}
        
        impact_point = intersections[0]
        normal = mesh.face_normals[tri_indices[0]]
        
        v_mag = np.linalg.norm(velocity_vector)
        kinetic_energy = 0.5 * mass_proj * (v_mag ** 2)
        density = mesh.metadata.get('density', 7850.0)
        penetration_depth = kinetic_energy / (density * 0.1 + 1e-5)
        
        return {
            "impact": True,
            "impact_point": impact_point.tolist(),
            "surface_normal": normal.tolist(),
            "kinetic_energy_joules": kinetic_energy,
            "estimated_penetration_mm": penetration_depth * 1000.0
        }

    def simulate_thermal_dissipation(self, mesh, heat_source_pos, initial_temp=1200.0, time_steps=5):
        """Models transient heat conduction across 3D mesh vertices."""
        vertices = mesh.vertices
        tree = KDTree(vertices)
        
        _, heat_indices = tree.query(heat_source_pos, k=max(1, int(len(vertices)*0.05)))
        temperatures = np.ones(len(vertices)) * 20.0
        temperatures[heat_indices] = initial_temp
        
        adjacency = mesh.vertex_adjacency_graph
        for _ in range(time_steps):
            new_temps = temperatures.copy()
            for v_idx in range(len(vertices)):
                neighbors = list(adjacency.neighbors(v_idx))
                if neighbors:
                    avg_neighbor_temp = np.mean(temperatures[neighbors])
                    new_temps[v_idx] = temperatures[v_idx] + 0.3 * (avg_neighbor_temp - temperatures[v_idx])
            temperatures = new_temps
            
        return {
            "max_recorded_temp": float(np.max(temperatures)),
            "min_recorded_temp": float(np.min(temperatures)),
            "heat_affected_nodes": int(np.sum(temperatures > 100.0))
        }

# --- Unified Pipeline Execution ---
if __name__ == "__main__":
    engine = StandaloneForensicEngine()
    
    print("--- Initializing Unified Research & Forensic Pipeline ---")
    
    # Generate target using titanium specifications fetched via the Research Engine link
    target_barrier = engine.generate_surface_target(material="titanium", radius=1.5, height=0.2)
    print(f"Target Material Density Loaded: {target_barrier.metadata['density']} kg/m^3")

    # Run Ballistic Test on Unified Model
    ballistic_res = engine.simulate_ballistic_impact(
        mesh=target_barrier,
        origin_vector=np.array([0.0, 0.0, -5.0]),
        velocity_vector=np.array([0.0, 0.0, 850.0])
    )
    print("\n[Unified Ballistic Result]:", ballistic_res)

    # Run Thermal Test on Unified Model
    thermal_res = engine.simulate_thermal_dissipation(
        mesh=target_barrier,
        heat_source_pos=np.array([0.0, 0.0, 0.1])
    )
    print("\n[Unified Thermal Result]:", thermal_res)
