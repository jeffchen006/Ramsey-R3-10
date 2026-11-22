#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
ulimit -t 750
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
src=../../ralph/lanes/B/src
scout=../ideas/r009_N
old=work/e108_r10_stitch2
queue=work/e108_r10_e98_queue
base=work/e108_r10_micro
opt=../../opt/bin
mode=${1:?search, prove, or replay}
out=${2:?work directory}
export TMPDIR="$PWD/$out"

timed() { /usr/bin/time -f 'CPU user=%U sys=%S wall=%e' "$@"; }
canon() { timeout 40s "$opt/labelg" -q | sort -u; }

deck() {
    local edge=$1 hosts=$2 prefix=$3 count
    printf 'DECK %s level=%s hosts=%s\n' "$prefix" "$edge" "$(wc -l < "$hosts")"
    timed timeout 45s "$out/deck" 8 0 < "$hosts" | canon > "$prefix.cards"
    timeout 15s "$opt/pickg" -qe"$edge":108 "$prefix.cards" "$prefix.eligible"
    timed timeout 60s "$out/clauses" 8 dump < "$prefix.eligible" > "$prefix.hyp" 2> "$prefix.clauses.log"
    timed timeout 45s "$out/transversal" "$edge" < "$prefix.hyp" > "$prefix.raw" 2> "$prefix.covers.log"
    canon < "$prefix.raw" > "$prefix.g6"
    count=$(wc -l < "$prefix.g6")
    if ((count)); then
        timeout 20s build/audit_duals 31 "$edge" 9 "$count" < "$prefix.g6"
        timeout 20s build/irreducible 9 < "$prefix.g6" | cmp - "$prefix.g6"
    fi
    wc -l "$prefix."{cards,eligible,raw,g6}
}

search() {
    local generation zero=0 tested=0 shiftcount batch group source prefix count degree new parents next name
    local -a groups
    export TMPDIR="$PWD/$out"
    mkdir "$out"
    timed timeout 80s bash "$src/e108_stitch_r10.sh" control "$out/control"
    for name in stitch deck; do cp "$out/control/$name" "$out/$name"; done
    for name in clauses transversal; do
        timed timeout 20s g++ -O3 -std=c++17 -march=native -I"$src" "$scout/$name.cc" -o "$out/$name"
    done
    timeout 30s "$out/deck" 6 0 < work/prefix_r7_replay/control.critical.g6 | canon > "$out/small.cards"
    cmp "$out/small.cards" "$queue/small.cards"
    timeout 30s "$out/clauses" 6 dump < "$out/small.cards" > "$out/small.hyp" 2> "$out/small.clauses.log"
    timeout 30s "$out/transversal" 16 < "$out/small.hyp" | canon > "$out/small.g6"
    cmp "$out/small.g6" "$queue/small.expected"
    for source in a b; do
        for degree in 7 8; do
            timeout 30s "$out/stitch" 8 108 "$degree" < "$old/$source.98.selected" > "$out/control.$source.$degree"
        done
        cat "$out/control.$source."{7,8} | canon | comm -12 - "$old/withheld.g6" > "$out/control.$source.hits"
        cmp "$out/control.$source.hits" "$old/$source.98.withheld"
    done
    wc -l "$out/"control.?.hits
    deck 98 work/e108_r10_new/stitch5.g6 "$out/stitch"
    deck 98 "$base/repuncture6.g6" "$out/repuncture"
    cat "$out/"{stitch,repuncture}.g6 | sort -u | cmp - "$queue/target.g6"
    cp "$queue/deny.g6" "$out/deny"
    wc -l "$out/deny"
    comm -23 "$out/stitch.g6" "$out/repuncture.g6" | comm -23 - "$out/deny" > "$out/0.stitch"
    comm -23 "$out/repuncture.g6" "$out/stitch.g6" | comm -23 - "$out/deny" > "$out/0.repuncture"
    comm -12 "$out/stitch.g6" "$out/repuncture.g6" | comm -23 - "$out/deny" > "$out/0.shared"
    sort -mu "$out/0."{stitch,repuncture,shared} | cmp - "$queue/fresh.g6"
    : > "$out/novel.g6"
    : > "$out/tested.g6"
    printf 'generation\tbatch\tstratum\tparents\tkeys\tnovel\n' > "$out/search.tsv"
    for generation in $(seq 0 23); do
        if ((generation)); then
            next="$out/$((generation - 1)).novel"
            if [[ ! -s $next ]]; then
                echo 'STOP empty fresh queue (no new targets to puncture)'
                break
            fi
            deck 98 "$next" "$out/$generation.parents"
            comm -23 "$out/$generation.parents.g6" "$out/deny" | comm -23 - "$out/tested.g6" > "$out/$generation.adaptive"
            if [[ ! -s $out/$generation.adaptive ]]; then
                echo 'STOP empty fresh queue (all parents already tested/excluded)'
                break
            fi
            groups=(adaptive)
        else
            groups=(stitch repuncture shared)
        fi
        parents=0
        for group in "${groups[@]}"; do
            parents=$((parents + $(wc -l < "$out/$generation.$group")))
            awk 'NR % 2 { print > first; next } { print > second }' \
                first="$out/$generation.$group.a" second="$out/$generation.$group.b" "$out/$generation.$group"
        done
        if ((tested + parents > 4096)); then
            echo 'STOP 4096-parent budget (remaining queue not exhausted)'
            break
        fi
        : > "$out/$generation.novel"
        for batch in a b; do
            shiftcount=0
            for group in "${groups[@]}"; do
                prefix="$out/$generation.$group.$batch"
                [[ -s $prefix ]] || continue
                count=$(wc -l < "$prefix")
                tested=$((tested+count))
                comm -12 "$prefix" "$out/tested.g6" | cmp - /dev/null
                sort -mu "$prefix" "$out/tested.g6" > "$out/tested.tmp"
                mv "$out/tested.tmp" "$out/tested.g6"
                for degree in 7 8; do
                    timed timeout 35s "$out/stitch" 8 108 "$degree" < "$prefix" > "$prefix.$degree.raw"
                done
                cat "$prefix."{7,8}.raw | canon > "$prefix.keys"
                timed comm -23 "$prefix.keys" "$base/union.g6" | comm -23 - "$out/novel.g6" > "$prefix.novel"
                new=$(wc -l < "$prefix.novel")
                shiftcount=$((shiftcount+new))
                sort -mu "$prefix.novel" "$out/$generation.novel" > "$out/generation.tmp"
                mv "$out/generation.tmp" "$out/$generation.novel"
                sort -mu "$prefix.novel" "$out/novel.g6" > "$out/novel.tmp"
                mv "$out/novel.tmp" "$out/novel.g6"
                printf '%s\t%s\t%s\t%d\t%d\t%d\n' "$generation" "$batch" "$group" \
                    "$count" "$(wc -l < "$prefix.keys")" "$new" | tee -a "$out/search.tsv"
            done
            if ((shiftcount)); then zero=0; else zero=$((zero+1)); fi
            ((zero < 2)) || break
        done
        if ((zero >= 2)); then
            echo 'STOP two disjoint zero-yield batches'
            break
        fi
    done
    test "$tested" -eq "$(wc -l < "$out/tested.g6")"
    sha256sum "$out/"{search.tsv,tested.g6,novel.g6}
}

proofs() {
    local count total
    count=$(wc -l < "$out/novel.g6")
    test "$count" -gt 0
    timeout 30s build/audit_duals 32 108 9 "$count" < "$out/novel.g6"
    timeout 30s build/irreducible 9 < "$out/novel.g6" | cmp - "$out/novel.g6"
    timed timeout 50s python3 - "$out/novel.g6" "$src" <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[2])
from critical_witness import witness, check
total = 0
for key in Path(sys.argv[1]).read_text().splitlines():
    evidence = witness(key, 9)
    assert evidence and check(evidence) == (32, 108)
    total += len(evidence['after_deletion'])
    assert len(evidence['after_deletion']) == 108
print(f'PASS {total} private independent-nine witnesses')
PY
    sort -cu "$out/novel.g6"
    sort -cu "$base/union.g6"
    canon < "$out/novel.g6" | cmp - "$out/novel.g6"
    comm -12 "$out/novel.g6" "$base/union.g6" | cmp - /dev/null
    replaydir=$(mktemp -d "$out/proofcheck.XXXXXX")
    trap 'rm -rf "$replaydir"' EXIT
    sort -mu "$out/novel.g6" "$base/critical1828.g6" > "$replaydir/critical.g6"
    timed timeout 35s "$opt/shortg" -tu "$replaydir/critical.g6" 2> "$replaydir/traces.log"
    rg -x ">Z $((1828+count)) graphs produced" "$replaydir/traces.log"
    if [[ $mode == prove ]]; then
        mv "$replaydir/critical.g6" "$out/critical.g6"
        timed sort -mu "$out/novel.g6" "$base/union.g6" > "$out/union.g6"
        timed timeout 30s build/demand_clique 8 < "$out/novel.g6" > "$out/cliques.tsv"
        awk 'ARGIND==1 {covered[$1]=1; next} ! (FNR in covered) {print FNR "\t" $0}' \
            "$out/cliques.tsv" "$out/novel.g6" > "$out/complement.tsv"
        cut -f 2 "$out/complement.tsv" | timeout 30s build/demand_clique 7 > "$out/pins.tsv"
        timed timeout --kill-after=5s 3m python3 "$src/floor109_proofs.py" "$out/complement.tsv" "$out/proofs" "$out/pins.tsv" > "$out/production.log"
    else
        cmp "$replaydir/critical.g6" "$out/critical.g6"
        sort -mu "$out/novel.g6" "$base/union.g6" | cmp - "$out/union.g6"
    fi
    total=$(wc -l < "$out/union.g6")
    test "$total" -eq "$((2104099+count))"
    timed timeout 30s python3 ../../ralph/lanes/G/verify_uncovered.py "$out/novel.g6" "$out/cliques.tsv" \
        --degree 7 --unproved "$out/complement.tsv"
    find "$out/proofs" -maxdepth 1 -type f -name '*.lrat' -exec cp -t "$replaydir" {} +
    timed timeout --kill-after=5s 3m python3 "$src/floor109_proofs.py" "$out/complement.tsv" "$replaydir" "$out/pins.tsv" \
        --replay --dual > "$replaydir/replay.log"
    awk '$1!="counts" {print $1,$2,$3}' "$out/production.log" > "$replaydir/production.index"
    awk '$1!="counts" {print $1,$2,$3}' "$replaydir/replay.log" > "$replaydir/replay.index"
    cmp "$replaydir/production.index" "$replaydir/replay.index"
    cmp <(cut -f 1 "$out/complement.tsv") <(awk '{print $1}' "$replaydir/replay.index")
    test "$(find "$replaydir" -maxdepth 1 -name '*.lrat' -printf x | wc -c)" -eq "$(wc -l < "$out/complement.tsv")"
    if [[ $mode == prove ]]; then cp "$replaydir/replay.log" "$out/replay.log"; else cmp "$replaydir/replay.log" "$out/replay.log"; fi
    sha256sum "$out/"{novel.g6,critical.g6,union.g6,cliques.tsv,complement.tsv,pins.tsv,production.log,replay.log}
    printf 'PASS %d checked: %d cliques, %d dual LRATs; %d/2104151 (%d missing)\n' \
        "$count" "$(wc -l < "$out/cliques.tsv")" "$(wc -l < "$out/complement.tsv")" "$total" "$((2104151-total))"
}

case "$mode" in
    search) search;;
    prove|replay) proofs;;
    *) exit 2;;
esac
