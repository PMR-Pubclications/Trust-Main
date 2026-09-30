import http.client
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

from security_service import PolicyError, make_handler, validate_policy


VALID_POLICY = "[Security]\nrequire_ssl = true\nauth_mode = token\n"


class SecurityPolicyTests(unittest.TestCase):
    def test_accepts_secure_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            policy_path = Path(directory) / "policy.ini"
            policy_path.write_text(VALID_POLICY, encoding="utf-8")

            validate_policy(policy_path)

    def test_rejects_policy_without_ssl(self):
        with tempfile.TemporaryDirectory() as directory:
            policy_path = Path(directory) / "policy.ini"
            policy_path.write_text(
                "[Security]\nrequire_ssl = false\nauth_mode = token\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(PolicyError, "require_ssl must be true"):
                validate_policy(policy_path)

    def test_health_endpoint_reports_policy_status(self):
        with tempfile.TemporaryDirectory() as directory:
            policy_path = Path(directory) / "policy.ini"
            policy_path.write_text(VALID_POLICY, encoding="utf-8")
            server = ThreadingHTTPServer(
                ("127.0.0.1", 0), make_handler(policy_path)
            )
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            self.addCleanup(server.server_close)
            self.addCleanup(thread.join)
            self.addCleanup(server.shutdown)

            connection = http.client.HTTPConnection(*server.server_address)
            self.addCleanup(connection.close)
            connection.request("GET", "/health")
            response = connection.getresponse()

            self.assertEqual(response.status, 200)
            self.assertEqual(response.read(), b'{"status": "ok", "policy": "valid"}')

            policy_path.write_text(
                "[Security]\nrequire_ssl = false\nauth_mode = token\n",
                encoding="utf-8",
            )
            connection.request("GET", "/health")
            response = connection.getresponse()

            self.assertEqual(response.status, 503)
            self.assertEqual(response.read(), b'{"status": "unhealthy"}')

    def test_unknown_endpoint_is_not_found(self):
        with tempfile.TemporaryDirectory() as directory:
            policy_path = Path(directory) / "policy.ini"
            policy_path.write_text(VALID_POLICY, encoding="utf-8")
            server = ThreadingHTTPServer(
                ("127.0.0.1", 0), make_handler(policy_path)
            )
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            self.addCleanup(server.server_close)
            self.addCleanup(thread.join)
            self.addCleanup(server.shutdown)

            connection = http.client.HTTPConnection(*server.server_address)
            self.addCleanup(connection.close)
            connection.request("GET", "/")
            response = connection.getresponse()

            self.assertEqual(response.status, 404)
            self.assertEqual(response.read(), b'{"status": "not_found"}')


if __name__ == "__main__":
    unittest.main()
