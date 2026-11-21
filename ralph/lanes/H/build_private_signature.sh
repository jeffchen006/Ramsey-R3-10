#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
cd "$root/lean"
export PATH="$HOME/.elan/bin:$PATH" LEAN_NUM_THREADS=1 LEAN_STACK_SIZE_KB=8192
ulimit -v 16777216
exec /usr/bin/time -f 'wall=%e user=%U sys=%S maxrss_kib=%M exit=%x' timeout 240 nice -n 5 taskset -c "${H_CPU:-148}" prlimit --cpu=180 lake --packages="$root/scratch/H/packages-local.json" "$@"
