import math
from typing import Dict, Any

class ForensicPhysicsEngine:
    
    @staticmethod
    def calculate_ballistic_trajectory(
        velocity_fps: float,
        angle_degrees: float,
        bullet_mass_grains: float,
        drag_coefficient: float,
        cross_sectional_area_sq_in: float,
        time_step: float = 0.001
    ) -> Dict[str, Any]:
        """
        2D Numerical Integration for projectile trajectory accounting for gravity and air drag.
        """
        # Conversions
        g = 32.174  # ft/s^2
        mass_lbs = bullet_mass_grains / 7000.0
        area_sq_ft = cross_sectional_area_sq_in / 144.0
        air_density = 0.0765  # lb/ft^3 (standard sea level)
        
        vx = velocity_fps * math.cos(math.radians(angle_degrees))
        vy = velocity_fps * math.sin(math.radians(angle_degrees))
        
        x, y, t = 0.0, 0.0, 0.0
        max_height = 0.0
        
        while y >= 0.0:
            v = math.sqrt(vx**2 + vy**2)
            # Drag force: Fd = 0.5 * rho * v^2 * Cd * A
            f_drag = 0.5 * air_density * (v**2) * drag_coefficient * area_sq_ft
            
            # Acceleration
            ax = -(f_drag * (vx / v)) / mass_lbs if v > 0 else 0
            ay = -g - ((f_drag * (vy / v)) / mass_lbs) if v > 0 else -g
            
            # Euler integration
            x += vx * time_step
            y += vy * time_step
            vx += ax * time_step
            vy += ay * time_step
            t += time_step
            
            if y > max_height:
                max_height = y
                
            if t > 60:  # Timeout safety
                break
                
        return {
            "total_distance_feet": round(x, 2),
            "max_elevation_feet": round(max_height, 2),
            "flight_time_seconds": round(t, 3),
            "impact_velocity_fps": round(math.sqrt(vx**2 + vy**2), 2)
        }

    @staticmethod
    def calculate_compartment_flashover(
        room_length_m: float,
        room_width_m: float,
        vent_width_m: float,
        vent_height_m: float
    ) -> Dict[str, Any]:
        """
        Calculates minimum Heat Release Rate (HRR in kW) required for room flashover
        using Thomas' Flashover Correlation.
        """
        floor_area = room_length_m * room_width_m
        vent_area = vent_width_m * vent_height_m
        
        # Thomas correlation: Q_fo = 780 * A_v * sqrt(H_v) + 378 * A_t
        hrr_flashover_kw = (780 * vent_area * math.sqrt(vent_height_m)) + (378 * floor_area)
        
        return {
            "critical_hrr_kw": round(hrr_flashover_kw, 2),
            "critical_hrr_mw": round(hrr_flashover_kw / 1000.0, 2),
            "minimum_temp_celsius": 500  # Standard flashover threshold
        }

    @staticmethod
    def calculate_column_buckling(
        elastic_modulus_psi: float,
        moment_of_inertia_in4: float,
        length_inches: float,
        effective_length_factor_k: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculates Euler Critical Buckling Load: P_cr = (pi^2 * E * I) / (K * L)^2
        """
        kl = effective_length_factor_k * length_inches
        p_cr = (math.pi**2 * elastic_modulus_psi * moment_of_inertia_in4) / (kl**2)
        
        return {
            "critical_buckling_load_lbs": round(p_cr, 2),
            "critical_buckling_load_kips": round(p_cr / 1000.0, 2)
        }
