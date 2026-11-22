#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
ulimit -St 650
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
src=../../ralph/lanes/B/src
self=${BASH_SOURCE[0]}
tools=../../opt/bin
source_dir=work/e108_r11_complement
base=work/e108_r11
masked=work/e108_r10_stitch2
scout=../ideas/r009_N
mode=${1:?prepare, pilot, finish, adaptive, audit, terminal, or proofs}
out=${2:?new work directory}
export TMPDIR="$PWD/$out"

canon() { timeout 25s "$tools/labelg" -q | sort -u; }
timed() { /usr/bin/time -f '%U %S %e' -o "$1" "${@:2}"; }
rows() { wc -l < "$1"; }
digest() { sha256sum "$1" | cut -d' ' -f1; }

prepare() {
    mkdir -p "$out"
    timed "$out/control.cpu" timeout 80s bash "$src/e108_stitch_r10.sh" control "$out/control"
    for mask in a b; do
        timed "$out/masked.$mask.cpu" timeout 40s bash "$self" control "$out" "$mask"
    done
    for binary in clauses transversal; do
        timed "$out/compile.$binary.cpu" timeout 20s g++ -O3 -std=c++17 -march=native -I"$src" "$scout/$binary.cc" -o "$out/$binary"
    done
    timed "$out/deck.control.cpu" timeout 50s bash "$self" deck "$out" small work/prefix_r7_replay/control.critical.g6 16 6
    cmp "$out/small.g6" work/e108_r10_e98_queue/small.expected
    test "$(rows "$source_dir/deck.known_r10r11")" -eq 471
    test "$(rows "$source_dir/deck.conservative_only")" -eq 745
    test ! -s "$source_dir/scout_n.98.fresh"
    test "$(rows "$source_dir/total.98.fresh")" -eq 7954
    sort -cu "$source_dir/total.98.fresh"
    sort -mu "$source_dir/deck.known_r10r11" "$source_dir/deck.conservative_only" "$source_dir/total.98.fresh" | cmp - "$source_dir/total.98.g6"
    comm -12 "$source_dir/deck.known_r10r11" "$source_dir/deck.conservative_only" | cmp - /dev/null
    comm -12 "$source_dir/excluded98.g6" "$source_dir/total.98.fresh" | cmp - /dev/null
    cp "$source_dir/old.98.fresh" "$out/old.pool"
    comm -12 "$source_dir/scout_other.98.fresh" "$out/old.pool" > "$out/shared.pool"
    comm -23 "$source_dir/scout_other.98.fresh" "$out/old.pool" > "$out/scout.pool"
    comm -23 "$out/old.pool" "$out/shared.pool" > "$out/old-only.pool"
    sort -mu "$out/old.pool" "$out/scout.pool" > "$out/occupied.pool"
    comm -23 "$source_dir/frontier.98.fresh" "$out/occupied.pool" > "$out/frontier.pool"
    sort -mu "$out/old-only.pool" "$out/shared.pool" "$out/scout.pool" "$out/frontier.pool" | cmp - "$source_dir/total.98.fresh"
    printf 'id\torigin\tparents\tkey_sha256\n' > "$out/plan.tsv"
    for group in old-only scout shared frontier; do
        prefix="$out/target.$group"
        printf '%s parents=%s\n' "$group" "$(rows "$out/$group.pool")"
        [[ -s "$out/$group.pool" ]] || continue
        timeout 20s python3 "$src/stratified_g6.py" --hash-only 64 "r12-$group" < "$out/$group.pool" | sort > "$prefix.pilot.parents"
        record_plan "$prefix.pilot.parents" "$group"
        comm -23 "$out/$group.pool" "$prefix.pilot.parents" | split -l 256 -d -a 3 --additional-suffix=.parents - "$prefix."
        for parents in "$prefix."[0-9]*.parents; do
            [[ -f "$parents" ]] || continue
            record_plan "$parents" "$group"
        done
    done
    cat "$out"/target.*.parents | sort | cmp - "$source_dir/total.98.fresh"
    printf 'id\torigin\tparents\tparent_sha256\td7_raw\td8_raw\tkeys\tkey_sha256\tcpu_s\n' > "$out/done.tsv"
    : > "$out/novel.g6"
}

record_plan() {
    local filename=${1##*/}
    printf '%s\t%s\t%s\t%s\n' "${filename%.parents}" "$2" "$(rows "$1")" "$(digest "$1")" >> "$out/plan.tsv"
}

control() {
    local mask=$1
    for degree in 7 8; do
        timeout 30s "$out/control/stitch" 8 108 "$degree" < "$masked/$mask.98.selected" > "$out/masked.$mask.$degree.raw"
    done
    cat "$out/masked.$mask."{7,8}.raw | canon | comm -12 - "$masked/withheld.g6" > "$out/masked.$mask.hits"
    cmp "$out/masked.$mask.hits" "$masked/$mask.98.withheld"
    printf 'PASS masked %s hits=%s\n' "$mask" "$(rows "$out/masked.$mask.hits")"
}

deck() {
    local prefix="$out/$1" hosts=$2 edge=$3 bound=$4 order=31
    if [[ $bound == 6 ]]; then order=15; fi
    timeout 25s "$out/control/deck" "$bound" 0 < "$hosts" | canon > "$prefix.cards"
    timeout 15s "$tools/pickg" -qe"$edge":108 "$prefix.cards" "$prefix.eligible"
    timeout 25s "$out/clauses" "$bound" dump < "$prefix.eligible" > "$prefix.hyp" 2> "$prefix.clauses.log"
    timeout 25s "$out/transversal" "$edge" < "$prefix.hyp" > "$prefix.raw" 2> "$prefix.covers.log"
    canon < "$prefix.raw" > "$prefix.g6"
    if [[ -s "$prefix.g6" ]]; then
        timeout 15s build/audit_duals "$order" "$edge" "$((bound+1))" "$(rows "$prefix.g6")" < "$prefix.g6"
        timeout 15s build/irreducible "$((bound+1))" < "$prefix.g6" | cmp - "$prefix.g6"
    fi
}

lift() {
    local prefix="$out/$1" count=$2
    for degree in 7 8; do
        timeout 30s "$out/control/stitch" 8 108 "$degree" < "$prefix.parents" > "$prefix.$degree.raw" 2> "$prefix.$degree.log"
        rg -x "inputs $count d $degree roots [0-9]+ anchors [0-9]+ viable [0-9]+ nodes [0-9]+ legalminimal [0-9]+ critical $(rows "$prefix.$degree.raw")" "$prefix.$degree.log"
    done
    cat "$prefix."{7,8}.raw | canon > "$prefix.keys"
    comm -23 "$prefix.keys" "$base/union.g6" > "$prefix.new"
}

cpu_total() { awk 'NF==3 { total += $1+$2 } END { printf "%.2f", total }' "$out/"*.cpu; }

run_shard() {
    local id=$1 group=$2 count=$3 hash=$4 prefix="$out/$1" elapsed
    [[ $(digest "$prefix.parents") == "$hash" && $(rows "$prefix.parents") == "$count" ]]
    awk -v total="$(cpu_total)" 'BEGIN { exit !(total <= 490) }' || { echo 'STOP reprice; reserve 110 CPU-s for checking and a final shard'; return 3; }
    timed "$prefix.cpu" timeout --kill-after=2s 45s bash "$self" lift "$out" "$id" "$count"
    sort -mu "$prefix.new" "$out/novel.g6" > "$out/novel.tmp"
    mv "$out/novel.tmp" "$out/novel.g6"
    elapsed=$(awk '{printf "%.2f",$1+$2}' "$prefix.cpu")
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$id" "$group" "$count" "$hash" \
        "$(rows "$prefix.7.raw")" "$(rows "$prefix.8.raw")" "$(rows "$prefix.keys")" "$(digest "$prefix.keys")" "$elapsed" | tee -a "$out/done.tsv"
    echo "Novel total=$(rows "$out/novel.g6") cumulative CPU-s=$(cpu_total)"
    test "$(rows "$out/novel.g6")" -le 5
}

wave() {
    local id group count hash
    while IFS=$'\t' read -r id group count hash; do
        [[ "$id" != id ]] || continue
        [[ $(rows "$out/novel.g6") -lt 5 ]] || { echo 'STOP five canonical new keys'; break; }
        case $mode in
            pilot) [[ "$id" == *.pilot && "$group" =~ ^(old-only|scout)$ ]] || continue;;
            finish) [[ "$id" == target.* ]] || continue;;
            adaptive) [[ "$id" == adapt.* ]] || continue;;
        esac
        if cut -f 1 "$out/done.tsv" | rg -Fx "$id" >/dev/null; then continue; fi
        run_shard "$id" "$group" "$count" "$hash"
    done < "$out/plan.tsv"
}

adaptive() {
    local generation=${3:?generation number} keys="$out/${4:?new-keys filename}" prefix parents
    [[ -s "$keys" && $(rows "$out/novel.g6") -lt 5 ]]
    cmp <(comm -12 "$keys" "$out/novel.g6") "$keys"
    [[ ! -e "$out/adapt.$generation.g6" ]]
    prefix="$out/adapt.$generation"
    timed "$prefix.deck.cpu" timeout --kill-after=2s 30s bash "$self" deck "$out" "adapt.$generation" "$keys" 98 8
    audit
    sort -mu "$source_dir/total.98.fresh" "$source_dir/excluded98.g6" "$out/adaptive.tested" "$out/target.tested" > "$prefix.excluded"
    comm -23 "$prefix.g6" "$prefix.excluded" > "$prefix.fresh"
    echo "ADAPT $generation parents=$(rows "$prefix.g6") fresh=$(rows "$prefix.fresh")"
    [[ -s "$prefix.fresh" ]] || return 0
    cp "$out/novel.g6" "$prefix.prev"
    split -l 128 -d -a 3 --additional-suffix=.parents "$prefix.fresh" "$prefix."
    for parents in "$prefix."[0-9]*.parents; do record_plan "$parents" "adapt.$generation"; done
    wave
    comm -23 "$out/novel.g6" "$prefix.prev" > "$prefix.novel"
}

audit() {
    timeout 20s python3 "$src/e108_r12_audit.py" "$out" "$source_dir" "$base"
}

terminal() {
    local tested produced novel
    audit
    tested=$(rows "$out/target.tested")
    produced=$(rows "$out/produced.keys")
    novel=$(rows "$out/novel.g6")
    if [[ -s "$out/target.remaining" ]]; then test "$novel" -eq 5; fi
    timeout 25s build/audit_duals 31 98 9 "$tested" < "$out/target.tested"
    timeout 25s build/irreducible 9 < "$out/target.tested" | cmp - "$out/target.tested"
    timeout 25s "$tools/shortg" -tu -T"$out" "$out/target.tested" 2> "$out/parents.traces"
    rg -x ">Z $tested graphs produced" "$out/parents.traces"
    while IFS=$'\t' read -r id rest; do
        [[ $id != id ]] || continue
        canon < <(cat "$out/$id."{7,8}.raw) | cmp - "$out/$id.keys"
    done < "$out/done.tsv"
    timeout 25s build/audit_duals 32 108 9 "$produced" < "$out/produced.keys"
    timeout 25s build/irreducible 9 < "$out/produced.keys" | cmp - "$out/produced.keys"
    timeout 25s "$tools/shortg" -tu -T"$out" "$out/produced.keys" 2> "$out/output.traces"
    rg -x ">Z $produced graphs produced" "$out/output.traces"
    cat "$base/critical.g6" "$out/produced.keys" | timeout 25s "$tools/shortg" -tu -T"$out" 2> "$out/novelty.traces"
    rg -x ">Z $((1875+novel)) graphs produced" "$out/novelty.traces"
    test "$(rows "$out/target.remaining")" -eq "$((7954-tested))"
    sha256sum "$out/"{plan.tsv,done.tsv,target.tested,target.remaining,adaptive.tested,produced.keys,novel.g6}
}

proofs() {
    local count complement
    count=$(rows "$out/novel.g6")
    ((count > 0 && count <= 5))
    timeout 25s build/audit_duals 32 108 9 "$count" < "$out/novel.g6"
    timeout 25s build/irreducible 9 < "$out/novel.g6" | cmp - "$out/novel.g6"
    timeout 25s python3 - "$src" "$out/novel.g6" <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
from critical_witness import check, witness
total = 0
for key in Path(sys.argv[2]).read_text().splitlines():
    evidence = witness(key, 9)
    assert evidence and check(evidence) == (32, 108)
    assert len(evidence['after_deletion']) == 108
    total += 108
print('PASS private independent-nine witnesses:', total)
PY
    comm -12 "$out/novel.g6" "$base/union.g6" | cmp - /dev/null
    sort -mu "$out/novel.g6" "$base/critical.g6" > "$out/critical.g6"
    timeout 25s "$tools/shortg" -tu -T"$out" "$out/critical.g6" 2> "$out/critical.traces"
    rg -x ">Z $((1875+count)) graphs produced" "$out/critical.traces"
    sort -mu "$out/novel.g6" "$base/union.g6" > "$out/union.g6"
    test "$(rows "$out/union.g6")" -eq "$((2104146+count))"
    timeout 15s build/demand_clique 8 < "$out/novel.g6" > "$out/cliques.tsv"
    awk 'ARGIND==1 { seen[$1]=1; next } !(FNR in seen) { print FNR "\t" $0 }' "$out/cliques.tsv" "$out/novel.g6" > "$out/complement.tsv"
    timeout 15s python3 ../../ralph/lanes/G/verify_uncovered.py "$out/novel.g6" "$out/cliques.tsv" --degree 7 --unproved "$out/complement.tsv"
    cut -f 2 "$out/complement.tsv" | timeout 15s build/demand_clique 7 > "$out/pins.tsv"
    timeout --kill-after=2s 55s python3 "$src/floor109_proofs.py" "$out/complement.tsv" "$out/proofs" "$out/pins.tsv" > "$out/production.log"
    timeout --kill-after=2s 30s python3 "$src/floor109_proofs.py" "$out/complement.tsv" "$out/proofs" "$out/pins.tsv" --replay --dual > "$out/replay.log"
    cmp <(awk '$1!="counts" {print $1,$2,$3}' "$out/production.log") <(awk '$1!="counts" {print $1,$2,$3}' "$out/replay.log")
    cmp <(cut -f 1 "$out/complement.tsv") <(awk '$1!="counts" {print $1}' "$out/replay.log")
    complement=$(rows "$out/complement.tsv")
    printf 'PASS %s new scoped cases, %s cliques, %s dual LRATs\n' "$count" "$((count-complement))" "$complement"
}

case $mode in
    prepare) prepare;;
    control) control "${3:?mask}";;
    pilot|finish) wave;;
    lift) lift "${3:?shard}" "${4:?count}";;
    deck) deck "${3:?prefix}" "${4:?hosts}" "${5:?edge}" "${6:?bound}";;
    adaptive) adaptive "$@";;
    audit) audit;;
    terminal) terminal;;
    proofs) proofs;;
    *) exit 2;;
esac
