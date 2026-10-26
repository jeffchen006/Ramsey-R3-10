#!/bin/bash
# param grid on (3,9,34): 16 configs, one per CPU 72-87
cd ./anneal
i=0
for w9 in 0 1; do for TT in "4 0.5" "1 0.1" "0.3 0.03" "0.1 0.01"; do for fo in 0 0.5; do
 set -- $TT
 cpu=$((72+i)); tag=g1_w${w9}_T$1_f$fo
 taskset -c $cpu nice -n 5 ./ls -n 34 -k 9 -maxdeg 8 -seed $((100+i)) -w9 $w9 -T0 $1 -T1 $2 -focus $fo -time 120 -sweep 500000 -keepgoing -out ../runs/anneal/grid/$tag > /dev/null &
 i=$((i+1))
done; done; done
wait
