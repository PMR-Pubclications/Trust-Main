#!/usr/bin/env python3
"""EMS Continuous Ambient Audio Recorder & Clinical Override Logger.

Mapped to: modules/Annon/scripts/utils/ems_override_logger.py
Maintains background audio recording during field incidents, tracks when a paramedic 
administers a flagged medication against system warnings, and compiles an audit-ready 
incident report package (JSON + Audio Timestamp) for hospital/ePCR submission.
"""

from __future__ import annotations

import datetime
import json
import os
import queue
import threading
import time
import wave
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# Audio Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024
REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "reports" / "incident_packages"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class OverrideEvent:
    timestamp: str
    patient_id: str
    proposed_medication: str
    conflict_type: str
    system_warning_issued: str
    medic_override_detected: bool = False
    medic_statement_transcript: Optional[str] = None
    audio_file_path: Optional[str] = None
    audio_timestamp_start: float = 0.0
    audio_timestamp_end: float = 0.0


class BackgroundAudioRecorder(threading.Thread):
    """Continuously records ambient cabin/field audio in a background thread."""

    def __init__(self, output_wav_path: Path):
        super().__init__()
        self.output_wav_path = output_wav_path
        self._stop_event = threading.Event()
        self.start_time = time.time()
        self.frames: List[bytes] = []

    def run(self) -> None:
        try:
            import pyaudio  # type: ignore
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE
            )
            print(f"🎙️ [AUDIO RECORDER] Background recording started -> {self.output_wav_path.name}")
            while not self._stop_event.is_set():
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                self.frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()
            self._save_wav()
        except Exception as e:
            print(f"⚠️ [AUDIO RECORDER] Hardware mic unavailable ({e}). Running in simulated audio logging mode.")
            self._simulate_recording()

    def _simulate_recording(self) -> None:
        while not self._stop_event.is_set():
            time.sleep(0.1)

    def _save_wav(self) -> None:
        if not self.frames:
            return
        import pyaudio  # type: ignore
        p = pyaudio.PyAudio()
        wf = wave.open(str(self.output_wav_path), 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        p.terminate()
        print(f"💾 [AUDIO RECORDER] Ambient audio saved to {self.output_wav_path}")

    def stop(self) -> float:
        self._stop_event.set()
        return time.time() - self.start_time


class ClinicalOverrideTracker:
    """Monitors field decisions and flags non-compliant medication delivery."""

    def __init__(self, incident_id: str, patient_id: str):
        self.incident_id = incident_id
        self.patient_id = patient_id
        self.session_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Start persistent audio capture
        self.audio_filename = REPORTS_DIR / f"audio_{self.incident_id}_{self.session_timestamp}.wav"
        self.recorder = BackgroundAudioRecorder(self.audio_filename)
        self.recorder.start()

        self.pending_warnings: Dict[str, OverrideEvent] = {}
        self.confirmed_overrides: List[OverrideEvent] = []

    def log_system_warning(self, medication: str, conflict_type: str, warning_msg: str) -> None:
        """Called when medication checker issues a 'STOP_ABORT' or critical warning."""
        current_time = time.time() - self.recorder.start_time
        event = OverrideEvent(
            timestamp=datetime.datetime.now().isoformat(),
            patient_id=self.patient_id,
            proposed_medication=medication.upper(),
            conflict_type=conflict_type,
            system_warning_issued=warning_msg,
            audio_file_path=str(self.audio_filename),
            audio_timestamp_start=round(current_time, 2)
        )
        self.pending_warnings[medication.lower()] = event
        print(f"🚨 [OVERRIDE TRACKER] Warning active for {medication.upper()}. Monitoring for paramedic action...")

    def register_medic_action(self, medication: str, action_taken: str, transcript: str) -> Optional[OverrideEvent]:
        """Logs if medic confirms administration despite active system warning.
        
        action_taken: 'ADMINISTERED' | 'ABORTED'
        """
        med_key = medication.lower()
        if med_key not in self.pending_warnings:
            return None

        event = self.pending_warnings.pop(med_key)
        event.audio_timestamp_end = round(time.time() - self.recorder.start_time, 2)
        event.medic_statement_transcript = transcript

        if action_taken.upper() in {"ADMINISTERED", "GIVEN", "OVERRIDE"}:
            event.medic_override_detected = True
            self.confirmed_overrides.append(event)
            print(f"\n⚠️ ⚠️ ⚠️ [CRITICAL AUDIT ALERT] OVERRIDE DETECTED ⚠️ ⚠️ ⚠️")
            print(f"Medic administered {medication.upper()} despite warning: '{event.system_warning_issued}'")
            print(f"Transcript captured: \"{transcript}\"\n")
        else:
            print(f"✅ [OVERRIDE TRACKER] Warning honored. Medic aborted {medication.upper()}.")

        return event

    def finalize_report_package(() -> Path:
        """Stops audio recording and generates the final JSON report package for hospital/ePCR transmission."""
        pass


def compile_ePCR_report_package(tracker: ClinicalOverrideTracker) -> Path:
    """Stops audio and outputs structured JSON package ready for HL7 FHIR upload."""
    duration = tracker.recorder.stop()
    report_filename = REPORTS_DIR / f"ePCR_package_{tracker.incident_id}_{tracker.session_timestamp}.json"

    package = {
        "incident_metadata": {
            "incident_id": tracker.incident_id,
            "patient_id": tracker.patient_id,
            "session_start": tracker.session_timestamp,
            "total_audio_duration_seconds": round(duration, 2),
            "ambient_audio_file": str(tracker.audio_filename)
        },
        "safety_audit_summary": {
            "total_critical_warnings": len(tracker.pending_warnings) + len(tracker.confirmed_overrides),
            "total_overrides_detected": len(tracker.confirmed_overrides),
            "compliance_flag": "NON_COMPLIANT_OVERRIDE" if tracker.confirmed_overrides else "FULL_COMPLIANCE"
        },
        "override_incident_details": [asdict(e) for e in tracker.confirmed_overrides]
    }

    with open(report_filename, "w", encoding="utf-8") as f:
        json.dump(package, f, indent=2)

    print(f"📦 [REPORT PACKAGER] Package generated: {report_filename}")
    return report_filename


# ==============================================================================
# Simulation / Integration Example
# ==============================================================================
if __name__ == "__main__":
    # Initialize Incident Session
    tracker = ClinicalOverrideTracker(incident_id="INC-2026-9921", patient_id="EHR-88392")

    time.sleep(1.0)  # Simulate ambient recording

    # Step 1: System issues critical warning
    tracker.log_system_warning(
        medication="Nitroglycerin",
        conflict_type="DRUG_INTERACTION",
        warning_msg="Fatal Hypotension Risk: Active prescription for Sildenafil detected."
    )

    time.sleep(2.0)  # Paramedic treats patient

    # Step 2: Paramedic proceeds anyway and speaks intention into mic/tablet
    tracker.register_medic_action(
        medication="Nitroglycerin",
        action_taken="ADMINISTERED",
        transcript="Command, patient chest pain is 10/10, pushing 0.4mg Nitro sublingual regardless of Sildenafil history."
    )

    time.sleep(1.0)

    # Step 3: Close session and build report package for hospital handover
    final_package_path = compile_ePCR_report_package(tracker)
    
    with open(final_package_path, "r") as f:
        print("\n--- GENERATED ePCR / HOSPITAL REPORT PACKAGE ---")
        print(f.read())
