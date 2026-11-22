#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "$0")/../../.." && pwd)
lane="$root/ralph/lanes/A"
stage=${1:-r20-review}
mode=${2:-all}
[[ "$stage" =~ ^r20[-A-Za-z0-9_]*$ ]]
[[ "$mode" == pilot || "$mode" == finish || "$mode" == all ]]
mkdir -p "$root/scratch/A/$stage"
cd "$root/scratch/A/$stage"
ulimit -v 1048576
ulimit -f 16384
export TMPDIR=$PWD LC_ALL=C

timed() {
    local label=$1
    shift
    /usr/bin/time -o "$label.time" -f '%U %S %e %M' nice -n 5 timeout 60s prlimit --cpu=45 -- "$@"
}

driver="$lane/audit_d5_20.py"
if [[ "$mode" != finish ]]; then
    timed compile c++ -std=c++20 -O3 -Wall -Wextra -Werror "$lane/expand_d5_20.cc" -o expand
    timed small python3 -B "$driver" small expand >small.log
    timed prepare python3 -B "$driver" prepare >prepare.log
    timed pilot-expand ./expand 8 5 5 8 0 130 <pilot.in.tsv >pilot.raw.tsv 2>pilot.receipt.tsv
    timed pilot-compare python3 -B "$driver" pilot >pilot.log 2>&1
fi

if [[ "$mode" != pilot ]]; then
    timed tail-expand ./expand 8 5 5 8 0 130 <tail.in.tsv >tail.raw.tsv 2>tail.receipt.tsv
    sort -s -n -k1,1 pilot.in.tsv tail.in.tsv >bound-partition.tsv
    cmp bound-partition.tsv all.in.tsv
    sort -s -n -k1,1 pilot.raw.tsv tail.raw.tsv >all.raw.tsv
    {
        head -1 pilot.receipt.tsv
        { tail -n +2 pilot.receipt.tsv; tail -n +2 tail.receipt.tsv; } | sort -s -n -k1,1
    } >all.receipt.tsv
    timed all-compare python3 -B "$driver" all >all.log 2>&1
    cmp all.classes.g6 "$root/scratch/G/round5/d5/full_e130.can.g6"
fi
