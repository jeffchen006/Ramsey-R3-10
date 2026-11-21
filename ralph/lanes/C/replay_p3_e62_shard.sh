#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
shard=${1:?supply shard 0..3 from scratch/C}
lane=../../ralph/lanes/C
py=../../opt/venv/bin/python
producer="p3e62-full-$shard.log"
while read -r row; do
    terminal=""
    while [[ -z "$terminal" ]]; do
        terminal=$(rg -m 1 "^TERMINAL $row fixed " "$producer" || :)
        if [[ -z "$terminal" ]]; then sleep 12; fi
    done
    expected=44
    if [[ "$row" == 17 || "$row" == 118 ]]; then expected=38; fi
    if [[ "$terminal" != "TERMINAL $row fixed {'checked': $expected} CPU-s "* ]]; then
        printf 'REPLAY-SKIP %s %s\n' "$row" "$terminal"
        continue
    fi
    "$py" -B "$lane/p3_low_trials.py" ../../gluing/val/r3_7_22.g6 p3-boundary-levels.log \
        ../../opt/bin p3low-pilot --row "$row" --mode fixed --verify
done < <(awk -v block="$shard" '(NR-1)%4==block' p3e62-residues.txt)
