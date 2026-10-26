#!/bin/bash
# usage: validate.sh CPU K N OPTS...   -> runs/satcore/val_K_N_<tag>.log
cpu=$1; k=$2; n=$3; shift 3
tag=$(echo "$*" | sed "s/--case.*//" | tr -cd "A-Za-z0-9" | cut -c1-80); [ -z "$tag" ] && tag=plain
log=./runs/satcore/val_${k}_${n}_${tag}.log
cd ./satcore
echo "cmd: bin/satcore -k $k -n $n $* ; start $(date -Is)" > $log
taskset -c $cpu nice -n 5 bin/satcore -k $k -n $n --out ./runs/satcore/found_${k}_${n}.g6 "$@" >> $log 2>&1; rc=$?
echo "end $(date -Is) rc=$rc" >> $log
