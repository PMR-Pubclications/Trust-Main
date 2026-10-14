"""
Module: Forensic Engine
Location: modules/Annon/scripts/models/
Description: Core deterministic physics, ballistics, spatter vector analysis, 
             and thermal dissipation engine. Operates independently of text 
             filtering modules.
             
External Dependency Link (Propaganda Rejection Filter):
https://github.com/PMR-Pubclications/Trust-Main/blob/main/modules%2FAnnon%2Fscripts%2Fmodels%2FSelf-LearningForensic%26PropagandaRejectionEngine.py
"""

import numpy as np
import trimesh
from scipy.spatial import KDTree

class StandaloneForensicEngine:
    """
    Executes objective spatial, ballistics, and thermal computations 
    on 3D mesh geometries.
    """
    def __init__(self):
        pass

    def generate_surface_target(self, radius=2.0, height=0.5, density=7850.0):
        """Generates a structural barrier or target mesh for physical testing."""
        mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
        mesh.metadata['density'] = density
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
            "max_recorded_temp": float(np.max(temperatures)),
            "min_recorded_temp": float(np.min(temperatures)),
            "heat_affected_nodes": int(np.sum(temperatures > 100.0))
        }

# --- Execution Demonstration ---
if __name__ == "__main__":
    engine = StandaloneForensicEngine()
    target_barrier = engine.generate_surface_target(radius=1.5, height=0.2, density=7850.0)

    print("--- Running Standalone Forensic Engine ---")
    
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
