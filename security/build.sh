#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OUTPUT=${1:-"$SCRIPT_DIR/security-service.pyz"}

python3 - "$SCRIPT_DIR" <<'PY'
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
for source in (root / "src").glob("*.py"):
    compile(source.read_bytes(), str(source), "exec")
for source in (root / "tests").glob("*.py"):
    compile(source.read_bytes(), str(source), "exec")
PY

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH="$SCRIPT_DIR/src${PYTHONPATH:+:$PYTHONPATH}" \
    python3 -m unittest discover -s "$SCRIPT_DIR/tests" -v

mkdir -p "$(dirname -- "$OUTPUT")"
python3 -m zipapp "$SCRIPT_DIR/src" \
    --main 'security_service:main' \
    --output "$OUTPUT" \
    --python '/usr/bin/env python3'
chmod 0755 "$OUTPUT"
printf 'Built %s\n' "$OUTPUT"
