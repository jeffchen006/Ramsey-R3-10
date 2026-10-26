#!/bin/bash
# Exploratory (3,10,40) runs. usage: n40.sh CPU NAME SECONDS OPTS...
cpu=$1; name=$2; secs=$3; shift 3
R=.
log=$R/runs/satcore/n40_$name.log
cd $R/satcore
echo "cmd: bin/satcore -n 40 -k 10 $* --time $secs ; cpu $cpu ; start $(date -Is) ; pid $$" > $log
taskset -c $cpu nice -n 5 bin/satcore -n 40 -k 10 "$@" --time $secs --report 600 --out $R/runs/satcore/found_10_40.g6 >> $log 2>&1; rc=$?
echo "end $(date -Is) rc=$rc" >> $log
