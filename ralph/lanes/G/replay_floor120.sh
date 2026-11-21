#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
lane="$root/ralph/lanes/G"
certs="$lane/root_certs"
if (( $# != 2 )); then
    echo "usage: $0 fresh-work-directory existing-full-LRAT-directory" >&2
    exit 2
fi
proofs=$(realpath -- "$2")
mkdir -p -- "$1"
cd -- "$1"
ulimit -v 16777216
hard_cpu=$(ulimit -Ht)
if [[ $hard_cpu == unlimited || $hard_cpu -gt 90 ]]; then
    ulimit -t 90
fi
(cd "$certs" && sha256sum -c floor120_inputs.sha256)
nice -n 5 timeout 90s python3 -S -B "$lane/check_floor120.py" --catalogue "$certs/complete33_le119.g6"
nice -n 5 timeout 90s python3 -S -B "$lane/root_core.py" "$certs/complete33_le119.g6" .
for (( index=1; index<=74; index++ )); do
    printf -v name '%04d' "$index"
    ln -s -- "$proofs/$name.lrat" "$name.lrat"
done
sha256sum -c "$certs/floor120_dimacs_lrat.sha256"
for (( index=1; index<=74; index++ )); do
    printf -v name '%04d' "$index"
    nice -n 5 timeout 35s "$root/opt/bin/lrat-check" "$name.cnf" "$name.lrat" > "$name.verify"
    nice -n 5 timeout 35s "$root/opt/bin/cake_lpr" "$name.cnf" "$name.lrat" > "$name.cake"
    rg -q '^c VERIFIED$' "$name.verify"
    rg -q '^s VERIFIED UNSAT$' "$name.cake"
done
printf '74/74 verified by both LRAT checkers\n'
nice -n 5 timeout 90s python3 -S -B "$lane/check_floor120.py" | diff - "$certs/closed167.csv"
printf 'Pinned e167 Farkas rows verified\n'
nice -n 5 timeout 90s python3 -S -B "$lane/scan_root_floor.py" --verify --output "$lane/root_floor120_certs.jsonl"
