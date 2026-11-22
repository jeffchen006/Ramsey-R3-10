#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname "$0")/../../.." && pwd); src=$root/ralph/lanes/D; data=$root/scratch/D/middle16
dest=$(realpath -m "${1:?give a writable scratch destination}"); mkdir -p "$dest";cd "$dest"; ulimit -v 16777216
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 TMPDIR=$dest
run(){ nice -n 5 timeout 480 prlimit --cpu=450:451 "$root/opt/venv/bin/python" -B "$@"; }
run "$src/middle16_roster.py" "$dest" >roster.log
for name in roster.jsonl prior.jsonl pilot.jsonl;do cmp "$name" "$data/$name";done
run "$src/middle16_cnf.py" >cal.log
run "$src/middle16_audit.py" holdout >holdout.log
run "$src/middle16_price.py" "$dest/archives" pilot.jsonl "$data/primary" >replay.jsonl
run "$src/middle16_audit.py" "$data" "$dest" >summary.log; cat cal.log holdout.log summary.log
