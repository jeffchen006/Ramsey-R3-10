#!/bin/bash
set -euo pipefail
lane=$(cd "$(dirname "$0")" && pwd); root=$(cd "$lane/../../.." && pwd)
test "$PWD" = "$root/scratch/F/r23"; tag=$1; shift
for slot in "$@"; do
  (ulimit -v 1048576; ulimit -f 16384; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1; exec setsid nohup nice -n 5 timeout 21300 prlimit --cpu=20800:20900 -- "$root/opt/venv/bin/python" -B "$lane/six_queue.py" worker "$tag" "$slot") >"$tag$slot.log" 2>&1 </dev/null & parent=$!
  sleep .08; child=$(ps --ppid "$parent" -o pid= | xargs); test -n "$child"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t1\t%s%s.log\n' "$tag" "$slot" "$parent" "$child" "$(date -Is)" "$(date -d '+21300 second' -Is)" "$tag" "$slot" >>dispatch.tsv
  printf '\n- Active: %s slot %s, worker %s (timeout %s), one core, `six_queue.py worker %s %s`, `scratch/F/r23/%s%s.log`, start %s, hard end %s.\n' "$tag" "$slot" "$child" "$parent" "$tag" "$slot" "$tag" "$slot" "$(date -Is)" "$(date -d '+21300 second' -Is)" >> "$lane/STATE.md"
done
