#!/bin/bash
# (3,10,39) calibration batch 2, CPUs 72-87
cd ./anneal
TIME=${1:-900}; TAG=${2:-c39b}
CFG=(
 "grow37|-grow 37 -leveltime 120 -T0 2 -T1 0.2 -vr 0.002"
 "grow37|-grow 37 -leveltime 120 -T0 2 -T1 0.2 -vr 0.002"
 "grow38|-grow 38 -leveltime 300 -T0 2 -T1 0.2 -focus 0.7"
 "grow38|-grow 38 -leveltime 300 -T0 2 -T1 0.2 -focus 0.7"
 "vr01f7|-T0 2 -T1 0.2 -focus 0.7 -vr 0.01"
 "vr01f7|-T0 2 -T1 0.2 -focus 0.7 -vr 0.01"
 "vr002|-T0 2 -T1 0.2 -vr 0.002"
 "vr002|-T0 2 -T1 0.2 -vr 0.002"
 "cap9|-degcap 9 -T0 2 -T1 0.2 -focus 0.7"
 "cap9|-degcap 9 -T0 2 -T1 0.2 -focus 0.7"
 "cap9vr|-degcap 9 -T0 2 -T1 0.2 -focus 0.7 -vr 0.01"
 "cap9vr|-degcap 9 -T0 2 -T1 0.2 -focus 0.7 -vr 0.01"
 "sym13|-sym 13 -T0 13 -T1 1.3 -sweep 50000"
 "sym13|-sym 13 -T0 13 -T1 1.3 -sweep 50000"
 "sym3|-sym 3 -T0 6 -T1 0.6 -sweep 200000"
 "sym3|-sym 3 -T0 6 -T1 0.6 -sweep 200000"
)
mkdir -p ../runs/anneal/calib
i=0
for c in "${CFG[@]}"; do
 name=${c%%|*}; args=${c#*|}
 taskset -c $((72+i)) nice -n 5 ./ls_v2 -n 39 -k 10 -maxdeg 9 -degcap 0 -w9 0 -focus 0.3 $args -bench -time $TIME -seed $((i+11)) -out ../runs/anneal/calib/${TAG}_${name}_$i > /dev/null &
 i=$((i+1))
done
wait
