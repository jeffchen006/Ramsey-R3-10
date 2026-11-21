#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
source_dir=../../ralph/lanes/B/src
source_file=val/r37_16_le22.g6
out=work/round4_tail_control
mkdir -p "$out"
for edge in 20 21 22; do
    timeout 15s ../../opt/bin/pickg -q -e"$edge" "$source_file" "$out/all$edge.g6"
    timeout 15s sort -cu "$out/all$edge.g6"
done

add_edges() {
    local input=$1 output=$2
    timeout 15s build/edgeup <"$input" | timeout 15s ../../opt/bin/shortg -q -Twork - "$output"
}

add_edges "$out/all20.g6" "$out/prior21.g6"
timeout 15s comm -23 "$out/prior21.g6" "$out/all21.g6" >"$out/bad21.g6"
test ! -s "$out/bad21.g6"
timeout 15s comm -23 "$out/all21.g6" "$out/prior21.g6" >"$out/tail21.g6"
timeout 15s sort -m "$out/prior21.g6" "$out/tail21.g6" >"$out/check21.g6"
cmp "$out/all21.g6" "$out/check21.g6"
add_edges "$out/prior21.g6" "$out/prior22.g6"
add_edges "$out/tail21.g6" "$out/from_tail22.g6"
timeout 15s comm -23 "$out/from_tail22.g6" "$out/prior22.g6" >"$out/novel22.g6"
timeout 15s sort -m "$out/prior22.g6" "$out/novel22.g6" >"$out/combined22.g6"
timeout 15s python3 "$source_dir/ecount.py" "$out/combined22.g6" 22:159
timeout 15s build/irreducible 7 <"$out/all22.g6" >"$out/critical22.g6"
timeout 15s comm -23 "$out/all22.g6" "$out/critical22.g6" >"$out/reducible22.g6"
cmp "$out/combined22.g6" "$out/reducible22.g6"
wc -l "$out"/{prior21,tail21,prior22,novel22,critical22}.g6
printf 'small disjoint-tail control passed\n'
