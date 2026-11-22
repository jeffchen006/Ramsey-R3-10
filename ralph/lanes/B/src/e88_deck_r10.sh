#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
ulimit -t 750
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
src=../../ralph/lanes/B/src
scout=../ideas/r009_N
o=../../opt/bin
build=work/e108_r10_stitch2
prefix=work/prefix_r8_generation/independent.critical.g6
mode=${1:?control or probe}
out=${2:?output directory}
mkdir "$out"
export TMPDIR="$PWD/$out"
canon() { timeout 60s "$o/labelg" -q | sort -u; }
report() { /usr/bin/time -f 'user=%U sys=%S wall=%e' "$@"; }
case $mode in
control)
    canon < work/prefix_r7_replay/control.critical.g6 > "$out/known.g6"
    timeout 20s python3 "$src/stratified_g6.py" --hash-only 21 r10-e88-control < "$out/known.g6" | sort > "$out/train.g6"
    comm -23 "$out/known.g6" "$out/train.g6" > "$out/withheld.g6"
    report timeout 30s "$build/deck" 6 3 < "$out/train.g6" | canon > "$out/cards.g6"
    timeout 20s build/irreducible 7 < "$out/cards.g6" | cmp - "$out/cards.g6"
    mark=(2 3 0 6 12 18 24 15 36)
    report timeout 30s "$build/stitch" 6 22 5 < "$out/cards.g6" > "$out/unmarked.raw"
    report timeout 30s "$build/stitch" 6 22 5 custom "${mark[@]}" < "$out/cards.g6" > "$out/marked.raw"
    timeout 30s python3 "$scout/markcheck.py" "${mark[@]}" < "$out/unmarked.raw" | cmp - "$out/marked.raw"
    canon < "$out/marked.raw" > "$out/marked.g6"
    comm -23 "$out/marked.g6" "$out/known.g6" | cmp - /dev/null
    comm -12 "$out/marked.g6" "$out/withheld.g6" > "$out/recovered.g6"
    test -s "$out/recovered.g6"
    wc -l "$out/"{train.g6,withheld.g6,cards.g6,unmarked.raw,marked.raw,marked.g6,recovered.g6}
    ;;
probe)
    report timeout 90s python3 "$src/stratified_g6.py" 256 r10-e88-deck < "$prefix" > "$out/seed256.g6"
    test "$(wc -l < "$out/seed256.g6")" -eq 256
    awk 'NR%2 {print > path "/a.seed"; next} {print > path "/b.seed"}' path="$out" "$out/seed256.g6"
    for slice in a b; do
        report timeout 90s "$build/deck" 8 3 < "$out/$slice.seed" | canon > "$out/$slice.cards"
        for level in 78 79 80 81 82; do
            timeout 15s "$o/pickg" -qe"$level" "$out/$slice.cards" "$out/$slice.$level.pool"
        done
    done
    for level in 78 79 80 81 82; do
        sort -mu "$out/a.$level.pool" "$out/b.$level.pool" > "$out/$level.pool"
        wc -l "$out/"{a.,b.,}"$level.pool"
        report timeout 20s python3 "$src/stratified_g6.py" 128 "r10-e88-$level" < "$out/$level.pool" \
            | sort > "$out/$level.sample"
        count=$(wc -l < "$out/$level.sample")
        if (( count == 0 )); then continue; fi
        timeout 20s build/audit_duals 29 "$level" 9 "$count" < "$out/$level.sample"
        timeout 20s build/irreducible 9 < "$out/$level.sample" | cmp - "$out/$level.sample"
        for deg in 6 7; do
            if (( level + deg > 88 )); then continue; fi
            report timeout 2m "$build/stitch" 8 88 "$deg" anchor < "$out/$level.sample" > "$out/$level.$deg.raw"
        done
        cat "$out/$level."*.raw | canon > "$out/$level.lifts"
        comm -23 "$out/$level.lifts" "$prefix" > "$out/$level.outside"
        wc -l "$out/$level."{sample,lifts,outside}
    done
    cat "$out/"*.outside | sort -u > "$out/outside.g6"
    sha256sum "$out/outside.g6" "$out/"*.sample
    ;;
*) exit 2;;
esac
