#!/bin/bash
# ladder: time to solution vs n (baseline SA), CPUs 72-87
cd ./anneal
mkdir -p ../runs/anneal/ladder
i=0
for kn in "9 30" "9 31" "9 32" "9 33" "10 34" "10 35" "10 36" "10 37"; do for s in 1 2; do
 set -- $kn
 taskset -c $((72+i)) nice -n 5 ./ls -k $1 -n $2 -maxdeg $(($1-1)) -degcap 0 -w9 0 -T0 1 -T1 0.1 -focus 0.3 -seed $s -time 120 -sweep 500000 -out ../runs/anneal/ladder/L_k$1_n$2_s$s > /dev/null &
 i=$((i+1))
done; done
wait
