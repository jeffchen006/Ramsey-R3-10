#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
lane="$root/ralph/lanes/G"
if (( $# != 2 )); then
    echo "usage: $0 fresh-work-directory round4-producer-directory" >&2
    exit 2
fi
source=$(realpath -- "$2")
mkdir -p -- "$1"
cd -- "$1"
ulimit -v 16777216
hard_cpu=$(ulimit -Ht)
if [[ $hard_cpu == unlimited || $hard_cpu -gt 120 ]]; then ulimit -t 120; fi
(cd "$source" && sha256sum -c "$lane/root_certs/e120_partial.sha256")
nice -n 5 timeout 50s python3 -S -B "$root/tools/check_graph.py" --n 33 --k 9 "$source/strict120.s8.g6" > check120.log
[[ $(wc -l < "$source/strict120.s8.g6") == 1223 ]]
[[ $(nice -n 5 timeout 20s "$root/opt/bin/countg" -q --e -1 "$source/strict120.s8.g6") == '120 1223' ]]
[[ $(nice -n 5 timeout 20s "$root/opt/bin/labelg" -q -S "$source/strict120.s8.g6" | sort -u | wc -l) == 1223 ]]
nice -n 5 timeout 40s python3 -S -B "$lane/verify_uncovered.py" "$source/strict120.s8.g6" "$source/s8.e120.cliq.tsv" \
    --degree 6 --unproved "$source/s8.e120.exception.tsv"
cut -f2 "$source/s8.e120.exception.tsv" | diff - "$source/s8.e120.exception.g6"
[[ $(wc -l < "$source/s8.e120.exception.g6") == 66 ]]
nice -n 5 timeout 80s python3 -S -B "$lane/root_core.py" "$source/s8.e120.exception.g6" .
for (( index=1; index<=66; ++index )); do
    printf -v name '%04d' "$index"
    cmp "$name.cnf" "$source/s8_e120_core/$name.cnf"
    proof="$source/s8_e120_core/$name.lrat"
    nice -n 5 timeout 35s "$root/opt/bin/lrat-check" "$name.cnf" "$proof" > "$name.verify"
    nice -n 5 timeout 35s "$root/opt/bin/cake_lpr" "$name.cnf" "$proof" > "$name.cake"
    rg -q '^c VERIFIED$' "$name.verify"
    rg -q '^s VERIFIED UNSAT$' "$name.cake"
done
printf '1223 supplied roots excluded (1157 cliques, 66 dual LRATs); no census claim by this script.\n'
