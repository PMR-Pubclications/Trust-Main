#!/usr/bin/env python3
"""Standalone live maintenance routine for Trust-Main.

Features:
- Continuous maintenance loop (or one-shot mode)
- CLI flags: --once, --interval, --dry-run, --log-level, --pid-file, --log-file
- Single-instance lock via PID file
- Graceful shutdown on SIGINT/SIGTERM
- Structured logging to stdout and optional file
- Explicit non-zero exit codes on hard failures
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).parent.resolve()
DEFAULT_INTERVAL_SECONDS = 300
DEFAULT_PID_FILE = REPO_ROOT / "trust_teardown.pid"
DEFAULT_LOG_FILE = REPO_ROOT / "trust_teardown.log"

SHUTDOWN_REQUESTED = False


@dataclass
class RuntimeConfig:
    interval: int
    once: bool
    dry_run: bool
    pid_file: Path
    log_file: Path | None


def parse_args() -> RuntimeConfig:
    parser = argparse.ArgumentParser(
        description="Run Trust standalone live maintenance routine."
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run one maintenance cycle and exit.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL_SECONDS,
        help=f"Seconds between cycles in live mode (default: {DEFAULT_INTERVAL_SECONDS}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log actions without applying destructive/system changes.",
    )
    parser.add_argument(
        "--pid-file",
        default=str(DEFAULT_PID_FILE),
        help=f"PID/lock file path (default: {DEFAULT_PID_FILE}).",
    )
    parser.add_argument(
        "--log-file",
        default=str(DEFAULT_LOG_FILE),
        help=f"Optional log file path (default: {DEFAULT_LOG_FILE}). Use '' to disable file logging.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity.",
    )

    ns = parser.parse_args()
    configure_logging(ns.log_level, ns.log_file)

    log_file = None if ns.log_file == "" else Path(ns.log_file)
    return RuntimeConfig(
        interval=max(1, ns.interval),
        once=ns.once,
        dry_run=ns.dry_run,
        pid_file=Path(ns.pid_file),
        log_file=log_file,
    )


def configure_logging(level: str, log_file: str) -> None:
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file != "":
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=handlers,
    )


def _signal_handler(signum, _frame) -> None:
    global SHUTDOWN_REQUESTED
    SHUTDOWN_REQUESTED = True
    logging.warning("Received signal %s. Shutdown requested.", signum)


def register_signal_handlers() -> None:
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)


def ensure_single_instance(pid_file: Path) -> None:
    if pid_file.exists():
        try:
            existing_pid = int(pid_file.read_text(encoding="utf-8").strip())
            os.kill(existing_pid, 0)
            logging.error("Another instance is already running (PID %s).", existing_pid)
            sys.exit(2)
        except ProcessLookupError:
            logging.warning("Stale PID file found. Replacing: %s", pid_file)
        except Exception:
            logging.warning("Unreadable PID file. Replacing: %s", pid_file)

    pid_file.write_text(str(os.getpid()), encoding="utf-8")
    logging.info("Instance lock acquired with PID file: %s", pid_file)


def remove_pid_file(pid_file: Path) -> None:
    try:
        if pid_file.exists():
            pid_file.unlink()
            logging.info("PID file removed: %s", pid_file)
    except Exception as exc:
        logging.warning("Failed to remove PID file %s: %s", pid_file, exc)


def scan_repository_and_generate_meta(dry_run: bool = False) -> dict:
    logging.info("Scanning repository and generating metadata...")

    capabilities: List[str] = []
    meta_tags = {"python", "system-lifecycle", "maintenance"}

    repo_files = [
        p.relative_to(REPO_ROOT)
        for p in REPO_ROOT.rglob("*")
        if not any(part.startswith(".") for part in p.parts)
    ]
    file_names = {p.name for p in repo_files}
    dir_names = {p.name for p in repo_files if (REPO_ROOT / p).is_dir()}

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
        "meta_tags": sorted(meta_tags),
        "capabilities": capabilities,
        "last_scanned": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
    }

    meta_path = REPO_ROOT / "app_metadata.json"
    if dry_run:
        logging.info("[dry-run] Would write metadata to %s", meta_path)
    else:
        with meta_path.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        logging.info("Metadata written: %s", meta_path)

    return metadata


def execute_teardown(dry_run: bool = False) -> List[str]:
    logging.info("Executing background resource purge...")

    target_processes = [
        "background-mining-worker",
        "telemetry-logger",
        "non-critical-submodule",
    ]

    for proc_name in target_processes:
        if dry_run:
            logging.info("[dry-run] Would terminate process pattern: %s", proc_name)
            continue

        try:
            subprocess.run(["pkill", "-f", proc_name], capture_output=True, text=True, check=False)
            logging.debug("pkill attempted for process pattern: %s", proc_name)
        except Exception as exc:
            logging.warning("Failed pkill for %s: %s", proc_name, exc)

    if dry_run:
        logging.info("[dry-run] Would run sync and attempt cache drop")
        return target_processes

    try:
        subprocess.run(["sync"], check=False)
        with open("/proc/sys/vm/drop_caches", "w", encoding="utf-8") as f:
            f.write("3")
    except Exception:
        logging.warning("Clearing system caches skipped (root privileges required).")

    logging.info("Teardown phase complete.")
    return target_processes


def execute_maintenance_routine(stopped_modules: List[str], dry_run: bool = False) -> None:
    logging.info("Triggering post-shutdown maintenance routine...")

    search_dirs = [REPO_ROOT / "asset" / "tmp", REPO_ROOT / "tmp", REPO_ROOT]
    for target_dir in search_dirs:
        if target_dir.exists() and target_dir.is_dir():
            for lock_file in target_dir.glob("*.lock"):
                try:
                    if dry_run:
                        logging.info("[dry-run] Would remove stale lock: %s", lock_file)
                    else:
                        lock_file.unlink()
                        logging.info("Removed stale lock: %s", lock_file)
                except Exception as exc:
                    logging.warning("Unable to delete %s: %s", lock_file, exc)

    for module in stopped_modules:
        log_file = REPO_ROOT / f"{module}.log"
        if log_file.exists() and log_file.stat().st_size > 5 * 1024 * 1024:
            try:
                backup_log = REPO_ROOT / f"{module}.log.old"
                if dry_run:
                    logging.info("[dry-run] Would rotate oversized log: %s -> %s", log_file, backup_log)
                else:
                    log_file.rename(backup_log)
                    log_file.touch()
                    logging.info("Rotated oversized log for module: %s", module)
            except Exception as exc:
                logging.warning("Log rotation failed for %s: %s", module, exc)

    if dry_run:
        logging.info("[dry-run] Would run final sync")
    else:
        subprocess.run(["sync"], check=False)

    logging.info("Maintenance cycle complete.")


def run_cycle(cfg: RuntimeConfig) -> None:
    scan_repository_and_generate_meta(dry_run=cfg.dry_run)
    stopped_processes = execute_teardown(dry_run=cfg.dry_run)
    execute_maintenance_routine(stopped_processes, dry_run=cfg.dry_run)


def main() -> int:
    cfg = parse_args()
    register_signal_handlers()
    ensure_single_instance(cfg.pid_file)

    try:
        if cfg.once:
            logging.info("Running one-shot maintenance cycle.")
            run_cycle(cfg)
            return 0

        logging.info("Starting live maintenance loop with interval=%ss", cfg.interval)
        while not SHUTDOWN_REQUESTED:
            cycle_start = time.time()
            run_cycle(cfg)

            elapsed = max(0, int(time.time() - cycle_start))
            sleep_for = max(1, cfg.interval - elapsed)
            logging.info("Cycle finished in %ss. Next run in %ss.", elapsed, sleep_for)

            for _ in range(sleep_for):
                if SHUTDOWN_REQUESTED:
                    break
                time.sleep(1)

        logging.info("Shutdown requested. Exiting live loop.")
        return 0

    except KeyboardInterrupt:
        logging.info("Interrupted by user.")
        return 130
    except Exception as exc:
        logging.exception("Fatal error in maintenance routine: %s", exc)
        return 1
    finally:
        remove_pid_file(cfg.pid_file)


if __name__ == "__main__":
    sys.exit(main())
