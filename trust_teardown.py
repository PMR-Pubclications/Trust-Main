#!/usr/bin/env python3
import json
import os
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.resolve()

def scan_repository_and_generate_meta():
    """
    Scans the repository directory to infer application capabilities,
    generates meta tags, writes a system description, and saves it to app_metadata.json.
    """
    print("[+] Scanning repository for capabilities and generating metadata...")
    
    capabilities = []
    meta_tags = set(["python", "system-lifecycle"])

    # Traverse repository structure
    repo_files = [p.relative_to(REPO_ROOT) for p in REPO_ROOT.rglob('*') if not any(part.startswith('.') for part in p.parts)]
    file_names = {p.name for p in repo_files}
    dir_names = {p.name for p in repo_files if p.is_dir()}

    # Inspect file markers to determine app features
    if "package.json" in file_names or "server.js" in file_names or "node_modules" in dir_names:
        capabilities.append("Node.js Backend & REST API Services")
        meta_tags.update(["nodejs", "api-backend", "server"])

    if any("mine" in f.lower() or "hash" in f.lower() for f in file_names):
        capabilities.append("Background Cryptographic Mining & Telemetry")
        meta_tags.update(["crypto-mining", "background-worker", "telemetry"])

    if any("telemetry" in f.lower() or "log" in f.lower() for f in file_names):
        capabilities.append("Forensic Telemetry & Audit Logging")
        meta_tags.update(["forensics", "telemetry-logging", "audit"])

    if "asset" in dir_names or "assets" in dir_names:
        capabilities.append("Local Asset Storage & Lifecycle Governance")
        meta_tags.update(["asset-management", "local-storage"])

    if any("obfuscate" in f.lower() or "shield" in f.lower() or "crypto" in f.lower() for f in file_names):
        capabilities.append("API Obfuscation & Security Submodules")
        meta_tags.update(["security", "obfuscation", "encryption"])

    if not capabilities:
        capabilities.append("Core Teardown & Maintenance Operations")

    description = (
        f"Automated service suite operating in {REPO_ROOT.name}. "
        f"Core capabilities include: {', '.join(capabilities)}. "
        f"Configured with background process lifecycle management and system maintenance routines."
    )

    metadata = {
        "app_name": REPO_ROOT.name,
        "description": description,
        "meta_tags": sorted(list(meta_tags)),
        "capabilities": capabilities,
        "last_scanned": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }

    # Write out meta file
    meta_path = REPO_ROOT / "app_metadata.json"
    try:
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        print(f"[+] Meta tag information generated and saved to {meta_path.name}")
        print(f"    - Description: {description}")
        print(f"    - Meta Tags: {', '.join(metadata['meta_tags'])}\n")
    except Exception as e:
        print(f"[-] Failed to save app_metadata.json: {e}\n")

    return metadata


def execute_teardown():
    print("Handshake acknowledged. Executing background resource purge...")
    
    target_processes = [
        "background-mining-worker",
        "telemetry-logger",
        "non-critical-submodule"
    ]

    for proc_name in target_processes:
        try:
            subprocess.run(["pkill", "-f", proc_name], capture_output=True, text=True)
        except Exception:
            pass

    # Clear kernel caches
    try:
        subprocess.run(["sync"], check=False)
        with open('/proc/sys/vm/drop_caches', 'w') as f:
            f.write('3')
    except Exception:
        print("Note: Clearing system caches requires root privileges.")

    print("Teardown routine completed successfully.")
    return target_processes


def execute_maintenance_routine(stopped_modules):
    """
    Executes post-shutdown maintenance routines: clears stale lock/PID files,
    verifies logging paths, rotates oversized log files, and resets state files.
    """
    print("\n[+] Triggering post-shutdown module maintenance routine...")

    # 1. Clean stale locks / temp runtime artifacts in repo asset/temp locations
    search_dirs = [REPO_ROOT / "asset" / "tmp", REPO_ROOT / "tmp", REPO_ROOT]
    for target_dir in search_dirs:
        if target_dir.exists() and target_dir.is_dir():
            for lock_file in target_dir.glob("*.lock"):
                try:
                    lock_file.unlink()
                    print(f"    - Removed stale lock: {lock_file.name}")
                except Exception as e:
                    print(f"    - Unable to delete {lock_file.name}: {e}")

    # 2. Maintain state & rotate module logs
    for module in stopped_modules:
        print(f"    - Running maintenance checks for module: '{module}'")
        log_file = REPO_ROOT / f"{module}.log"
        
        # Log rotation if file size exceeds 5MB
        if log_file.exists() and log_file.stat().st_size > 5 * 1024 * 1024:
            try:
                backup_log = REPO_ROOT / f"{module}.log.old"
                log_file.rename(backup_log)
                log_file.touch()
                print(f"      Rotated oversized log for {module}")
            except Exception as e:
                print(f"      Log rotation failed for {module}: {e}")

    # 3. Final sync flush
    subprocess.run(["sync"], check=False)
    print("[+] All module maintenance tasks completed. System primed for restart.")


if __name__ == "__main__":
    scan_repository_and_generate_meta()
    stopped_processes = execute_teardown()
    execute_maintenance_routine(stopped_processes)
