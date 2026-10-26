#!/bin/bash
# Run MathCheckRamsey (commit 84b2aefc, copy in runs/satcore/mathcheck_<copy>) with a time limit.
# usage: mathcheck.sh CPU COPY SECONDS MAIN_ARGS...   log: runs/satcore/mc_<COPY>_<args>.log
cpu=$1; copy=$2; secs=$3; shift 3
R=.
tag=$(echo "$*" | tr -cd "A-Za-z0-9_" | cut -c1-60)
log=$R/runs/satcore/mc_${copy}_${tag}.log
cd $R/runs/satcore/mathcheck_$copy
export PATH=$R/runs/satcore/pybin:$PATH
echo "cmd: ./main.sh $* ; cpu $cpu ; limit $secs ; start $(date -Is)" > $log
t0=$(date +%s.%N)
timeout $secs taskset -c $cpu nice -n 5 ./main.sh "$@" >> $log 2>&1; rc=$?
t1=$(date +%s.%N)
echo "end $(date -Is) rc=$rc wall=$(echo "$t1 - $t0" | bc) s" >> $log
