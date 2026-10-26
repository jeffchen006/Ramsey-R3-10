#!/bin/bash
# Build the Lean case-table modules of one tag with bounded parallelism and memory.
# Usage: scripts/build_tag.sh MOD P   (MOD e.g. GrMtf; P parallel lake builds, each <= 6 GB; use P <= 2 on CPUs 148-149)
set -u
cd ./lean
. ./env.sh
MOD=$1; P=$2
CAP="scripts/memcap.sh 6"
T="taskset -c 148-149 nice -n 5"
date; echo "== base"
$T lake build R310.LP.Cases 2>&1 | tail -1
echo "== batches"
ls R310/LP/Data/${MOD}T9*[0-9][0-9][0-9].lean | sed 's|/|.|g; s|\.lean$||' | \
  xargs -P $P -I{} sh -c "$CAP $T lake build {} > /dev/null 2>&1 && echo ok {} || echo FAIL {}"
echo "== joins"
for m in R310.LP.Data.${MOD}Surv R310.LP.Data.${MOD}Lpk $(ls R310/LP/Data/${MOD}T9*.lean | grep -v '[0-9][0-9][0-9].lean' | sed 's|/|.|g; s|\.lean$||'); do
  $CAP $T lake build $m > /dev/null 2>&1 && echo ok $m || echo FAIL $m
done
echo "== cases"
/usr/bin/time -f "%e s %M KB" scripts/memcap.sh 20 $T lake build R310.LP.Cases${MOD} 2>&1 | grep -v "module system\|^✔\|^trace\|^\s*\[" | tail -20
date
