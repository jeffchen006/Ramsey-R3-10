#!/bin/bash
set -euo pipefail
prior=$1; task=$2; lane=$(cd "$(dirname "$0")" && pwd); root=$(cd "$lane/../../.." && pwd); py=$root/opt/venv/bin/python
while [[ -e /proc/$prior ]]; do sleep 2; done
export TMPDIR=$PWD PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
echo "$(date -Is) prior lease returned $prior; taking $task"
case $task in
 bank) "$py" -B "$lane/chart_bank24.py" >bank.stdout; "$py" -B "$lane/chart_ctl24.py" >control.stdout; "$py" -B "$lane/global24.py" pilot pilot.tsv >pilot.stdout;;
 fixed) "$py" -B "$lane/cards24.py" control >control.stdout && "$py" -B "$lane/cards24.py" inventory >inventory.stdout && "$py" -B "$lane/cards24.py" wave pilot.tsv 100000 45 >pilot.jsonl;;
 near) "$py" -B "$lane/near24.py" 100000 240032 >pilot.stdout;;
 shape) "$py" -B "$lane/source24.py" control >control.stdout; "$py" -B "$lane/source24.py" plan pilot >planpilot.stdout; "$py" -B "$lane/source24.py" wave pilot.tsv 250000 >pilot.jsonl;;
esac
