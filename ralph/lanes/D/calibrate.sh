#!/bin/bash
# Run from a scratch directory. USAGE: calibrate.sh N OUT EXPECTED_G6 TOTAL_KERNELS
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
vertices=$1 out=$2 expected=$3 count=$4
awk -F '\t' -v expect="$count" 'NR>1 && ($2 != "DONE" || $1<0 || $1>=expect || seen[$1]++) {++incomplete} END {exit (incomplete || NR != expect+1)}' "$out/results.tsv"
shopt -s nullglob
solutions=("$out"/*.sol)
if ((${#solutions[@]})); then
    cat "${solutions[@]}" | python3 -B "$root/sms/edges2g6.py" "$vertices" > "$out/models.g6"
else
    : > "$out/models.g6"
fi
export TMPDIR="$PWD"
"$root/opt/bin/labelg" -q < "$out/models.g6" | LC_ALL=C sort -u > "$out/canonical.g6"
"$root/opt/bin/labelg" -q < "$expected" | LC_ALL=C sort -u > "$out/expected.g6"
diff -u "$out/expected.g6" "$out/canonical.g6"
printf 'PASS %s: %d canonically distinct graph(s)\n' "$out" "$(wc -l < "$out/canonical.g6")"
