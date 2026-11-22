#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1 TMPDIR=$PWD/work

src=../../ralph/lanes/B/src
scout=../ideas/astra_N/handoff.g6
base=work/e108_r6_follow/pass4/union.g6
old_critical=work/e108_r6_rewire/startcritical.g6
reducible=work/e108_r5/reducible.g6
out=${1:?new output directory}
mkdir "$out"
printf '%s  %s\n' fa153a6ca98fd08ba5a526fee55bc18c45a0b810c260bb160b211c56103021c2 "$scout" | sha256sum -c -
cp "$scout" "$out/scout1142.g6"
timeout 30s build/audit_duals 32 108 9 1142 < "$out/scout1142.g6"
timeout 30s build/irreducible 9 < "$out/scout1142.g6" | cmp - "$out/scout1142.g6"
timeout 30s ../../opt/bin/shortg -q -T"$out" "$old_critical" "$out/old.nauty.g6"
sort -cu "$base"
sort -cu "$reducible"
test "$(wc -l < "$reducible")" -eq 2102271
cmp <(comm -23 "$base" "$reducible") "$out/old.nauty.g6"
test -z "$(comm -23 "$reducible" "$base" | head -c 1)"
test -z "$(comm -12 "$out/scout1142.g6" "$base" | head -c 1)"
sort -mu "$out/scout1142.g6" "$out/old.nauty.g6" > "$out/critical1756.g6"
timeout 30s ../../opt/bin/shortg -tu -T"$out" "$out/critical1756.g6" 2> "$out/traces.log"
cat "$out/traces.log"
rg -q '^>Z 1756 graphs read ' "$out/traces.log"
rg -qx '>Z 1756 graphs produced' "$out/traces.log"
sort -mu "$base" "$out/scout1142.g6" > "$out/union.g6"
test "$(wc -l < "$out/union.g6")" -eq 2104027
timeout 2m python3 "$src/critical_witness.py" count "$out/scout1142.g6" > "$out/witness.count"
rg -qx 1142 "$out/witness.count"
sha256sum "$base" "$old_critical" "$reducible" "$out/"{scout1142,critical1756,union}.g6
printf 'PASS separate scout 1142: union 2104027/2104151, deficit 124; certificate scope unchanged\n'
