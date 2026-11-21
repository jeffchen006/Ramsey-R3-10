#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
source_dir=../../ralph/lanes/B/src
prefix=work/r39_30_le88_mixed_prefix
out=work/prefix_checkpoint_r4
mkdir -p "$out"

find "$prefix" -maxdepth 1 -type f -name '*.canon' -print0 | sort -z >"$out/chunks.nul"
test -s "$out/chunks.nul"
xargs -0 -a "$out/chunks.nul" -r cat | timeout 4m ../../opt/bin/pickg -q -e0:87 - "$out/subset.raw"
timeout 3m sort -u -Twork "$out/subset.raw" >"$out/subset.g6"
rm "$out/subset.raw"
timeout 1m ../../opt/bin/pickg -q -e86 "$out/subset.g6" "$out/e86.g6"
timeout 1m ../../opt/bin/pickg -q -e87 "$out/subset.g6" "$out/e87.g6"
timeout 2m sort -mu "$out/e87.g6" work/edgeup2/up86/e87.g6 >"$out/union87.g6"
wc -l "$out"/{e86,e87,union87}.g6
bc=0
cmp -s "$out/e86.g6" work/hog_30_86.canon || bc=1
if (( bc )); then printf 'e86 checkpoint not yet equal to HoG\n'; else printf 'e86 checkpoint exact HoG equality\n'; fi
if timeout 2m python3 "$source_dir/ecount.py" "$out/union87.g6" 87:147335; then
    printf 'e87 checkpoint union reaches exact published count\n'
else
    printf 'e87 checkpoint incomplete; do not move the production tail\n'
fi
