#!/usr/bin/env bash
#
# security/deploy.sh
#
# Convenience deployment script for the standalone Trust security service
# on a Linux server. Builds and (re)starts the Docker Compose stack defined
# in security/docker-compose.yml.
#
# Usage:
#   ./security/deploy.sh            # build + start (or restart) the service
#   ./security/deploy.sh down       # stop and remove the service
#   ./security/deploy.sh logs       # tail logs
#
# Prerequisites (documented in security/README.md):
#   - Docker Engine + the Docker Compose plugin installed on the Linux host
#   - security/.env created from security/.env.example with real values
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yml"
ENV_FILE="${SCRIPT_DIR}/.env"
ACTION="${1:-up}"

if [ ! -f "${ENV_FILE}" ]; then
  echo "ERROR: ${ENV_FILE} not found." >&2
  echo "Copy security/.env.example to security/.env and fill in real values first." >&2
  exit 1
fi

# Refuse to run as root unless explicitly overridden; Docker itself will
# still run the container as the unprivileged 'security' user defined in
# the Dockerfile, but the deploy script should not require root either.
if [ "$(id -u)" -eq 0 ] && [ "${ALLOW_ROOT_DEPLOY:-0}" != "1" ]; then
  echo "WARNING: running as root. Prefer a non-root user with docker group" \
       "membership. Set ALLOW_ROOT_DEPLOY=1 to suppress this check." >&2
fi

compose() {
  docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" "$@"
}

case "${ACTION}" in
  up)
    compose build
    compose up -d
    compose ps
    ;;
  down)
    compose down
    ;;
  logs)
    compose logs -f --tail=200
    ;;
  restart)
    compose restart
    ;;
  *)
    echo "Unknown action: ${ACTION}" >&2
    echo "Usage: $0 [up|down|restart|logs]" >&2
    exit 1
    ;;
esac
