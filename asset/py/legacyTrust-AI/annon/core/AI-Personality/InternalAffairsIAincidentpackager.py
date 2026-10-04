import collections
import dataclasses
import datetime
import hashlib
import json
import logging
import time
from typing import Dict, List, Optional, Tuple
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


@dataclasses.dataclass
class IncidentPackage:
    officer_id: str
    trigger_type: str
    timestamp: str
    gps_coordinates: Tuple[float, float]
    audio_buffer_sha256: str
    raw_audio_bytes: bytes
    telemetry_summary: Dict[str, float]

    def to_json(self) -> str:
        return json.dumps({
            "officer_id": self.officer_id,
            "trigger_type": self.trigger_type,
            "timestamp": self.timestamp,
            "gps": {"lat": self.gps_coordinates[0], "lon": self.gps_coordinates[1]},
            "buffer_sha256": self.audio_buffer_sha256,
            "telemetry": self.telemetry_summary
        }, indent=2)


class RollingAudioBuffer:
    """
    Circular audio buffer holding 15 minutes of continuous audio frames.
    Automatically drops the oldest frames when maximum capacity is reached.
    """
    def __init__(self, sample_rate: int = 16000, bytes_per_sample: int = 2, buffer_duration_sec: int = 900):
        self.sample_rate = sample_rate
        self.bytes_per_sample = bytes_per_sample
        self.max_bytes = sample_rate * bytes_per_sample * buffer_duration_sec
        self._buffer = collections.deque()
        self._current_bytes = 0

    def append_chunk(self, audio_chunk: bytes) -> None:
        """Appends raw PCM audio chunk to the rolling ring buffer."""
        chunk_len = len(audio_chunk)
        self._buffer.append(audio_chunk)
        self._current_bytes += chunk_len

        while self._current_bytes > self.max_bytes and self._buffer:
            removed = self._buffer.popleft()
            self._current_bytes -= len(removed)

    def freeze_and_package((self) -> Tuple[bytes, str]:
        """
        Locks the current 15-minute buffer, concatenates PCM stream,
        and computes a SHA-256 cryptographic signature.
        """
        full_audio = b"".join(self._buffer)
        sha256_hash = hashlib.sha256(full_audio).hexdigest()
        return full_audio, sha256_hash


class IMUKinematicAnalyzer:
    """
    Processes 100 Hz accelerometer (g) and gyroscope (deg/s) sensor streams
    to differentiate phone drops from active physical struggles.
    """
    def __init__(self, sampling_rate_hz: int = 100):
        self.fs = sampling_rate_hz

    def analyze_window(self, accel_data: np.ndarray, gyro_data: np.ndarray) -> Dict[str, bool | float]:
        """
        Evaluates a sliding window of IMU data.
        accel_data: N x 3 array [ax, ay, az] in g units
        gyro_data:  N x 3 array [gx, gy, gz] in deg/sec
        """
        if len(accel_data) < self.fs or len(gyro_data) < self.fs:
            return {"is_drop": False, "is_struggle": False}

        # 1. Magnitude Computations
        a_mag = np.linalg.norm(accel_data, axis=1)  # Acceleration magnitude
        w_mag = np.linalg.norm(gyro_data, axis=1)   # Angular velocity magnitude

        # 2. Ballistic Drop Checks
        # Free-fall: a_mag < 0.2g for at least 180 ms (18 samples at 100 Hz)
        free_fall_mask = a_mag < 0.2
        max_free_fall_samples = self._max_consecutive_true(free_fall_mask)
        has_free_fall = max_free_fall_samples >= int(0.18 * self.fs)

        # High-G Impact Spike (> 16g)
        max_g = np.max(a_mag)
        has_impact = max_g >= 16.0

        # Settling / Rest phase within tail of window (< 30 deg/s)
        tail_gyro_quiet = np.mean(w_mag[-int(0.4 * self.fs):]) < 30.0
        is_drop = has_free_fall and has_impact and tail_gyro_quiet

        # 3. Physical Struggle Kinematic Checks
        # Dynamic Kinetic Energy: average absolute deviation from 1.0g gravity baseline
        e_kinetic = np.mean(np.abs(a_mag - 1.0))

        # Gyroscopic Saturation: percentage of window where rotation >= 250 deg/s
        gyro_saturation_ratio = np.sum(w_mag >= 250.0) / len(w_mag)

        # Vector Jerk Reversals (directional chaos)
        jerk = np.diff(accel_data, axis=0) * self.fs
        jerk_mag = np.linalg.norm(jerk, axis=1)
        high_jerk_rate = np.sum(jerk_mag > 30.0) / len(jerk_mag)

        # Struggle Condition: Sustained kinetic energy >= 1.25g, >65% gyro saturation, no free-fall
        is_struggle = (
            not has_free_fall and
            e_kinetic >= 1.25 and
            gyro_saturation_ratio >= 0.65 and
            high_jerk_rate >= 0.20
        )

        return {
            "is_drop": bool(is_drop),
            "is_struggle": bool(is_struggle),
            "max_g": float(max_g),
            "e_kinetic": float(e_kinetic),
            "gyro_saturation": float(gyro_saturation_ratio)
        }

    @staticmethod
    def _max_consecutive_true(mask: np.ndarray) -> int:
        max_count = current = 0
        for val in mask:
            if val:
                current += 1
                max_count = max(max_count, current)
            else:
                current = 0
        return max_count


class EscalationEngine:
    """
    Coordinates shift monitoring, sensor fusion validation, buffer locking,
    and Internal Affairs secure dispatch.
    """
    def __init__(self, officer_id: str):
        self.officer_id = officer_id
        self.audio_buffer = RollingAudioBuffer()
        self.imu_analyzer = IMUKinematicAnalyzer(sampling_rate_hz=100)
        self.is_on_duty = True

    def process_telemetry_frame(
        self,
        audio_chunk: bytes,
        accel_window: np.ndarray,
        gyro_window: np.ndarray,
        acoustic_trigger_flag: bool,
        current_gps: Tuple[float, float]
    ) -> Optional[IncidentPackage]:
        """Main event loop processing pipeline."""
        if not self.is_on_duty:
            return None

        # 1. Update Continuous Rolling Ring Buffer
        self.audio_buffer.append_chunk(audio_chunk)

        # 2. Perform Kinematic Analysis
        imu_results = self.imu_analyzer.analyze_window(accel_window, gyro_window)

        # 3. Correlated Trigger Logic
        # Require acoustic distress OR mechanical struggle flag
        is_escalated = acoustic_trigger_flag or imu_results["is_struggle"]

        if is_escalated:
            logging.warning("INCIDENT FLAGGED: Freezing audio buffer & packaging telemetry...")
            audio_bytes, buffer_hash = self.audio_buffer.freeze_and_package()

            trigger_type = "ACOUSTIC_AND_KINEMATIC" if (acoustic_trigger_flag and imu_results["is_struggle"]) else (
                "KINEMATIC_STRUGGLE" if imu_results["is_struggle"] else "ACOUSTIC_DISTRESS"
            )

            package = IncidentPackage(
                officer_id=self.officer_id,
                trigger_type=trigger_type,
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                gps_coordinates=current_gps,
                audio_buffer_sha256=buffer_hash,
                raw_audio_bytes=audio_bytes,
                telemetry_summary={
                    "max_g": imu_results["max_g"],
                    "e_kinetic": imu_results["e_kinetic"],
                    "gyro_saturation": imu_results["gyro_saturation"]
                }
            )
            self._dispatch_to_internal_affairs(package)
            return package

        return None

    def handle_device_power_off(self) -> None:
        """Handles contractually mandated auto-clockout on shutdown."""
        logging.info(f"Officer {self.officer_id}: Power-off detected. Executing contract clock-out sequence.")
        self.is_on_duty = False

    def _dispatch_to_internal_affairs(self, package: IncidentPackage) -> None:
        """Simulates secure TLS transmission to IA queue."""
        logging.info(f"TRANSMITTING TO IA QUEUE -> Package Hash: {package.audio_buffer_sha256}")
        logging.info(f"Metadata Manifest:\n{package.to_json()}")


# --- Simulation / Verification Script ---
if __name__ == "__main__":
    engine = EscalationEngine(officer_id="OFFICER-4821")

    # Simulate 2 seconds of 100 Hz IMU struggle data
    num_samples = 200
    sim_accel = np.random.normal(loc=1.0, scale=1.5, size=(num_samples, 3))  # High dynamic energy
    sim_gyro = np.random.uniform(low=-400.0, high=400.0, size=(num_samples, 3)) # High angular rotation
    sim_audio_chunk = b"\x00\x00" * 3200  # PCM audio chunk placeholder

    # Process frame
    package = engine.process_telemetry_frame(
        audio_chunk=sim_audio_chunk,
        accel_window=sim_accel,
        gyro_window=sim_gyro,
        acoustic_trigger_flag=True,  # Simulate simultaneous acoustic hit
        current_gps=(45.6312, -122.6716)
    )
