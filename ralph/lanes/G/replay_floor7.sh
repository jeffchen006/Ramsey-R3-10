#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
lane="$root/ralph/lanes/G"
if (( $# != 2 )); then
    echo "usage: $0 fresh-work-directory producer-data-directory" >&2
    exit 2
fi
source=$(realpath -- "$2")
mkdir -p -- "$1"
cd -- "$1"
ulimit -v 16777216
hard_cpu=$(ulimit -Ht)
if [[ $hard_cpu == unlimited || $hard_cpu -gt 90 ]]; then
    ulimit -t 90
fi
(cd "$source" && sha256sum -c "$lane/root_certs/floor7_inputs.sha256")
cmp "$lane/root_certs/canon32_e104.g6" "$source/canon32_e104.g6"
for level in 104 105 106; do
    input="$source/e$level.add.g6"
    parent=()
    case "$level" in
        104) input="$source/canon32_e104.g6" ;;
        105) parent=(--parent "$source/canon32_e104.g6") ;;
        106) parent=(--parent "$source/e105.add.g6") ;;
    esac
    nice -n 5 timeout 90s python3 -S -B "$lane/verify_uncovered.py" "$input" "$source/e$level.cliq.tsv" \
        --degree 7 --unproved "$source/e$level.unproved.tsv" --published-edges "$level" "${parent[@]}"
done
test ! -s "$source/e104.unproved.tsv"
cut -f2 "$source/e105.unproved.tsv" | diff - "$source/e105.exception.g6"
cut -f2 "$source/e106.unproved.tsv" | diff - <(cat "$source"/e106.exception.part.0?)
recheck_group() (
    input=$1
    proofdir=$2
    total=$3
    mkdir -- "$proofdir"
    cd -- "$proofdir"
    actual=$(wc -l < "$source/$input")
    (( actual == total ))
    nice -n 5 timeout 90s python3 -S -B "$lane/root_core.py" "$source/$input" . --root 7
    for (( index=1; index<=total; index++ )); do
        printf -v name '%04d' "$index"
        cmp "$name.cnf" "$source/$proofdir/$name.cnf"
        proof="$source/$proofdir/$name.lrat"
        nice -n 5 timeout 35s "$root/opt/bin/lrat-check" "$name.cnf" "$proof" > "$name.verify"
        nice -n 5 timeout 35s "$root/opt/bin/cake_lpr" "$name.cnf" "$proof" > "$name.cake"
        rg -q '^c VERIFIED$' "$name.verify"
        rg -q '^s VERIFIED UNSAT$' "$name.cake"
    done
    printf '%s: %s checked LRAT exceptions\n' "$proofdir" "$total"
)
recheck_group e105.exception.g6 e105_exception_core 1
recheck_group e106.exception.part.00 e106_exception_core.00 23
recheck_group e106.exception.part.01 e106_exception_core.01 22
recheck_group e106.exception.part.02 e106_exception_core.02 22
printf 'Verified floor107: 19521 checked clique witnesses and 68 checked LRATs\n'
