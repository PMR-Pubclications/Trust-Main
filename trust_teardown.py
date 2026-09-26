#!/usr/bin/env python3
import sys
import os
import subprocess
import time

LOG_FILE = "/var/log/trustfence_memory.log"

def log_message(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [TEARDOWN] {msg}\n"
    print(entry.strip())
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(entry)
    except Exception:
        pass

def main():
    # Capture the handshake trigger source passed from File 1
    trigger_source = sys.argv[1] if len(sys.argv) > 1 else "UNKNOWN"
    log_message(f"Handshake acknowledged from source: [{trigger_source}]. Purging background processes.")

    # Target non-critical background modules or workers to terminate
    target_processes = [
        "background-mining-worker",
        "telemetry-logger",
        "non-critical-submodule"
    ]

    for proc_name in target_processes:
        try:
            result = subprocess.run(["pkill", "-f", proc_name], capture_output=True, text=True)
            if result.returncode == 0:
                log_message(f"Terminated background process target: {proc_name}")
            else:
                log_message(f"Process target not active or found: {proc_name}")
        except Exception as e:
            log_message(f"Failed to process target {proc_name}: {e}")

    # Reclaim physical RAM at the kernel level
    try:
        subprocess.run(["sync"], check=False)
        with open('/proc/sys/vm/drop_caches', 'w') as f:
            f.write('3')
        log_message("Kernel memory caches successfully cleared.")
    except Exception as e:
        log_message(f"Notice: Clearing system caches requires elevated root permissions: {e}")

    log_message("Handshake routine complete. Resources freed.")

if __name__ == "__main__":
    main()
