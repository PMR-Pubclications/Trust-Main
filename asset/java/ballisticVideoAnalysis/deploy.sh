#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
APP_DIR=/opt/ballistics-video-analysis
CONFIG_DIR=/etc/ballistics-video-analysis
LOG_DIR=/var/log/ballistics-video-analysis
SERVICE_NAME=ballistics.service

if [ "$(id -u)" -ne 0 ]; then
    echo "Run this installer as root (for example: sudo $0)." >&2
    exit 1
fi

command -v mvn >/dev/null 2>&1 || { echo "Maven is required to build the service." >&2; exit 1; }
command -v java >/dev/null 2>&1 || { echo "Java 17 or newer is required to run the service." >&2; exit 1; }
command -v systemctl >/dev/null 2>&1 || { echo "systemctl is required on the target Linux host." >&2; exit 1; }

if ! getent passwd ballistics >/dev/null; then
    useradd --system --user-group --no-create-home --shell /usr/sbin/nologin ballistics
fi

mvn -f "$PROJECT_DIR/pom.xml" clean package

install -d -o root -g root -m 0755 "$APP_DIR"
install -o root -g root -m 0644 "$PROJECT_DIR/target/ballistic-video-analysis.jar" \
    "$APP_DIR/ballistic-video-analysis.jar"
install -d -o root -g ballistics -m 0750 "$CONFIG_DIR"
if [ ! -e "$CONFIG_DIR/application.properties" ]; then
    install -o root -g ballistics -m 0640 "$PROJECT_DIR/conf/application.properties" \
        "$CONFIG_DIR/application.properties"
fi
install -d -o ballistics -g ballistics -m 0750 "$LOG_DIR"
install -o root -g root -m 0644 "$PROJECT_DIR/ballistics.service" \
    "/etc/systemd/system/$SERVICE_NAME"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
if systemctl is-active --quiet "$SERVICE_NAME"; then
    systemctl restart "$SERVICE_NAME"
else
    systemctl start "$SERVICE_NAME"
fi

echo "Installed and started $SERVICE_NAME."
echo "Check status with: systemctl status $SERVICE_NAME"
echo "Follow logs with: journalctl -u $SERVICE_NAME -f"
