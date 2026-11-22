#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd); lane="$root/ralph/lanes/D"; old="$root/scratch/D/c6r23/wing"; n=$1; parent=$(awk -v n="$n" '$1==n{print $2}' "$old/pids.tsv")
while args=$(ps -o args= -p "$parent") && [[ "$args" == *"$lane/post23.sh $n" || "$args" == *"$lane/wingproof23.py shard $n" ]];do sleep 3;done
exec "$root/opt/venv/bin/python" -B "$lane/wingreplay23.py" "$n"
