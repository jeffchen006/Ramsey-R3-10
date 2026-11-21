#!/bin/bash
set -euo pipefail
ulimit -v 16777216
index=$1
/usr/bin/time -f 'trace cpu user=%U sys=%S wall=%e maxrss=%M' \
    ./colour_packing_trace 1000000 trace "R7_trace.$index.tmp" \
    < "R7_full.$index.txt" > "R7_trace.$index.results"
cmp "R7_full.$index.results" "R7_trace.$index.results"
nodes=$(awk '$1 != "no-extension" {bad=1} { nodes += $2 } END {if (bad) exit 1; print nodes}' "R7_trace.$index.results")
test "$(wc -c < "R7_trace.$index.tmp")" -eq "$((nodes+8))"
mv "R7_trace.$index.tmp" "R7_trace.$index.bin"
sha256sum "R7_trace.$index.bin"
