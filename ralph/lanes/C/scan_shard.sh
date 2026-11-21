#!/bin/bash
set -euo pipefail
ulimit -v 16777216
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
root=$(cd "$(dirname "$0")/../../.." && pwd)
part=$1
shift
script="$root/ralph/lanes/C/kernel_projection.py"
/usr/bin/time -f 'scan cpu user=%U sys=%S wall=%e maxrss=%M' python3 -B -u "$script" scan "$@" < "$part.g6" > "$part.jsonl"
/usr/bin/time -f 'verify cpu user=%U sys=%S wall=%e maxrss=%M' python3 -B -u "$script" verify "$@" < "$part.jsonl"
