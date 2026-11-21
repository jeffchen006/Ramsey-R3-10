#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

directory=work/e162_r5
source=../G/round3/e107.partial.g6
mkdir -p "$directory"
cp "$source" "$directory/e107.in.g6"
sha256sum "$directory/e107.in.g6" build/mtfcover_r5
/usr/bin/time -f 'validity CPU %U+%S wall %e' timeout 5m \
    build/audit_duals 32 107 9 234352 < "$directory/e107.in.g6"
/usr/bin/time -f 'canonical CPU %U+%S wall %e' timeout 5m \
    ../../opt/bin/shortg -q -T"$directory" "$directory/e107.in.g6" "$directory/e107.canon.g6"
cmp "$directory/e107.in.g6" "$directory/e107.canon.g6"
/usr/bin/time -f 'gluing CPU %U+%S wall %e' timeout 6m \
    build/mtfcover_r5 -X -k 9 -d 7 -m 7 -M 9 -E 162 -e 162 \
    -s 7888888 -p 0,0,0,0,0,0,0,2,32,6 < "$directory/e107.in.g6" > "$directory/completions.g6"
printf 'e162 adjacent-seven pinned scan: 234352 supplied roots; raw output %s\n' "$(wc -l < "$directory/completions.g6")"
if [[ -s "$directory/completions.g6" ]]; then
    cp "$directory/completions.g6" ../../ralph/found/B_e162_d7.g6
    timeout 1m python3 ../../tools/check_graph.py --n 40 --k 10 ../../ralph/found/B_e162_d7.g6
    timeout 1m python3 ../../.hmz/flows/r310_ralph/gate.py ../.. check ../../ralph/found/B_e162_d7.g6 40 10
fi
