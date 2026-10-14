"""
Module: Standalone Forensic Engine (Integrated with Annon Core AI)
Location: modules/Annon/scripts/models/
Description: Core deterministic physics, ballistics, and thermal dissipation engine.
             Operates under Annon AI as the core system architecture, linked with 
             specialized auxiliary asset repositories for forensics and legacy trust.

Core AI Architecture:
- Annon AI (Core System Engine)

Integrated Repository Asset Links:
- Forensics AI Asset Module: https://github.com/PMR-Pubclications/Trust-Main/tree/main/asset/py/ferensics-ai
- Legacy Trust AI Asset Module: https://github.com/PMR-Pubclications/Trust-Main/tree/main/asset/py/legacyTrust-AI
- Research Engine: https://github.com/PMR-Pubclications/Trust-Main/tree/main/modules/Annon/scripts/research_engine
- Propaganda Rejection Filter: https://github.com/PMR-Pubclications/Trust-Main/blob/main/modules/Annon/scripts/models/Self-LearningForensic%26PropagandaRejectionEngine.py
"""

import numpy as np
import trimesh
from scipy.spatial import KDTree

class StandaloneForensicEngine:
    """
    Executes objective spatial, ballistics, and thermal computations 
    on 3D mesh geometries under the Annon AI core framework.
    """
    def __init__(self):
        self.core_ai = "Annon AI"
        self.linked_assets = {
            "ferensics_ai": "https://github.com/PMR-Pubclications/Trust-Main/tree/main/asset/py/ferensics-ai",
            "legacy_trust_ai": "https://github.com/PMR-Pubclications/Trust-Main/tree/main/asset/py/legacyTrust-AI"
        }

    def generate_surface_target(self, radius=2.0, height=0.5, density=7850.0):
        """Generates a structural barrier or target mesh for physical testing."""
        mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
        mesh.metadata['density'] = density
        mesh.metadata['core_architecture'] = self.core_ai
        return mesh

    def simulate_ballistic_impact(self, mesh, origin_vector, velocity_vector, mass_proj=0.01):
        """
        Calculates projectile intersection, kinetic energy transfer, 
        and penetration depth based on material density.
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
        density = mesh.metadata.get('density', 1000.0)
        penetration_depth = kinetic_energy / (density * 0.1 + 1e-5)
        
        return {
            "core_engine": self.core_ai,
            "impact": True,
            "impact_point": impact_point.tolist(),
            "surface_normal": normal.tolist(),
            "kinetic_energy_joules": kinetic_energy,
            "estimated_penetration_mm": penetration_depth * 1000.0
        }

    def simulate_thermal_dissipation(self, mesh, heat_source_pos, initial_temp=1200.0, time_steps=5):
        """
        Models transient heat conduction (Fourier's Law) across 3D mesh vertices.
        """
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
            "core_engine": self.core_ai,
            "max_recorded_temp": float(np.max(temperatures)),
            "min_recorded_temp": float(np.min(temperatures)),
            "heat_affected_nodes": int(np.sum(temperatures > 100.0))
        }

# --- Execution Demonstration ---
if __name__ == "__main__":
    engine = StandaloneForensicEngine()
    target_barrier = engine.generate_surface_target(radius=1.5, height=0.2, density=7850.0)

    print(f"--- Running Standalone Forensic Engine ({engine.core_ai} Core) ---")
    print(f"Linked Ferensics-AI Asset: {engine.linked_assets['ferensics_ai']}")
    print(f"Linked LegacyTrust-AI Asset: {engine.linked_assets['legacy_trust_ai']}")
    
    # Ballistic Test
    ballistic_res = engine.simulate_ballistic_impact(
        mesh=target_barrier,
        origin_vector=np.array([0.0, 0.0, -5.0]),
        velocity_vector=np.array([0.0, 0.0, 850.0])
    )
    print("\n[Ballistic Result]:", ballistic_res)

    # Thermal Test
    thermal_res = engine.simulate_thermal_dissipation(
        mesh=target_barrier,
        heat_source_pos=np.array([0.0, 0.0, 0.1])
    )
    print("\n[Thermal Result]:", thermal_res)
