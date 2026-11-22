#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
destination=$(realpath -m "${1:?supply your own writable scratch directory}")
mkdir -p "$destination";cd "$destination"
export TMPDIR=$destination PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 16777216
src=$root/ralph/lanes/D; data=$root/scratch/D/book14; python=$root/opt/venv/bin/python
run(){ nice -n 5 timeout 240 prlimit --cpu=190:191 "$@"; }
run g++ -std=c++17 -O3 -mpopcnt "$src/wing_orbits.cpp" -o ./orbit-check
run ./orbit-check 4 "$data/wing8.scan" <"$data/wing8.g6" >orbit.tsv 2>orbit.log
cmp orbit.tsv "$data/orbit.tsv"
run "$python" -B "$src/wing_replay.py" 12 >sparse.log
run "$python" -B "$src/half_bind.py" >half-bind.log
run "$python" -B "$src/wing_replay.py" half >half-duals.log
run "$python" -B "$src/plateau_audit.py" >plateau.log
run "$python" -B "$src/book14_receipts.py" --readonly >panel.log
run "$python" -B "$src/book14_rebuild.py" "$destination" >cnf-binding.log
while read -r filename digest; do
    echo "$digest  $filename" | sha256sum --check
    tag=${filename%.cnf}
    for checker in cake_lpr lrat-check; do run "$root/opt/bin/$checker" "$filename" "$data/$tag.lrat" >"$tag.$checker.log";rg -q VERIFIED "$tag.$checker.log";done
done <cnf-binding.log
cat orbit.log sparse.log half-bind.log half-duals.log plateau.log panel.log
