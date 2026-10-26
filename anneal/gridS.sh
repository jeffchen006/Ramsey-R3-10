#!/bin/bash
# sawtooth (Exoo 2013) tests: 4 configs per call on CPUs 72-75. usage: gridS.sh N TIME TAG "name|args" x4
cd ./anneal
N=$1; TIME=$2; TAG=$3; shift 3
i=0
for c in "$@"; do
 name=${c%%|*}; args=${c#*|}
 rm -f ../runs/anneal/grid/${TAG}_$name.log
 taskset -c $((72+i)) nice -n 5 ./ls -n $N -k 10 -maxdeg 9 -degcap 0 -w9 0 -focus 0.3 -bench -time $TIME $args -seed $((500+i)) -out ../runs/anneal/grid/${TAG}_$name > /dev/null &
 i=$((i+1))
done
wait
for c in "$@"; do name=${c%%|*}; f=../runs/anneal/grid/${TAG}_$name.log; echo "$name found=$(grep -c FOUND $f) $(grep END $f | cut -d' ' -f4-)"; done
