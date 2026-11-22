#!/bin/bash
set -euo pipefail
lane=$(cd "$(dirname "$0")" && pwd); root=$(cd "$lane/../../.." && pwd)
case "$PWD" in "$root"/scratch/F/*) ;; *) exit 2;; esac
test ! -e jobs.tsv
py=$root/opt/venv/bin/python
run() { bash "$lane/round19_step.sh" "$@"; }
ulimit -v 524288; ulimit -f 16384
export TMPDIR=$PWD PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
run hashes 4 bash -c 'cd "$1"; sha256sum -c ralph/lanes/F/ROUND20_FREEZE.sha256' bash "$root"
run build 9 g++ -O3 -std=c++20 -march=native "$lane/two_double.cpp" -o binary
run small 3 "$py" -B "$lane/two_double_pilot.py" small
for tag in s{0..7} old pin; do run "control_$tag" 2 ./binary "$tag.q" 5 "$tag.bank" "$tag.rows" "$tag.trace" 8; done
run literal 5 "$py" -B "$lane/two_double_pilot.py" literal
run mutations 3 "$py" -B "$lane/two_double_pilot.py" mutations
run preflight 4 "$py" -B "$lane/two_double_pilot.py" preflight
run produce 6 ./binary pilot.q 10 pilot.bank pilot.rows pilot.trace 8
run verify 5 "$py" -B "$lane/two_double_pilot.py" verify
run price 5 "$py" -B "$lane/two_double_pilot.py" price
run geometry 2 "$py" -B "$lane/two_double_geometry.py"
