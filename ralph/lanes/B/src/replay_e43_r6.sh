#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

source_dir=../../ralph/lanes/B/src
timeout 2m bash "$source_dir/audit_e88_scans.sh" e43
test ! -s val/d7_e43_outside_prefix.g6
out=work/e43_r6_replay
mkdir -p "$out"
timeout 1m ../../opt/bin/pickg -q -e43 val/r38_22_le44.g6 "$out/fresh43.g6"
cmp "$out/fresh43.g6" work/d7_e43_outside_prefix_inputs.g6
sort -cu "$out/fresh43.g6"
timeout 1m build/audit_duals 22 43 8 1521 < "$out/fresh43.g6"
timeout 1m ../../opt/bin/shortg -t -u -T"$out" "$out/fresh43.g6" 2> "$out/traces.log"
rg -q '^>Z 1521 graphs read ' "$out/traces.log"
rg -qx '>Z 1521 graphs produced' "$out/traces.log"
sha256sum "$out/fresh43.g6" val/d7_e43_outside_prefix.g6
printf 'PASS exact GR T13 e43 seed set, bound to all 48 terminal generation chunks\n'
