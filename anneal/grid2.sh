#!/bin/bash
# (3,9,34): degree handling x temperature, 60 s each, CPUs 72-87
cd ./anneal
i=0
for dc in "0 0" "0 64" "0 256" "0 2048"; do for TT in "1 0.1" "0.3 0.03"; do for w9 in 0 1; do
 set -- $dc $TT
 cpu=$((72+i)); tag=g2_wD$2_T$3_w$w9
 taskset -c $cpu nice -n 5 ./ls -n 34 -k 9 -maxdeg 8 -degcap $1 -wD $2 -seed $((200+i)) -w9 $w9 -T0 $3 -T1 $4 -focus 0.3 -time 60 -sweep 500000 -keepgoing -out ../runs/anneal/grid/$tag > /dev/null &
 i=$((i+1))
done; done; done
wait
