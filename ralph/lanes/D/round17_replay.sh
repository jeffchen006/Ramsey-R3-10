#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname "$0")/../../.." && pwd); src=$root/ralph/lanes/D; data=$root/scratch/D/middle17
dest=$(realpath -m "${1:?give a fresh scratch destination}"); mode=${2:-audit}; [[ $mode =~ ^(audit|sample|full)$ ]]
mkdir -p "$dest"; cd "$dest"; ulimit -v 16777216
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 TMPDIR=$dest
run(){ nice -n 5 timeout 180 prlimit --cpu=160:161 -- "$root/opt/venv/bin/python" -B "$@"; }
run "$src/middle16_cnf.py" >plants.log
run "$src/middle16_roster.py" "$dest" >roster.log; cmp roster.jsonl "$data/roster.jsonl"
run "$src/middle17_coverage.py" "$data/frozen" >coverage.log
run "$src/middle17_reconcile.py" "$data" "$dest" --full >reconciled.log
if [[ $mode != audit ]]; then
    for phase in checkpoint rest; do
        for worker in 0 1 2 3; do
            packs=("$data/$phase-$worker"/batch*.zip)
            if [[ $mode = sample ]]; then packs=("${packs[0]}"); fi
            for pack in "${packs[@]}"; do
                name=$(basename "$pack" .zip); offset=${name#batch}; unit=$dest/$phase-$worker; mkdir -p "$unit"
                run "$src/middle17_recheck.py" "$pack" "$phase" "$worker" "$((10#$offset))" "$unit"
                cut_from='.ok'; test -s "$unit/$name$cut_from"
            done
        done
    done
fi
cat plants.log coverage.log reconciled.log
