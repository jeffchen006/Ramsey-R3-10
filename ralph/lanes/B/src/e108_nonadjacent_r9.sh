#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1 TMPDIR=$PWD/work
src=../../ralph/lanes/B/src
opt=../../opt/bin
out=${1:?new output directory}
stage=${2:?control or heldout}
mkdir "$out"
timeout 30s nice -n 5 g++ -O3 -std=c++17 -Wall -Wextra -Wno-unused-function \
    "$src/nonadjacent_critical.cc" -o "$out/lift"
timeout 30s nice -n 5 cc -O3 -std=c11 -Wall -Wextra -Wno-unused-function \
    "$src/nonadjacent_stems.c" -o "$out/cards"

function cards {
    local tag=$1 hosts=$2 low=$3 high=$4
    timeout 90s nice -n 5 "$out/cards" "$low" "$high" < "$hosts" > "$out/$tag.raw"
    timeout 90s nice -n 5 "$opt/shortg" -q -T"$out" "$out/$tag.raw" "$out/$tag.g6"
    wc -l "$out/$tag.g6"
}
function scan {
    local tag=$1 source=$2 alpha=$3 minimum=$4 edges=$5
    echo "scan $tag: $source"
    /usr/bin/time -f 'generator user=%U sys=%S wall=%e' timeout 180s nice -n 5 \
        "$out/lift" "$alpha" "$minimum" "$edges" < "$source" > "$out/$tag.raw"
    timeout 30s nice -n 5 "$opt/shortg" -q -T"$out" "$out/$tag.raw" "$out/$tag.g6"
    sha256sum "$source" "$out/$tag.g6"
    wc -l "$out/$tag.g6"
}
function sample {
    local input=$1 count=$2 target=$3
    local size
    size=$(wc -l < "$input")
    if (( size <= count )); then cp "$input" "$target"; return; fi
    awk -v n="$size" -v m="$count" '
        BEGIN { for (i=0; i<m; ++i) take[1+int((i+0.5)*n/m)]=1 }
        NR in take
    ' "$input" > "$target"
    test "$(wc -l < "$target")" -eq "$count"
}

case "$stage" in
control)
    timeout 90s nice -n 5 python3 "$src/cal_nonadjacent_critical.py" "$out/cards" "$out/lift"
    "$opt/pickg" -q -e21 val/r37_16_le22.g6 "$out/e21.g6"
    "$opt/pickg" -q -e22 val/r37_16_le22.g6 "$out/e22.raw.g6"
    "$opt/shortg" -q -T"$out" "$out/e22.raw.g6" "$out/e22.g6"
    timeout 20s nice -n 5 build/irreducible 7 < "$out/e22.g6" > "$out/e22.critical.g6"
    test "$(wc -l < "$out/e21.g6")" -eq 15
    test "$(wc -l < "$out/e22.g6")" -eq 201
    test "$(wc -l < "$out/e22.critical.g6")" -eq 42
    cards control "$out/e21.g6" 10 22
    scan hidden22 "$out/control.g6" 6 0 22
    comm -23 "$out/hidden22.g6" "$out/e22.critical.g6" > "$out/unexpected.g6"
    test ! -s "$out/unexpected.g6"
    test "$(wc -l < "$out/hidden22.g6")" -eq 38
    echo 'withheld e22 critical control: 38 of 42 recovered'
    ;;
heldout)
    catalogue=work/e108_r8_import
    count=${3:-256}
    for source in up107 old108; do
        if [[ $source == up107 ]]; then
            tail -n +4097 work/e108_r5/e107.control.g6 > "$out/e107.eligible.g6"
            sample "$out/e107.eligible.g6" 256 "$out/$source.hosts.g6"
        else
            sample "$catalogue/old.nauty.g6" 128 "$out/$source.hosts.g6"
        fi
        for level in 92 93; do
            tag=$source.$level
            cards "$tag.pool" "$out/$source.hosts.g6" "$level" "$level"
            sample "$out/$tag.pool.g6" "$count" "$out/$tag.sample.g6"
            scan "$tag.lift" "$out/$tag.sample.g6" 8 4 108
            comm -12 "$out/$tag.lift.g6" "$catalogue/scout1142.g6" > "$out/$tag.scout.g6"
            comm -23 "$out/$tag.lift.g6" "$catalogue/union.g6" > "$out/$tag.novel.g6"
            wc -l "$out/$tag."{scout,novel}.g6
        done
    done
    sort -mu "$out/"*.novel.g6 > "$out/novel.g6"
    wc -l "$out/novel.g6"
    ;;
*) exit 2 ;;
esac
