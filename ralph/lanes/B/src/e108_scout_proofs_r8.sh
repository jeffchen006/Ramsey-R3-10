#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

src=../../ralph/lanes/B/src
verifier=../../ralph/lanes/G/verify_uncovered.py
mode=${1:?produce, finish, or replay}
out=${2:?proof directory}
input=work/e108_r8_import/scout1142.g6
[[ $mode == produce || $mode == finish || $mode == replay ]]
printf '%s  %s\n' fa153a6ca98fd08ba5a526fee55bc18c45a0b810c260bb160b211c56103021c2 "$input" | sha256sum -c -
if [[ $mode == produce ]]; then
    mkdir "$out"
    timeout 45s build/demand_clique 8 < "$input" > "$out/cliques.tsv"
    awk 'ARGIND==1 {covered[$1]=1; next} ! (FNR in covered) {print FNR "\t" $0}' \
        "$out/cliques.tsv" "$input" > "$out/complement.tsv"
    timeout 45s build/demand_clique 7 < <(cut -f 2 "$out/complement.tsv") > "$out/pins.tsv"
    timeout --kill-after=5s 3m python3 "$src/floor109_proofs.py" "$out/complement.tsv" "$out/proofs" "$out/pins.tsv" \
        > "$out/production.log"
fi
timeout 45s python3 "$verifier" "$input" "$out/cliques.tsv" --degree 7 --unproved "$out/complement.tsv"
tmp=$(mktemp -d "$out/replay.XXXXXX")
trap 'rm -rf "$tmp"' EXIT
find "$out/proofs" -maxdepth 1 -type f -name '*.lrat' -exec cp -t "$tmp" {} +
timeout --kill-after=5s 2m python3 "$src/floor109_proofs.py" "$out/complement.tsv" "$tmp" "$out/pins.tsv" \
    --replay --dual > "$tmp/replay.log"
awk '$1!="counts" {print $1,$2,$3}' "$out/production.log" > "$tmp/production.index"
awk '$1!="counts" {print $1,$2,$3}' "$tmp/replay.log" > "$tmp/replay.index"
cmp "$tmp/production.index" "$tmp/replay.index"
cmp <(cut -f 1 "$out/complement.tsv") <(awk '{print $1}' "$tmp/replay.index")
test "$(find "$tmp" -maxdepth 1 -name '*.lrat' -printf x | wc -c)" -eq "$(wc -l < "$out/complement.tsv")"
if [[ $mode != replay ]]; then
    cp "$tmp/replay.log" "$out/replay.log"
else
    cmp "$tmp/replay.log" "$out/replay.log"
fi
sha256sum "$input" "$out/"{cliques.tsv,complement.tsv,pins.tsv,production.log,replay.log}
printf 'PASS 1142 supplied scout keys, %s cliques and %s dual LRATs\n' \
    "$(wc -l < "$out/cliques.tsv")" "$(wc -l < "$out/complement.tsv")"
