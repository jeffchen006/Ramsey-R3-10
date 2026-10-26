#!/bin/bash
# runjobs2.sh JOBFILE OUT.jsonl TIMEOUT_SEC NPAR EXTRA_ARGS...  (pinned to symsat CPUs)
JOBS=$1; OUT=$2; TO=$3; NP=$4; shift 4
PY=./tools/venv/bin/python
cd ./symsat
cat "$JOBS" | xargs -P $NP -I{} bash -c "taskset -c 88-95,168-175 nice -n 5 timeout $((TO+120)) $PY cyclic.py {} --tl $TO $* 2>/dev/null >> $OUT || echo '{\"job\": \"{}\", \"result\": \"KILLED\"}' >> $OUT"
