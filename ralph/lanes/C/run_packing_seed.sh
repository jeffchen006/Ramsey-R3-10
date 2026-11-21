#!/bin/bash
set -euo pipefail
ulimit -v 16777216
root=$(cd "$(dirname "$0")/../../.." && pwd)
index=$1
/usr/bin/time -f 'generate cpu user=%U sys=%S wall=%e maxrss=%M' \
    python3 -B -u "$root/ralph/lanes/C/pair_packages.py" scan R7_X.g6 --index "$index" --out R7_full
/usr/bin/time -f 'pack cpu user=%U sys=%S wall=%e maxrss=%M' \
    ./colour_packing 1000000 < "R7_full.$index.txt" > "R7_full.$index.results"
records=$(( $(wc -l < "R7_full.$index.txt") - 2 ))
results=$(wc -l < "R7_full.$index.results")
test "$records" -eq "$results"
printf 'complete %s of %s package pairs\n' "$results" "$records"
awk '{ cnt[$1]++; nodes += $2; if ($2 > max) max=$2 } END {
    for (status in cnt) print status, cnt[status]; print "nodes",nodes,"max",max
}' "R7_full.$index.results"
