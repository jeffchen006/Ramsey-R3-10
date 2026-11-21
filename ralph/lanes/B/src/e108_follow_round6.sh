#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

previous=${1:?terminal e108 pass directory}
out=${2:?new working directory}
src=../../ralph/lanes/B/src
goal=2104151
mkdir "$out"
for pass in {1..8}; do
    count=$(wc -l < "$previous/union.g6")
    if (( count > goal )); then exit 2; fi
    if (( count == goal )); then break; fi
    if [[ ! -s "$previous/new.g6" ]]; then
        printf 'fixed point: %s of %s, %s missing\n' "$count" "$goal" "$((goal-count))"
        exit 3
    fi
    next="$out/pass$pass"
    timeout --kill-after=15s 2m bash "$src/e108_lateral_round6.sh" "$previous/new.g6" "$previous/union.g6" "$next" 1
    previous=$next
done
test "$(wc -l < "$previous/union.g6")" -eq "$goal"
ln "$previous/union.g6" "$out/full.g6"
/usr/bin/time -f 'validity CPU %U+%S wall %e' timeout --kill-after=15s 4m build/audit_duals 32 108 9 "$goal" < "$out/full.g6"
/usr/bin/time -f 'Traces CPU %U+%S wall %e' timeout --kill-after=15s 6m ../../opt/bin/shortg -t -u -T"$out" "$out/full.g6" 2> "$out/traces.log"
cat "$out/traces.log"
rg -q '^>Z 2104151 graphs read ' "$out/traces.log"
rg -qx '>Z 2104151 graphs produced' "$out/traces.log"
comm -13 work/e108_r5/reducible.g6 "$out/full.g6" > "$out/critical.g6"
comm -23 work/e108_r5/reducible.g6 "$out/full.g6" > "$out/missing_reducible.g6"
test ! -s "$out/missing_reducible.g6"
test "$(wc -l < "$out/critical.g6")" -eq 1880
timeout 1m build/irreducible 9 < "$out/critical.g6" | cmp - "$out/critical.g6"
sha256sum "$out/full.g6" "$out/critical.g6"
printf 'exact e108 census PASS: %s valid pairwise nonisomorphic classes (GR Table 14)\n' "$goal"
