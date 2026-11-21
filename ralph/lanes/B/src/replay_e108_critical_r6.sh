#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

src=../../ralph/lanes/B/src
directory=work/e108_r6_critical_proof
input=work/e108_r6_rewire/startcritical.g6
out=$(mktemp -d work/e108_replay.XXXXXX)
trap 'rm -rf "$out"' EXIT
timeout 30s build/audit_duals 32 108 9 614 < "$input"
timeout 30s build/irreducible 9 < "$input" | cmp - "$input"
timeout 30s ../../opt/bin/shortg -t -u -T"$out" "$input" 2> "$out/traces.log"
rg -q '^>Z 614 graphs read ' "$out/traces.log"
rg -qx '>Z 614 graphs produced' "$out/traces.log"
test "$(wc -l < "$directory/clique.cliq.tsv")" -eq 569
test "$(wc -l < "$directory/clique.missing.tsv")" -eq 45
timeout 45s python3 ../../ralph/lanes/G/verify_uncovered.py "$input" "$directory/clique.cliq.tsv" \
    --degree 7 --unproved "$directory/clique.missing.tsv"
cp "$directory/proofs/"*.lrat "$out/"
timeout 2m python3 "$src/floor109_proofs.py" "$directory/clique.missing.tsv" "$out" "$directory/pins.tsv" \
    --replay --dual > "$out/replay.log"
awk '$1!="counts" {print $1,$2,$3}' "$out/replay.log" > "$out/replay.index"
awk '$1!="counts" {print $1,$2,$3}' "$directory/production.log" > "$out/production.index"
test "$(wc -l < "$out/replay.index")" -eq 45
cmp "$out/production.index" "$out/replay.index"
printf 'PASS supplied 614-class e108 cover: 569 cliques + 45 regenerated and dual-checked LRATs\n'
