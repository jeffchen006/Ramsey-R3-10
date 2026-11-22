#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd); lane="$root/ralph/lanes/D"; python="$root/opt/venv/bin/python"; slot=$1
parent=$(awk -v slot="$slot" '$1==slot{print $2}' pids.tsv)
while args=$(ps -o args= -p "$parent") && [[ "$args" == *"$lane/work24.py worker manifest $slot 30" ]]; do sleep 2; done
if mkdir cal5.claim 2>/dev/null; then "$python" -B "$lane/wing24.py" cal 5 >cal5.log 2>&1 && touch cal5.ok; fi
until [[ -e cal5.ok ]]; do sleep 1;done
for pilot in $(cat splitpilot); do
    if mkdir "claimed.$pilot" 2>/dev/null; then "$python" -B "$lane/work24.py" pilot "$pilot"; fi
done
until [[ -e splitgo ]];do sleep 2;done
exec "$python" -B "$lane/work24.py" worker splitmanifest "$slot" 30
