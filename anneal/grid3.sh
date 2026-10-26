#!/bin/bash
# benchmark on (3,K,N): solutions found in TIME s per config; CPUs 72-87
cd ./anneal
N=${1:-38}; K=${2:-10}; TIME=${3:-120}; TAG=${4:-g3}
B="-n $N -k $K -maxdeg $((K-1)) -bench -time $TIME"
CFG=(
 "base|-degcap 0 -w9 0 -T0 1 -T1 0.1 -focus 0.3"
 "w9|-degcap 0 -w9 1 -T0 1 -T1 0.1 -focus 0.3"
 "T2|-degcap 0 -w9 0 -T0 2 -T1 0.2 -focus 0.3"
 "T05|-degcap 0 -w9 0 -T0 0.5 -T1 0.05 -focus 0.3"
 "Tfix03|-degcap 0 -w9 0 -T0 0.3 -T1 0.3 -focus 0.3"
 "f0|-degcap 0 -w9 0 -T0 1 -T1 0.1 -focus 0"
 "f07|-degcap 0 -w9 0 -T0 1 -T1 0.1 -focus 0.7"
 "sw2M|-degcap 0 -w9 0 -T0 1 -T1 0.1 -focus 0.3 -sweep 2000000"
 "sw100k|-degcap 0 -w9 0 -T0 1 -T1 0.1 -focus 0.3 -sweep 100000"
 "cap|-w9 0 -T0 1 -T1 0.1 -focus 0.3"
 "wD32|-degcap 0 -wD 32 -w9 0 -T0 1 -T1 0.1 -focus 0.3"
 "wT64|-degcap 0 -wT 64 -w9 0 -T0 1 -T1 0.1 -focus 0.3"
 "wT16|-degcap 0 -wT 16 -w9 0 -T0 1 -T1 0.1 -focus 0.3"
 "tabu|-method tabu -degcap 0 -w9 0 -tabusample 200"
 "tabu50|-method tabu -degcap 0 -w9 0 -tabusample 50"
 "rr|-degcap 0 -w9 0 -T0 1 -T1 0.1 -focus 0.3 -rr 1"
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
