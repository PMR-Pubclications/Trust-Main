import cv2
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from forensic_physics import ForensicPhysicsEngine


class VideoBallisticsAnalyzer:
    def __init__(self, min_contour_area: float = 5.0, max_contour_area: float = 500.0):
        self.min_contour_area = min_contour_area
        self.max_contour_area = max_contour_area

    def analyze_trajectory_video(
        self,
        video_path: str,
        pixels_per_foot: Optional[float] = None,
        bullet_mass_grains: float = 115.0,
        drag_coefficient: float = 0.16,
        cross_area_sq_in: float = 0.09
    ) -> Dict[str, Any]:
        """
        Processes video frame-by-frame using frame differencing to track projectile 
        centroids, estimates initial velocity and angle, and computes 2D trajectory prediction.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Unable to open video file at {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30.0  # Fallback standard frame rate

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        prev_frame = None
        trajectory_points: List[Tuple[float, float, float]] = []  # (frame_time, x_px, y_px)
        frame_idx = 0

        while Cap_is_running := cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Preprocess frame: Gray -> Gaussian Blur
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            if prev_frame is not None:
                # 1. Frame Differencing to isolate fast-moving object
                delta = cv2.absdiff(prev_frame, blurred)
                _, thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)
                thresh = cv2.dilate(thresh, None, iterations=2)

                # 2. Find moving contours
                contours, _ = cv2.findContours(
                    thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )

                for contour in contours:
                    area = cv2.contourArea(contour)
                    if self.min_contour_area <= area <= self.max_contour_area:
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cx = float(M["m10"] / M["m00"])
                            cy = float(M["m01"] / M["m00"])
                            timestamp = frame_idx / fps
                            # Invert Y to match Cartesian coordinate system (0,0 at bottom-left)
                            cartesian_y = height - cy
                            trajectory_points.append((timestamp, cx, cartesian_y))

            prev_frame = blurred
            frame_idx += 1

        cap.release()

        if len(trajectory_points) < 2:
            return {
                "status": "warning",
                "message": "Insufficient moving projectile frames detected in video.",
                "detected_points_count": len(trajectory_points)
            }

        # 3. Fit 1D Linear/Parabolic Vector to detected points
        times = np.array([pt[0] for pt in trajectory_points])
        xs = np.array([pt[1] for pt in trajectory_points])
        ys = np.array([pt[2] for pt in trajectory_points])

        # Linear fit for directional angle
        dx = xs[-1] - xs[0]
        dy = ys[-1] - ys[0]
        dt = times[-1] - times[0]

        if dt <= 0:
            dt = 0.001

        angle_radians = np.arctan2(dy, dx)
        angle_degrees = float(np.degrees(angle_radians))

        # Pixel velocity
        pixel_distance = float(np.sqrt(dx**2 + dy**2))
        velocity_px_per_sec = pixel_distance / dt

        # 4. Calibrate velocity if scale is supplied
        estimated_velocity_fps = 1150.0  # Default fallback if unscaled
        if pixels_per_foot and pixels_per_foot > 0:
            estimated_velocity_fps = round((velocity_px_per_sec / pixels_per_foot), 2)

        # 5. Run trajectory physics model with extracted video metrics
        physics_prediction = ForensicPhysicsEngine.calculate_ballistic_trajectory(
            velocity_fps=estimated_velocity_fps,
            angle_degrees=max(0.1, angle_degrees),
            bullet_mass_grains=bullet_mass_grains,
            drag_coefficient=drag_coefficient,
            cross_sectional_area_sq_in=cross_area_sq_in
        )

        return {
            "status": "success",
            "video_metadata": {
                "frame_width": width,
                "frame_height": height,
                "fps": fps,
                "total_frames_processed": frame_idx
            },
            "extracted_metrics": {
                "detected_points_count": len(trajectory_points),
                "launch_angle_degrees": round(angle_degrees, 2),
                "pixel_velocity_px_sec": round(velocity_px_per_sec, 2),
                "calibrated_velocity_fps": estimated_velocity_fps
            },
            "physics_trajectory_prediction": physics_prediction,
            "tracked_coordinates": [
                {"t_sec": round(t, 4), "x_px": round(x, 1), "y_px": round(y, 1)}
                for t, x, y in trajectory_points
            ]
        }
