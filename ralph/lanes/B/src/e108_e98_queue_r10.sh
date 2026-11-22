#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
ulimit -t 300
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
src=../../ralph/lanes/B/src
scout=../ideas/r009_N
stitch=work/e108_r10_stitch2
o=../../opt/bin
out=${1:?new output directory}
mkdir "$out"
export TMPDIR="$PWD/$out"
canon() { timeout 60s "$o/labelg" -q | sort -u; }
for tool in clauses transversal; do
    timeout 30s g++ -O3 -std=c++17 -march=native -I"$src" "$scout/$tool.cc" -o "$out/$tool"
done

timeout 30s "$stitch/deck" 6 0 < work/prefix_r7_replay/control.critical.g6 | canon > "$out/small.cards"
canon < "$scout/exact15.cards" | cmp - "$out/small.cards"
timeout 30s "$out/clauses" 6 dump < "$out/small.cards" > "$out/small.hyp" 2> "$out/small.clauses.log"
timeout 30s "$out/transversal" 16 < "$out/small.hyp" > "$out/small.raw" 2> "$out/small.covers.log"
canon < "$scout/exact15.16.raw" > "$out/small.expected"
canon < "$out/small.raw" | cmp - "$out/small.expected"
test -s "$out/small.expected"
wc -l "$out/small."{cards,expected}

sort -mu work/e108_r10_new/stitch5.g6 work/e108_r10_micro/repuncture6.g6 > "$out/hosts.g6"
test "$(wc -l < "$out/hosts.g6")" -eq 11
timeout 30s "$stitch/deck" 8 0 < "$out/hosts.g6" | canon > "$out/all.cards"
timeout 20s "$o/pickg" -qe98:108 "$out/all.cards" "$out/target.cards"
/usr/bin/time -f 'clauses user=%U sys=%S wall=%e' timeout 45s "$out/clauses" 8 dump \
    < "$out/target.cards" > "$out/target.hyp" 2> "$out/target.clauses.log"
/usr/bin/time -f 'covers user=%U sys=%S wall=%e' timeout 45s "$out/transversal" 98 \
    < "$out/target.hyp" > "$out/target.raw" 2> "$out/target.covers.log"
canon < "$out/target.raw" > "$out/target.g6"
count=$(wc -l < "$out/target.g6")
test "$count" -gt 0
timeout 20s build/audit_duals 31 98 9 "$count" < "$out/target.g6"
timeout 20s build/irreducible 9 < "$out/target.g6" | cmp - "$out/target.g6"
sort -mu "$stitch/previous.parents" "$stitch/"{a,b}.98.selected "$stitch/micro.98.selected" > "$out/deny.g6"
comm -23 "$out/target.g6" "$out/deny.g6" > "$out/fresh.g6"
wc -l "$out/"{all.cards,target.cards,target.raw,target.g6,fresh.g6}
sha256sum "$out/"{target.g6,fresh.g6}
printf 'PASS parent-only queue; no further e108 lift was run\n'
