#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

catalogue=${1:?catalogue}
out=${2:?new directory}
mode=${3:-sample}
src=../../ralph/lanes/B/src
mkdir "$out"
case "$mode" in
    sample) timeout 30s python3 "$src/sample_levels.py" "$catalogue" 32 108 4096 6108171 > "$out/input.g6" ;;
    all) cp "$catalogue" "$out/input.g6" ;;
    *) exit 2 ;;
esac
test -s "$out/input.g6"
sha256sum "$catalogue" "$out/input.g6"
timeout 2m bash "$src/e107_cliques.sh" "$out/input.g6" "$out/clique"
missing=$(wc -l < "$out/clique.missing.tsv")
if (( missing )); then
    /usr/bin/time -f 'pin search CPU %U+%S wall %e' timeout 30s build/demand_clique 7 < "$out/clique.missing.g6" > "$out/pins.tsv"
    /usr/bin/time -f 'proof production CPU %U+%S wall %e' timeout --kill-after=15s 10m \
        python3 "$src/e107_core_proofs.py" "$out/clique.missing.tsv" "$out/proofs" --pins "$out/pins.tsv" > "$out/production.log"
    count=$(awk '$2=="cert" { n++ } END {print n+0}' "$out/production.log")
    printf 'all %s missing checked for proof production, %s dual LRATs; pins %s\n' "$missing" "$count" "$(wc -l < "$out/pins.tsv")"
    if (( count != missing )); then
        awk '$2!="cert"' "$out/production.log"
        exit 3
    fi
    /usr/bin/time -f 'proof replay CPU %U+%S wall %e' timeout --kill-after=15s 8m \
        python3 "$src/e107_core_proofs.py" "$out/clique.missing.tsv" "$out/proofs" --pins "$out/pins.tsv" --verify-only > "$out/replay.log"
    cmp <(awk '$2=="cert"' "$out/production.log") <(awk '$2=="cert"' "$out/replay.log")
    du -sb "$out/proofs"
fi
printf 'pilot PASS: %s roots = %s cliques + %s dual LRATs\n' "$(wc -l < "$out/input.g6")" "$(wc -l < "$out/clique.cliq.tsv")" "$missing"
