#!/bin/bash
# (3,10,39) calibration batch 3 (VR variants), CPUs 72-87
cd ./anneal
TIME=${1:-900}; TAG=${2:-c39b}
CFG=(
 "vr002|-T0 2 -T1 0.2 -vr 0.002"
 "vr002|-T0 2 -T1 0.2 -vr 0.002"
 "vr002|-T0 2 -T1 0.2 -vr 0.002"
 "vr002|-T0 2 -T1 0.2 -vr 0.002"
 "vr005|-T0 2 -T1 0.2 -vr 0.005"
 "vr005|-T0 2 -T1 0.2 -vr 0.005"
 "vr005|-T0 2 -T1 0.2 -vr 0.005"
 "vr001|-T0 2 -T1 0.2 -vr 0.001"
 "vr001|-T0 2 -T1 0.2 -vr 0.001"
 "vr001|-T0 2 -T1 0.2 -vr 0.001"
 "vr002s1|-T0 2 -T1 0.2 -vr 0.002 -vrslack 1"
 "vr002s1|-T0 2 -T1 0.2 -vr 0.002 -vrslack 1"
 "vr002e170|-T0 2 -T1 0.2 -vr 0.002 -wX 16 -emax 170"
 "vr002e170|-T0 2 -T1 0.2 -vr 0.002 -wX 16 -emax 170"
 "vr002T15|-T0 1.5 -T1 0.3 -vr 0.002"
 "vr002T15|-T0 1.5 -T1 0.3 -vr 0.002"
)
mkdir -p ../runs/anneal/calib
i=0
for c in "${CFG[@]}"; do
 name=${c%%|*}; args=${c#*|}
 taskset -c $((72+i)) nice -n 5 ./ls_v3 -n 39 -k 10 -maxdeg 9 -degcap 0 -w9 0 -focus 0.3 $args -bench -time $TIME -seed $((i+11)) -out ../runs/anneal/calib/${TAG}_${name}_$i > /dev/null &
 i=$((i+1))
done
wait
