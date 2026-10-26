#!/bin/bash
# benchmark (CFG = current grid) on (3,K,N): solutions found in TIME s per config; CPUs 72-87
cd ./anneal
N=${1:-38}; K=${2:-10}; TIME=${3:-120}; TAG=${4:-g3}
B="-n $N -k $K -maxdeg $((K-1)) -bench -time $TIME"
CFG=(
 "T2a|-degcap 0 -w9 0 -T0 2 -T1 0.2 -focus 0.3"
 "T2b|-degcap 0 -w9 0 -T0 2 -T1 0.2 -focus 0.3"
 "vr0005a|-degcap 0 -w9 0 -T0 2 -T1 0.2 -focus 0.3 -vr 0.0005"
 "vr0005b|-degcap 0 -w9 0 -T0 2 -T1 0.2 -focus 0.3 -vr 0.0005"
 "vr002a|-degcap 0 -w9 0 -T0 2 -T1 0.2 -focus 0.3 -vr 0.002"
 "vr002b|-degcap 0 -w9 0 -T0 2 -T1 0.2 -focus 0.3 -vr 0.002"
 "vr01a|-degcap 0 -w9 0 -T0 2 -T1 0.2 -focus 0.3 -vr 0.01"
 "vr01b|-degcap 0 -w9 0 -T0 2 -T1 0.2 -focus 0.3 -vr 0.01"
 "vr05a|-degcap 0 -w9 0 -T0 2 -T1 0.2 -focus 0.3 -vr 0.05"
 "vr05b|-degcap 0 -w9 0 -T0 2 -T1 0.2 -focus 0.3 -vr 0.05"
 "vr002s1a|-degcap 0 -w9 0 -T0 2 -T1 0.2 -focus 0.3 -vr 0.002 -vrslack 1"
 "vr002s1b|-degcap 0 -w9 0 -T0 2 -T1 0.2 -focus 0.3 -vr 0.002 -vrslack 1"
 "vr01T1a|-degcap 0 -w9 0 -T0 1 -T1 0.1 -focus 0.3 -vr 0.01"
 "vr01T1b|-degcap 0 -w9 0 -T0 1 -T1 0.1 -focus 0.3 -vr 0.01"
 "vr01f0a|-degcap 0 -w9 0 -T0 2 -T1 0.2 -focus 0 -vr 0.01"
 "vr01f0b|-degcap 0 -w9 0 -T0 2 -T1 0.2 -focus 0 -vr 0.01"
)
mkdir -p ../runs/anneal/grid
i=0
for c in "${CFG[@]}"; do
 name=${c%%|*}; args=${c#*|}
 rm -f ../runs/anneal/grid/${TAG}_$name.log
 taskset -c $((72+i)) nice -n 5 ./ls $B $args -seed $((300+i)) -out ../runs/anneal/grid/${TAG}_$name > /dev/null &
 i=$((i+1))
done
wait
for c in "${CFG[@]}"; do name=${c%%|*}; f=../runs/anneal/grid/${TAG}_$name.log; echo "$name found=$(grep -c FOUND $f) $(grep END $f | cut -d' ' -f4-)"; done
