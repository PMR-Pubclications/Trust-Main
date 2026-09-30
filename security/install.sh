#!/bin/sh
set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo "Run this installer as root (for example, with sudo)." >&2
    exit 1
fi

for command in python3 systemctl install; do
    if ! command -v "$command" >/dev/null 2>&1; then
        echo "Required command not found: $command" >&2
        exit 1
    fi
done

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
INSTALL_DIR=/opt/security-service
CONFIG_DIR=/etc/security-service
ENV_FILE=/etc/default/security-service
UNIT_FILE=/etc/systemd/system/security-service.service
BUILD_DIR=$(mktemp -d)
trap 'rm -rf "$BUILD_DIR"' EXIT HUP INT TERM

"$SCRIPT_DIR/build.sh" "$BUILD_DIR/security-service.pyz"

install -d -m 0755 "$INSTALL_DIR" "$CONFIG_DIR"
install -m 0755 "$BUILD_DIR/security-service.pyz" "$INSTALL_DIR/security-service.pyz"

if [ ! -e "$CONFIG_DIR/policy.ini" ]; then
    install -m 0644 "$SCRIPT_DIR/policy.example.ini" "$CONFIG_DIR/policy.ini"
fi
if [ ! -e "$ENV_FILE" ]; then
    install -D -m 0644 "$SCRIPT_DIR/security-service.env" "$ENV_FILE"
fi

install -m 0644 "$SCRIPT_DIR/security-service.service" "$UNIT_FILE"
systemctl daemon-reload
systemctl enable --now security-service.service
systemctl restart security-service.service

echo "Installed and started security-service.service."
echo "Check health at http://127.0.0.1:8787/health"
