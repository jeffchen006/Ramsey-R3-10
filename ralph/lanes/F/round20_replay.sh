#!/bin/bash
set -euo pipefail
lane=$(cd "$(dirname "$0")" && pwd); root=$(cd "$lane/../../.." && pwd)
case "$PWD" in "$root"/scratch/F/*) ;; *) exit 2;; esac
test ! -e jobs.tsv; test ! -e pilot.rows
old=$root/scratch/F/r19; py=$root/opt/venv/bin/python
run() { bash "$lane/round19_step.sh" "$@"; }
ulimit -v 524288; ulimit -f 16384
export TMPDIR=$PWD PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
run hashes 5 bash -c 'cd "$1"; sha256sum -c ralph/lanes/F/ROUND19_FREEZE.sha256' bash "$root"
run build 12 g++ -O3 -std=c++20 -march=native "$lane/one_double.cpp" -o binary
run small 3 "$py" -B "$lane/one_double_pilot.py" small
for quotient in c*.q; do
  tag=${quotient%.q}; run "control_$tag" 2 ./binary "$quotient" 4 "$tag.bank" "$tag.rows" "$tag.trace" 8
done
run calibrate 10 "$py" -B "$lane/one_double_pilot.py" calibrate
run tamper 4 "$py" -B "$lane/one_double_pilot.py" tamper
run corrupt_pin 4 bash -c 'cd "$1"; "$2" -B "$3/one_double_pilot.py" adverse' bash "$old" "$py" "$lane"
cmp "$old/newcalib.stdout" calibrate.stdout; cmp "$old/newtamper.stdout" tamper.stdout; cmp "$old/mutation.stdout" corrupt_pin.stdout
for file in c*.trace c*.checked positive.g6 positive.gate; do cmp "$file" "$old/$file"; done
cp -- "$old/pilot.q" "$old/pilot.bank" .; cp -- "$old/unexamined.rows" pilot.rows
run preflight 5 "$py" -B "$lane/round20_census.py" preflight
run produce 35 ./binary pilot.q 10 pilot.bank pilot.rows pilot.trace 8
run verify 18 "$py" -B "$lane/one_double_check.py" pilot
run price 10 "$py" -B "$lane/round20_census.py" price
