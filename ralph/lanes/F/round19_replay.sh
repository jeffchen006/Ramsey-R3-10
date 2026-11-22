#!/bin/bash
set -eu
lane=$(cd "$(dirname "$0")" && pwd); root=$(cd "$lane/../../.." && pwd);original=$root/scratch/F/r19
case "$PWD" in "$root"/scratch/F/*) ;; *) exit 2;; esac
test -z "$(ls -A .)" || exit 2
ulimit -v 524288
run(){ nice -n 5 timeout 30 prlimit --cpu=20 -- "$@"; }
py(){ run "$root/opt/venv/bin/python" -B "$lane/one_double_pilot.py" "$@"; }
run g++ -std=c++20 -O3 -march=native "$lane/one_double.cpp" -o binary
py small
for quotient in c*.q; do tag=${quotient%.q};run ./binary "$quotient" 4 "$tag.bank" "$tag.rows" "$tag.trace" 8 > "$tag.out"; done
py calibrate;py tamper;py pilot > freeze.stdout;cmp freeze.stdout "$original/freeze.stdout"
run ./binary pilot.q 10 pilot.bank pilot.rows pilot.trace 8 > pilotrun.stdout
run "$root/opt/venv/bin/python" -B "$lane/one_double_check.py" pilot
py adverse;py price > price.out;cmp price.out "$original/detailprice.stdout"
files=0
for file in *.trace *.checked *.bank *.rows *.q *.tsv *.left *.g6 *.gate;do cmp "$file" "$original/$file";files=$((files+1));done
echo "$files deterministic control, pilot, receipt and price files matched; freeze and detailed price logs matched too."
