#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd); lane="$root/ralph/lanes/D"; old="$root/scratch/D/m14r23"; n=$1
parent=$(awk -v n="$n" '$1==n{print $2}' "$old/staticpids.tsv"); expected="$root/opt/venv/bin/python -B $lane/static23.py $n"
while [[ $(ps -o args= -p "$parent") == "$expected" ]]; do sleep 4; done
exec "$root/opt/venv/bin/python" -B "$lane/wingproof23.py" shard "$n"
