#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1 TMPDIR=$PWD/work

src=../../ralph/lanes/B/src
opt=../../opt/bin
out=${1:?new output directory}
stage=${2:?control or probe}
mkdir "$out"
timeout 30s nice -n 5 g++ -O3 -std=c++17 -Wall -Wextra -Wno-unused-function \
    "$src/pair_repartition.cc" -o "$out/generator"
catalogue=work/e108_r8_import

function scan {
    local name=$1 input=$2 alpha=$3 plus=$4 widen=$5 limit=$6
    echo "scan $name $alpha $plus $widen ($input)"
    /usr/bin/time -f 'generator user=%U sys=%S wall=%e' \
        timeout "$limit" nice -n 5 "$out/generator" "$alpha" "$plus" "$widen" \
        < "$input" > "$out/$name.raw"
    timeout 45s nice -n 5 "$opt/shortg" -q -T"$out" "$out/$name.raw" "$out/$name.g6"
    sha256sum "$input" "$out/$name.g6"
    wc -l "$out/$name.g6"
}

function sample {
    local input=$1 offset=$2 count=$3 stride=$4 target=$5
    local size
    size=$(wc -l < "$input")
    awk -v n="$size" -v m="$count" -v offset="$offset" -v stride="$stride" '
        BEGIN { for (i=0; i<m; ++i) take[1+int((i*stride+offset+0.5)*n/(m*stride))]=1 }
        NR in take
    ' "$input" > "$target"
    test "$(wc -l < "$target")" -eq "$count"
}

case "$stage" in
control)
    timeout 45s nice -n 5 python3 "$src/cal_pair_repartition.py" "$out/generator"
    "$opt/pickg" -q -e21 val/r37_16_le22.g6 "$out/e21.g6"
    "$opt/pickg" -q -e22 val/r37_16_le22.g6 "$out/e22.raw.g6"
    "$opt/shortg" -q -T"$out" "$out/e22.raw.g6" "$out/e22.g6"
    timeout 20s nice -n 5 build/irreducible 7 < "$out/e22.g6" > "$out/e22.critical.g6"
    test "$(wc -l < "$out/e21.g6")" -eq 15
    test "$(wc -l < "$out/e22.g6")" -eq 201
    test "$(wc -l < "$out/e22.critical.g6")" -eq 42
    scan hidden22 "$out/e21.g6" 6 1 1 30s
    comm -23 "$out/hidden22.g6" "$out/e22.critical.g6" > "$out/unexpected.g6"
    test ! -s "$out/unexpected.g6"
    test "$(wc -l < "$out/hidden22.g6")" -eq 33
    echo 'withheld e22 critical control: 33 of 42 recovered'
    ;;
probe)
    source107=work/e108_r5/e107.control.g6
    sample "$source107" 0 32 32 "$out/e107.g6"
    sample work/e108_r5/reducible.g6 0 32 32 "$out/e108.reducible.g6"
    sample "$catalogue/old.nauty.g6" 0 32 16 "$out/e108.old.g6"
    scan up107 "$out/e107.g6" 8 1 1 240s
    scan lateral108 "$out/e108.reducible.g6" 8 0 1 240s
    scan old108 "$out/e108.old.g6" 8 0 1 240s
    for name in up107 lateral108 old108; do
        comm -12 "$out/$name.g6" "$catalogue/scout1142.g6" > "$out/$name.scout.g6"
        comm -23 "$out/$name.g6" "$catalogue/union.g6" > "$out/$name.novel.g6"
        wc -l "$out/$name."{scout,novel}.g6
    done
    sort -mu "$out/"*.novel.g6 > "$out/novel.g6"
    wc -l "$out/novel.g6"
    ;;
*) exit 2 ;;
esac
