#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
root=../../..
gen=../../G/round9
py="$root/opt/venv/bin/python"
tool="$root/ralph/lanes/A/audit_strip_extensions.py"
bins=("$gen"/mixed26.pilot.{0,1,2}.log)
production=("$gen"/mixed26.production.{0,1,2,3,4,5,6,7}.log)
LC_ALL=C sort "$gen/mixed26.keys" | cmp - mixed.j3.sorted
exec "$py" -B "$tool" replay "$gen/mixed26.keys" "${A_AUDIT_FOLDER:-mixed26-audit}" \
    --schedule "$gen/mixed26.pilot.keys" --batch "$gen/mixed26.pilot" "${bins[@]}" \
    --schedule "$gen/mixed26.production.keys" --batch "$gen/mixed26.production" "${production[@]}" \
    --require-cover "$@"
