#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
ulimit -t 750
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
src=../../ralph/lanes/B/src
o=../../opt/bin
scout=../ideas/r009_N
known=work/e108_r10_import
mode=${1:?control, prepare, generate, lift, or repuncture}
out=${2:?output directory}
export TMPDIR="$PWD/$out"

canon() { timeout 60s "$o/labelg" -q | sort -u; }
report() { /usr/bin/time -f 'user=%U sys=%S wall=%e' "$@"; }

case $mode in
control)
    mkdir "$out"
    report timeout 30s g++ -O3 -std=c++17 -march=native -I"$src" "$scout/stitch.cc" -o "$out/stitch"
    report timeout 30s g++ -O3 -std=c++17 -march=native -I"$src" "$scout/deck.cc" -o "$out/deck"
    timeout 20s build/irreducible 7 < val/r37_15_le16.g6 > "$out/small.parents"
    for deg in 1 2 3 4 5 6; do
        report timeout 20s "$out/stitch" 6 22 "$deg" < "$out/small.parents" > "$out/small.$deg.raw"
    done
    cat "$out"/small.*.raw | canon > "$out/small.g6"
    canon < work/prefix_r7_replay/control.critical.g6 > "$out/expected.g6"
    comm -23 "$out/small.g6" "$out/expected.g6" | cmp - /dev/null
    test "$(wc -l < "$out/small.g6")" -eq 36
    cat "$out/small.g6" "$scout/smallblind.set" | timeout 20s "$o/shortg" -tu 2> "$out/control.traces"
    rg -qx '>Z 36 graphs produced' "$out/control.traces"
    printf 'PASS independent lower level: 36/42 critical order-16/e22 controls; no extras\n'
    ;;
prepare)
    prefix=work/prefix_r8_generation/independent.critical.g6
    test "$(wc -l < "$prefix")" -eq 153612
    report timeout 90s python3 "$src/stratified_g6.py" 128 r10-prefix < "$prefix" > "$out/seed128.g6"
    awk 'NR%2 {print > path "/a.seed"; next} {print > path "/b.seed"}' path="$out" "$out/seed128.g6"
    cat "$scout"/{strong31.g6,up31c.g6,ex31.j,new31.deck} \
        work/hog_31_95.canon | canon > "$out/previous.parents"
    wc -l "$out/previous.parents" "$out/"?.seed
    report timeout 20s python3 "$src/stratified_g6.py" --hash-only 245 r10-withheld \
        < "$known/critical1817.g6" | sort > "$out/withheld.g6"
    sha256sum "$out/"{seed128.g6,previous.parents,withheld.g6} "$out/"?.seed
    ;;
generate)
    slice=${3:?a or b}
    [[ $slice == a || $slice == b ]]
    for level in 98 99 100 101; do
        for deg in 6 7 8; do
            report timeout 2m "$out/stitch" 8 "$level" "$deg" < "$out/$slice.seed" > "$out/$slice.$level.$deg.parent.raw"
        done
        cat "$out/$slice.$level."*.parent.raw | canon > "$out/$slice.$level.pool"
        comm -23 "$out/$slice.$level.pool" "$out/previous.parents" > "$out/$slice.$level.fresh"
        if [[ $slice == b ]]; then
            comm -23 "$out/$slice.$level.fresh" "$out/a.$level.selected" > "$out/$slice.$level.pool2"
            mv "$out/$slice.$level.pool2" "$out/$slice.$level.fresh"
        fi
        report timeout 30s python3 "$src/stratified_g6.py" 128 "r10-$slice-$level" < "$out/$slice.$level.fresh" \
            | sort > "$out/$slice.$level.selected"
        wc -l "$out/$slice.$level."{pool,fresh,selected}
        sha256sum "$out/$slice.$level."{pool,selected}
    done
    ;;
lift)
    slice=${3:?a or b}
    [[ $slice == a || $slice == b ]]
    for level in 98 99 100 101; do
        selected="$out/$slice.$level.selected"
        for deg in 8 7; do
            if (( level + deg > 108 )); then
                continue
            fi
            report timeout 2m "$out/stitch" 8 108 "$deg" < "$selected" > "$out/$slice.$level.$deg.target.raw"
        done
        cat "$out/$slice.$level."*.target.raw | canon > "$out/$slice.$level.keys"
        comm -12 "$out/$slice.$level.keys" "$out/withheld.g6" > "$out/$slice.$level.withheld"
        comm -23 "$out/$slice.$level.keys" "$known/union.g6" > "$out/$slice.$level.novel"
        wc -l "$out/$slice.$level."{keys,withheld,novel}
    done
    sort -u "$out/$slice."*.keys > "$out/$slice.keys"
    sort -u "$out/$slice."*.withheld > "$out/$slice.withheld"
    sort -u "$out/$slice."*.novel > "$out/$slice.novel"
    wc -l "$out/$slice."{keys,withheld,novel}
    sha256sum "$out/$slice."{keys,withheld,novel}
    ;;
repuncture)
    used=$(cat "$out/"{a,b}.98.selected | sort -u | wc -l)
    test "$used" -eq 249
    report timeout 30s "$out/deck" 8 16 < work/e108_r10_new/stitch5.g6 | canon > "$out/micro.cards"
    timeout 20s "$o/pickg" -qe98 "$out/micro.cards" "$out/micro.98.pool"
    sort -mu "$out/previous.parents" "$out/"{a,b}.98.selected > "$out/micro.exclude"
    comm -23 "$out/micro.98.pool" "$out/micro.exclude" > "$out/micro.98.fresh"
    report timeout 20s python3 "$src/stratified_g6.py" "$((256-used))" r10-repuncture \
        < "$out/micro.98.fresh" | sort > "$out/micro.98.selected"
    count=$(wc -l < "$out/micro.98.selected")
    test "$count" -gt 0
    timeout 20s build/audit_duals 31 98 9 "$count" < "$out/micro.98.selected"
    timeout 20s build/irreducible 9 < "$out/micro.98.selected" | cmp - "$out/micro.98.selected"
    for deg in 7 8; do
        report timeout 20s "$out/stitch" 8 108 "$deg" < "$out/micro.98.selected" > "$out/micro.$deg.target.raw"
    done
    cat "$out/"micro.*.target.raw | canon > "$out/micro.keys"
    comm -23 "$out/micro.keys" work/e108_r10_new/union.g6 > "$out/micro.novel"
    wc -l "$out/micro.98."{pool,fresh,selected} "$out/micro."{keys,novel}
    sha256sum "$out/micro.98.selected" "$out/micro.novel"
    ;;
*) exit 2;;
esac
