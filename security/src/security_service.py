import configparser
import json
import logging
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


LOGGER = logging.getLogger("security_service")


class PolicyError(Exception):
    pass


def validate_policy(path):
    policy = configparser.ConfigParser(interpolation=None)
    try:
        with Path(path).open(encoding="utf-8") as policy_file:
            policy.read_file(policy_file)
    except (OSError, configparser.Error, UnicodeError) as error:
        raise PolicyError("policy file cannot be read or parsed") from error

    if not policy.has_section("Security"):
        raise PolicyError("missing [Security] section")
    if policy.get("Security", "require_ssl", fallback="").strip().lower() != "true":
        raise PolicyError("require_ssl must be true")
    if policy.get("Security", "auth_mode", fallback="").strip().lower() != "token":
        raise PolicyError("auth_mode must be token")


def make_handler(policy_path):
    class HealthHandler(BaseHTTPRequestHandler):
        server_version = "SecurityPolicyService"
        sys_version = ""

        def do_GET(self):
            if self.path != "/health":
                self._respond(404, {"status": "not_found"})
                return

            try:
                validate_policy(policy_path)
            except PolicyError as error:
                LOGGER.warning("Health check failed: %s", error)
                self._respond(503, {"status": "unhealthy"})
                return

            self._respond(200, {"status": "ok", "policy": "valid"})

        def _respond(self, status, payload):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            LOGGER.info("HTTP response status=%d client=%s", status, self.client_address[0])

        def log_message(self, format_string, *args):
            return

    return HealthHandler


def main():
    logging.basicConfig(
        level=os.environ.get("SECURITY_SERVICE_LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    host = os.environ.get("SECURITY_SERVICE_HOST", "127.0.0.1")
    policy_path = os.environ.get(
        "SECURITY_SERVICE_POLICY_FILE", "/etc/security-service/policy.ini"
    )
    try:
        port = int(os.environ.get("SECURITY_SERVICE_PORT", "8787"))
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        raise SystemExit("SECURITY_SERVICE_PORT must be an integer from 1 to 65535")

    try:
        validate_policy(policy_path)
        LOGGER.info("Security policy is valid.")
    except PolicyError as error:
        LOGGER.error("Security policy is invalid: %s", error)

    try:
        server = ThreadingHTTPServer((host, port), make_handler(policy_path))
    except OSError as error:
        LOGGER.error("Could not start HTTP listener: %s", error)
        raise SystemExit(1) from error

    LOGGER.info("Listening on %s:%d", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Shutdown requested.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
