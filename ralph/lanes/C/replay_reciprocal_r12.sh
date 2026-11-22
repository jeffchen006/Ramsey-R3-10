#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
lane="$root/ralph/lanes/C"
archive="$root/scratch/C/r12"
source22="$root/gluing/val/r3_7_22.g6"
python="$root/opt/venv/bin/python"
export LC_ALL=C OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mode=${1:-verify}
ulimit -v 16777216
ulimit -c 0
cd "$archive"
sha256sum -c "$lane/ROUND12_REPLAY.sha256"
case "$mode" in
verify)
    g++ -std=c++20 -O3 "$lane/reciprocal_r12_tight_check.cpp" -o tight_replay
    nice -n 5 timeout 30 prlimit --cpu=20:25 ./tight_replay "$source22" independent.replay.tight
    cmp independent.tight independent.replay.tight
    cmp <(sort independent.replay.tight) <(sort census.tight)
    nice -n 5 timeout 100 prlimit --cpu=55:60 "$python" -B "$lane/reciprocal_r12_ledger.py" \
        projection-dense independent.replay.tight recheck
    ;;
census)
    g++ -std=c++20 -O3 "$lane/reciprocal_r12_census.cpp" -o census_replay
    nice -n 5 timeout 60 ./census_replay control ../r11/cal-10.g6 ../r11/cal-planted.tsv
    nice -n 5 timeout 240 prlimit --cpu=150:155 ./census_replay target "$source22" replay
    cmp census.hist replay.hist
    cmp census.hosts replay.hosts
    cmp census.tight replay.tight
    cmp ../r10/fixed22.tsv replay.old
    ;;
*) exit 2 ;;
esac
