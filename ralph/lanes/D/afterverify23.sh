#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd); lane="$root/ralph/lanes/D"; n=$1; parent=$(awk -v n="$n" '$1==n{print $2}' "$root/scratch/D/c6r23/wing/verify/pids.tsv")
while args=$(ps -o args= -p "$parent") && [[ "$args" == *"$lane/afterwing23.sh $n" || "$args" == *"$lane/wingreplay23.py $n" ]];do sleep 3;done
exec "$root/opt/venv/bin/python" -B "$lane/wingproof23.py" squarefree18 "$n"
