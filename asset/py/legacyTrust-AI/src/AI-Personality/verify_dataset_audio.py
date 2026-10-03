import json
import re
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import config

WAV_DIR = config.WAV_DIR
TARGET_I = config.TARGET_I
I_TOLERANCE = config.I_TOLERANCE
MAX_TRUE_PEAK = config.MAX_TRUE_PEAK
MAX_WORKERS = config.VERIFY_MAX_WORKERS


def analyze_audio_file(file_path: Path) -> dict:
    """
    Executes FFmpeg loudnorm in print mode to capture precise 
    Integrated Loudness (LUFS) and True Peak (dBFS) JSON metrics.
    """
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-i", str(file_path),
        "-af", f"loudnorm=I={TARGET_I}:TP={config.TARGET_TP}:LRA={config.TARGET_LRA}:print_format=json",
        "-f", "null",
        "-"
    ]

    try:
        # Run FFmpeg command and capture stderr where loudnorm outputs JSON
        result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, check=True)
        
        # Extract JSON block from stderr output
        json_match = re.search(r"\{[\s\S]*?\}", result.stderr)
        if not json_match:
            return {"file": file_path.name, "error": "Failed to parse FFmpeg JSON output"}

        metrics = json.loads(json_match.group(0))
        
        integrated_loudness = float(metrics.get("input_i", 0.0))
        true_peak = float(metrics.get("input_tp", 0.0))

        # Check compliance against targets
        loudness_pass = abs(integrated_loudness - TARGET_I) <= I_TOLERANCE
        peak_pass = true_peak <= MAX_TRUE_PEAK

        passed = loudness_pass and peak_pass

        return {
            "file": file_path.name,
            "passed": passed,
            "integrated_loudness": integrated_loudness,
            "true_peak": true_peak,
            "loudness_pass": loudness_pass,
            "peak_pass": peak_pass
        }

    except Exception as e:
        return {"file": file_path.name, "error": str(e)}


def verify_dataset_specifications():
    if not WAV_DIR.exists():
        print(f"Error: Directory '{WAV_DIR}' does not exist.")
        return

    wav_files = sorted(list(WAV_DIR.glob("*.wav")))
    if not wav_files:
        print(f"No .wav files found in '{WAV_DIR}'.")
        return

    print(f"Scanning {len(wav_files)} WAV clips against specs:")
    print(f"  • Integrated Loudness Target : {TARGET_I} LUFS (±{I_TOLERANCE} LUFS)")
    print(f"  • Max True Peak Cap         : {MAX_TRUE_PEAK} dBFS\n")

    passed_count = 0
    failed_files = []

    # Process files in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(analyze_audio_file, f): f for f in wav_files}
        
        for future in as_completed(futures):
            res = future.result()
            
            if "error" in res:
                print(f"❌ [ERROR] {res['file']}: {res['error']}")
                failed_files.append(res)
            elif res["passed"]:
                passed_count += 1
            else:
                failed_files.append(res)

    # Summary Report Output
    print("=" * 65)
    print(f"VERIFICATION SUMMARY: {passed_count} / {len(wav_files)} PASSED")
    print("=" * 65)

    if failed_files:
        print("\nNON-COMPLIANT CLIPS DETECTED:")
        print(f"{'Filename':<20} | {'Integrated (LUFS)':<18} | {'True Peak (dBFS)':<18} | {'Reason'}")
        print("-" * 65)
        for item in failed_files:
            reasons = []
            if not item.get("loudness_pass", True):
                reasons.append("Loudness Out of Spec")
            if not item.get("peak_pass", True):
                reasons.append("Peak Exceeded")
            
            reason_str = ", ".join(reasons) if reasons else item.get("error", "Unknown")
            i_str = f"{item.get('integrated_loudness', 0):.2f}" if 'integrated_loudness' in item else "N/A"
            tp_str = f"{item.get('true_peak', 0):.2f}" if 'true_peak' in item else "N/A"
            
            print(f"{item['file']:<20} | {i_str:<18} | {tp_str:<18} | {reason_str}")
    else:
        print("\nAll audio clips perfectly meet target RMS/loudness and peak specifications!")


if __name__ == "__main__":
    verify_dataset_specifications()
