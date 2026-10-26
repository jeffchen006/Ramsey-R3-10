#!/bin/bash
# benchmark (CFG = current grid) on (3,K,N): solutions found in TIME s per config; CPUs 72-87
cd ./anneal
N=${1:-38}; K=${2:-10}; TIME=${3:-120}; TAG=${4:-g3}
B="-n $N -k $K -maxdeg $((K-1)) -bench -time $TIME"
CFG=(
 "T2|-degcap 0 -w9 0 -T0 2 -T1 0.2 -focus 0.3"
 "T3|-degcap 0 -w9 0 -T0 3 -T1 0.3 -focus 0.3"
 "T4|-degcap 0 -w9 0 -T0 4 -T1 0.4 -focus 0.3"
 "T6|-degcap 0 -w9 0 -T0 6 -T1 0.6 -focus 0.3"
 "T3_05|-degcap 0 -w9 0 -T0 3 -T1 0.5 -focus 0.3"
 "T3_1|-degcap 0 -w9 0 -T0 3 -T1 1 -focus 0.3"
 "T2_05|-degcap 0 -w9 0 -T0 2 -T1 0.5 -focus 0.3"
 "Tfix1|-degcap 0 -w9 0 -T0 1 -T1 1 -focus 0.3"
 "T3f0|-degcap 0 -w9 0 -T0 3 -T1 0.3 -focus 0"
 "T3f07|-degcap 0 -w9 0 -T0 3 -T1 0.3 -focus 0.7"
 "T3sw2M|-degcap 0 -w9 0 -T0 3 -T1 0.3 -focus 0.3 -sweep 2000000"
 "T3sw200k|-degcap 0 -w9 0 -T0 3 -T1 0.3 -focus 0.3 -sweep 200000"
 "T3cap|-w9 0 -T0 3 -T1 0.3 -focus 0.3"
 "T3wT64|-degcap 0 -wT 64 -w9 0 -T0 3 -T1 0.3 -focus 0.3"
 "T3wT128|-degcap 0 -wT 128 -w9 0 -T0 3 -T1 0.3 -focus 0.3"
 "T3rr|-degcap 0 -w9 0 -T0 3 -T1 0.3 -focus 0.3 -rr 1"
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
