#!/bin/bash
# runjobs.sh JOBFILE OUT.jsonl TIMEOUT_SEC EXTRA_ARGS...  (16 parallel, pinned to symsat CPUs)
JOBS=$1; OUT=$2; TO=$3; shift 3
PY=./tools/venv/bin/python
cd ./symsat
cat "$JOBS" | xargs -P 16 -I{} bash -c "taskset -c 88-95,168-175 nice -n 5 timeout $TO $PY cyclic.py {} --tl $TO $* 2>/dev/null >> $OUT || echo '{\"job\": \"{}\", \"result\": \"KILLED\"}' >> $OUT"
