#!/bin/bash
# (3,10,39) calibration: 4 configs x 4 seeds, CPUs 72-87
cd ./anneal
BIN=${BIN:-./ls_v1}; TIME=${1:-900}; TAG=${2:-c39}
CFG=("T2|-T0 2 -T1 0.2" "Tfix1|-T0 1 -T1 1" "T2_05|-T0 2 -T1 0.5" "T3f07|-T0 3 -T1 0.3 -focus 0.7")
mkdir -p ../runs/anneal/calib
i=0
for c in "${CFG[@]}"; do for s in 1 2 3 4; do
 name=${c%%|*}; args=${c#*|}
 taskset -c $((72+i)) nice -n 5 $BIN -n 39 -k 10 -maxdeg 9 -degcap 0 -w9 0 -focus 0.3 $args -bench -time $TIME -seed $s -out ../runs/anneal/calib/${TAG}_${name}_s$s > /dev/null &
 i=$((i+1))
done; done
wait
