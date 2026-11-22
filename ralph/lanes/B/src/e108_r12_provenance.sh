#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
ulimit -t 30
export LC_ALL=C
src=../ideas/r009_N
source_dir=work/e108_r11_complement
out=${1:?output directory}
opt=../../opt/bin
mkdir "$out"
export TMPDIR="$PWD/$out"

match() {
    local name=$1 pool=$2
    sha256sum "$pool"
    timeout 10s "$opt/pickg" -qe98 "$pool" | timeout 10s "$opt/labelg" -q | sort -u > "$out/$name.e98"
    comm -12 "$out/$name.e98" "$source_dir/deck.conservative_only" > "$out/$name.overlap"
    printf '%s level98=%s overlap=%s\n' "$name" "$(wc -l < "$out/$name.e98")" "$(wc -l < "$out/$name.overlap")"
}

cmp "$src/new31.deck" "$src/audit.deck.g6"
rg -F 'inputs 806 d 8' "$src/audit.final.replay"
rg -F 'inputs 843 d 7' "$src/audit.final.replay"
match deck "$src/audit.deck.g6"
match untried "$src/untried31"
match strong_pilot "$src/strong31.pilot"
match strong_pool "$src/strong31.g6"
match exact_pool "$src/ex31.j"
match up_pool "$src/up31c.g6"
sort -mu "$out/"*.overlap | cmp - "$source_dir/deck.conservative_only"
comm -23 "$source_dir/deck.conservative_only" "$out/deck.overlap" > "$out/not_deck_bound.g6"
printf 'Named N deck d7/d8 replay covers %s of 745; others = %s (do not treat the logged counts alone as parent binding)\n' \
    "$(wc -l < "$out/deck.overlap")" "$(wc -l < "$out/not_deck_bound.g6")"
