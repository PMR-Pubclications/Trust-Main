import numpy as np
import cv2
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

@dataclass
class BleedingAlert:
    zone_name: str
    anomaly_type: str  # 'ASYMMETRY', 'THERMAL_PLUME', or 'RAPID_COOLING'
    delta_temp_celsius: float
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # (x, y, w, h)

class ThermalBleedingDetector:
    def __init__(self, asymmetry_threshold_c: float = 1.5, gradient_threshold: float = 0.8):
        self.asymmetry_threshold = asymmetry_threshold_c
        self.gradient_threshold = gradient_threshold
        self.frame_history: List[Tuple[float, np.ndarray]] = []  # (timestamp, thermal_matrix)
        self.history_window_sec = 30.0

    def analyze_frame(self, thermal_matrix: np.ndarray, current_time: float) -> List[BleedingAlert]:
        """
        Processes a radiometric thermal frame (2D float array where each pixel is Temp in Celsius).
        Returns a list of detected thermal anomalies indicating internal bleeding or ischemia.
        """
        alerts = []
        
        # Maintain rolling time window
        self.frame_history.append((current_time, thermal_matrix))
        self.frame_history = [
            (t, mat) for t, mat in self.frame_history 
            if current_time - t <= self.history_window_sec
        ]

        # 1. Spatial Thermal Gradient Analysis (\nabla T)
        grad_x = cv2.Sobel(thermal_matrix, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(thermal_matrix, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Isolate anomalous thermal boundary contours
        _, high_grad_mask = cv2.threshold(magnitude, self.gradient_threshold, 255, cv2.THRESH_BINARY)
        high_grad_mask = high_grad_mask.astype(np.uint8)
        
        contours, _ = cv2.findContours(high_grad_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 100:  # Ignore pixel noise
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            roi = thermal_matrix[y:y+h, x:x+w]
            roi_mean = float(np.mean(roi))
            surrounding_mean = float(np.mean(thermal_matrix))
            delta = abs(roi_mean - surrounding_mean)
            
            if delta >= self.asymmetry_threshold:
                alerts.append(BleedingAlert(
                    zone_name=f"ROI_{x}_{y}",
                    anomaly_type="THERMAL_PLUME",
                    delta_temp_celsius=round(delta, 2),
                    confidence=min(1.0, delta / 3.0),
                    bounding_box=(x, y, w, h)
                ))

        # 2. Temporal Cooling Rate Analysis (dT/dt)
        if len(self.frame_history) > 5:
            oldest_time, oldest_matrix = self.frame_history[0]
            dt = current_time - oldest_time
            if dt > 5.0:  # Minimum 5-second baseline
                temp_diff = thermal_matrix - oldest_matrix
                cooling_rate = temp_diff / dt  # °C per second
                
                # Rapid localized cooling (< -0.05 °C/sec indicates severe loss of vascular perfusion)
                rapid_cooling_mask = (cooling_rate < -0.05).astype(np.uint8) * 255
                cool_contours, _ = cv2.findContours(rapid_cooling_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for c in cool_contours:
                    if cv2.contourArea(c) > 150:
                        x, y, w, h = cv2.boundingRect(c)
                        max_rate = abs(float(np.min(cooling_rate[y:y+h, x:x+w])))
                        alerts.append(BleedingAlert(
                            zone_name=f"Perfusion_Loss_{x}_{y}",
                            anomaly_type="RAPID_COOLING",
                            delta_temp_celsius=round(max_rate * dt, 2),
                            confidence=min(1.0, max_rate / 0.1),
                            bounding_box=(x, y, w, h)
                        ))

        return alerts

    def evaluate_bilateral_asymmetry(self, left_roi: np.ndarray, right_roi: np.ndarray) -> Optional[BleedingAlert]:
        """
        Directly compares symmetric anatomical zones (e.g., Left vs. Right Abdominal Flank).
        """
        mean_left = np.mean(left_roi)
        mean_right = np.mean(right_roi)
        delta = abs(mean_left - mean_right)

        if delta >= self.asymmetry_threshold:
            cooler_side = "LEFT" if mean_left < mean_right else "RIGHT"
            return BleedingAlert(
                zone_name=f"Bilateral_Flank_{cooler_side}_DEFICIT",
                anomaly_type="ASYMMETRY",
                delta_temp_celsius=round(float(delta), 2),
                confidence=min(1.0, delta / 2.5),
                bounding_box=(0, 0, 0, 0)
            )
        return None
