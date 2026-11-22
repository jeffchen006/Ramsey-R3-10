#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
ulimit -t 300
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
src=../../ralph/lanes/B/src
opt=../../opt/bin
main=work/e108_r11
base=work/e108_r10_micro
stitch_prior=work/e108_r10_stitch2
out=${1:?new output directory}
mkdir "$out"
export TMPDIR="$PWD/$out"
timeit() { /usr/bin/time -f 'CPU user=%U sys=%S wall=%e' "$@"; }
canon() { timeout 45s "$opt/labelg" -q | sort -u; }

cohorts=(old scout_n scout_other frontier)
cp work/e108_r8_import/old.nauty.g6 "$out/old.hosts"
cp work/e108_r10_import/scout61.g6 "$out/scout_n.hosts"
cp work/e108_r8_import/scout1142.g6 "$out/scout_other.hosts"
sort -mu work/e108_r10_new/stitch5.g6 "$base/repuncture6.g6" "$main/novel.g6" > "$out/frontier.hosts"
for group in "${cohorts[@]}"; do sort -cu "$out/$group.hosts"; done
cat "$out/"*.hosts | sort | cmp - "$main/critical.g6"

timeit timeout 30s build/audit_duals 31 95 9 560 < work/hog_31_95.canon
timeit timeout 20s build/edgeup < work/hog_31_95.canon | canon > "$out/reducible96.g6"
count=$(wc -l < "$out/reducible96.g6")
timeit timeout 30s build/audit_duals 31 96 9 "$count" < "$out/reducible96.g6"
printf 'e96 reducible %s / 35154; critical denominator %s\n' "$count" "$((35154-count))"
sort -mu "$main/deny" "$main/tested.g6" | timeout 25s "$opt/pickg" -qe98 > "$out/excluded98.g6"

price() {
    local group=$1 prefix="$out/$1" edge count
    timeit timeout 30s "$main/deck" 8 0 < "$prefix.hosts" | canon > "$prefix.cards"
    timeit timeout 150s "$main/clauses" 8 dump < "$prefix.cards" > "$prefix.hyp" 2> "$prefix.clauses.log"
    test "$(wc -l < "$prefix.cards")" -eq "$(rg -c '^host ' "$prefix.clauses.log")"
    for edge in 96 98; do
        timeit timeout 60s "$main/transversal" "$edge" < "$prefix.hyp" > "$prefix.$edge.raw" 2> "$prefix.$edge.transversal.log"
        test "$(wc -l < "$prefix.cards")" -eq "$(rg -c '^forced ' "$prefix.$edge.transversal.log")"
        canon < "$prefix.$edge.raw" > "$prefix.$edge.g6"
        count=$(wc -l < "$prefix.$edge.g6")
        if ((count)); then
            timeit timeout 30s build/audit_duals 31 "$edge" 9 "$count" < "$prefix.$edge.g6"
            timeit timeout 30s build/irreducible 9 < "$prefix.$edge.g6" | cmp - "$prefix.$edge.g6"
        fi
    done
    wc -l "$prefix."{hosts,cards,96.raw,96.g6,98.raw,98.g6}
}

pids=()
for group in "${cohorts[@]}"; do
    price "$group" > "$out/$group.price.log" 2>&1 &
    pids+=("$!")
done
failed=0
for pid in "${pids[@]}"; do if ! wait "$pid"; then failed=1; fi; done
cat "$out/"*.price.log
test "$failed" -eq 0

printf 'cohort\thosts\te96_critical\te98_total\te98_fresh\n'
for group in "${cohorts[@]}"; do
    comm -23 "$out/$group.98.g6" "$out/excluded98.g6" > "$out/$group.98.fresh"
    printf '%s\t%s\t%s\t%s\t%s\n' "$group" \
        "$(wc -l < "$out/$group.hosts")" "$(wc -l < "$out/$group.96.g6")" \
        "$(wc -l < "$out/$group.98.g6")" "$(wc -l < "$out/$group.98.fresh")"
done
for edge in 96 98; do sort -mu "$out/"*".$edge.g6" > "$out/total.$edge.g6"; done
comm -12 "$out/total.96.g6" "$out/reducible96.g6" | cmp - /dev/null
comm -23 "$out/total.98.g6" "$out/excluded98.g6" > "$out/total.98.fresh"
sort -mu "$main/tested.g6" "$stitch_prior/"{a,b,micro}.98.selected > "$out/r10r11.tested98"
comm -12 "$out/total.98.g6" "$out/r10r11.tested98" > "$out/deck.known_r10r11"
comm -23 "$out/excluded98.g6" "$out/r10r11.tested98" | comm -12 - "$out/total.98.g6" > "$out/deck.conservative_only"
sort -m "$out/"{deck.known_r10r11,deck.conservative_only,total.98.fresh} | cmp - "$out/total.98.g6"
wc -l "$out/"{reducible96.g6,total.96.g6,total.98.g6,total.98.fresh,excluded98.g6,deck.known_r10r11,deck.conservative_only}
sha256sum "$out/"{reducible96.g6,total.96.g6,total.98.g6,total.98.fresh,excluded98.g6,deck.known_r10r11,deck.conservative_only}
