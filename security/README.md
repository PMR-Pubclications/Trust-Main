# Security Policy Service

This standalone Python service validates a small security policy and exposes
only a health endpoint. Its policy checks reflect security settings already
present in the repository (`require_ssl` and token authentication). It does not
authenticate application users, provide TLS termination, or read/store tokens
or other secrets.

The project uses only the Python 3 standard library and builds to an executable
zip application. It does not depend on the rest of Trust-Main.

## Prerequisites

- Linux with systemd
- Python 3.9 or newer
- Root privileges for installation

## Build and test

From this directory:

```sh
./build.sh
python3 -m unittest discover -s tests -v
```

`build.sh` validates the Python sources, runs the tests, and creates
`security-service.pyz`. The build artifact is ignored by Git.

## Install or update as a systemd service

Copy this folder to the Linux server, then run:

```sh
sudo ./install.sh
```

The idempotent installer builds and tests the application, installs the
executable under `/opt/security-service/`, installs the systemd unit, and
enables and restarts the service. It installs the example policy and
environment file only when those files do not already exist, preserving
administrator changes on redeploy.

Manage the service and view logs with:

```sh
sudo systemctl status security-service
sudo systemctl stop security-service
sudo systemctl start security-service
sudo systemctl enable security-service
sudo journalctl -u security-service -f
```

To update, copy the new `/security` project to the server and rerun
`sudo ./install.sh`.

## Configuration

The installer creates `/etc/default/security-service` and
`/etc/security-service/policy.ini`. Edit these files and restart the service:

```sh
sudo systemctl restart security-service
```

Supported environment variables in `/etc/default/security-service`:

| Variable | Default | Purpose |
| --- | --- | --- |
| `SECURITY_SERVICE_HOST` | `127.0.0.1` | HTTP listen address. Keep loopback unless access is protected by a trusted network or proxy. |
| `SECURITY_SERVICE_PORT` | `8787` | HTTP listen port (`1`–`65535`). |
| `SECURITY_SERVICE_POLICY_FILE` | `/etc/security-service/policy.ini` | Policy file to validate. |
| `SECURITY_SERVICE_LOG_LEVEL` | `INFO` | Python logging level. |

The policy file must contain:

```ini
[Security]
require_ssl = true
auth_mode = token
```

An invalid or unreadable policy produces an unhealthy response and a
diagnostic in the service journal. The validator does not handle secret values;
store any application credentials separately using the host's secret-management
mechanism.

## Health check

By default, verify the service and current policy with:

```sh
curl --fail http://127.0.0.1:8787/health
```

A valid policy returns HTTP 200 with `{"status": "ok", "policy": "valid"}`.
An invalid policy returns HTTP 503 with `{"status": "unhealthy"}`. Other paths
return HTTP 404.
