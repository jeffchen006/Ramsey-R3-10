#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

src=../../ralph/lanes/B/src
verifier=../../ralph/lanes/G/verify_uncovered.py
mode=${1:?produce or replay}
[[ $mode == produce || $mode == replay ]]
tranche=${2:-scout}
case $tranche in
    scout)
        base=work/e108_r8_import
        out=work/e108_r10_import
        input=$out/scout61.g6
        supplied=../ideas/r009_N/handoff.g6
        previous=$base/critical1756.g6
        checksum=eadc55f1fe69f5b115578bb0980cdac8f15d8ccd71c47fe2bdc03f7822c4c998
        count=61 prior_count=2104027 total_critical=1817
        ;;
    stitch)
        base=work/e108_r10_import
        out=work/e108_r10_new
        input=$out/stitch5.g6
        supplied=work/e108_r10_stitch2/b.novel
        previous=$base/critical1817.g6
        checksum=1f789beaf157d921413ba515916dab78deb72d00daa79ea1bae1990c0e7144cd
        count=5 prior_count=2104088 total_critical=1822
        ;;
    repuncture)
        base=work/e108_r10_new
        out=work/e108_r10_micro
        input=$out/repuncture6.g6
        supplied=work/e108_r10_stitch2/micro.novel
        previous=$base/critical1822.g6
        checksum=32c7038fe00eae6d29d51892bb503ad1cd5400996cc63542b795abef239d27c5
        count=6 prior_count=2104093 total_critical=1828
        ;;
    *) exit 2;;
esac
merged=$out/critical$total_critical.g6
if [[ $mode == produce ]]; then
    mkdir "$out"
    cp "$supplied" "$input"
fi
export TMPDIR="$PWD/$out"
printf '%s  %s\n' "$checksum" "$input" | sha256sum -c -
timeout 30s build/audit_duals 32 108 9 "$count" < "$input"
timeout 30s build/irreducible 9 < "$input" | cmp - "$input"
timeout 45s python3 - "$input" "$src" "$count" <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[2])
from critical_witness import witness, check
count = 0
for key in Path(sys.argv[1]).read_text().splitlines():
    evidence = witness(key, 9)
    assert evidence and check(evidence) == (32, 108)
    count += len(evidence['after_deletion'])
assert count == 108 * int(sys.argv[3])
print(f'PASS {count} private independent-nine witnesses')
PY
sort -cu "$input"
sort -cu "$base/union.g6"
comm -12 "$input" "$base/union.g6" | cmp - /dev/null
tmp=$(mktemp -d "$out/replay.XXXXXX")
trap 'rm -rf "$tmp"' EXIT
timeout 30s ../../opt/bin/labelg -q "$input" | sort -u | cmp - "$input"
sort -mu "$input" "$previous" > "$tmp/critical.g6"
timeout 30s ../../opt/bin/shortg -tu "$tmp/critical.g6" 2> "$tmp/traces.log"
cat "$tmp/traces.log"
rg -qx ">Z $total_critical graphs produced" "$tmp/traces.log"
if [[ $mode == produce ]]; then
    mv "$tmp/critical.g6" "$merged"
    sort -mu "$input" "$base/union.g6" > "$out/union.g6"
    timeout 30s build/demand_clique 8 < "$input" > "$out/cliques.tsv"
    awk 'ARGIND==1 {covered[$1]=1; next} ! (FNR in covered) {print FNR "\t" $0}' \
        "$out/cliques.tsv" "$input" > "$out/complement.tsv"
    cut -f 2 "$out/complement.tsv" | timeout 30s build/demand_clique 7 > "$out/pins.tsv"
    timeout --kill-after=5s 3m python3 "$src/floor109_proofs.py" "$out/complement.tsv" "$out/proofs" "$out/pins.tsv" \
        > "$out/production.log"
else
    cmp "$tmp/critical.g6" "$merged"
    sort -mu "$input" "$base/union.g6" | cmp - "$out/union.g6"
fi
test "$(wc -l < "$out/union.g6")" -eq "$((prior_count + count))"
timeout 30s python3 "$verifier" "$input" "$out/cliques.tsv" --degree 7 --unproved "$out/complement.tsv"
find "$out/proofs" -maxdepth 1 -type f -name '*.lrat' -exec cp -t "$tmp" {} +
timeout --kill-after=5s 2m python3 "$src/floor109_proofs.py" "$out/complement.tsv" "$tmp" "$out/pins.tsv" \
    --replay --dual > "$tmp/replay.log"
awk '$1!="counts" {print $1,$2,$3}' "$out/production.log" > "$tmp/production.index"
awk '$1!="counts" {print $1,$2,$3}' "$tmp/replay.log" > "$tmp/replay.index"
cmp "$tmp/production.index" "$tmp/replay.index"
cmp <(cut -f 1 "$out/complement.tsv") <(awk '{print $1}' "$tmp/replay.index")
test "$(find "$tmp" -maxdepth 1 -name '*.lrat' -printf x | wc -c)" -eq "$(wc -l < "$out/complement.tsv")"
if [[ $mode == produce ]]; then
    cp "$tmp/replay.log" "$out/replay.log"
else
    cmp "$tmp/replay.log" "$out/replay.log"
fi
sha256sum "$input" "$merged" "$out/"{union.g6,cliques.tsv,complement.tsv,pins.tsv,production.log,replay.log}
printf 'PASS %s keys, %s cliques and %s dual LRATs; %s/2104151 supplied (%s missing)\n' \
    "$count" "$(wc -l < "$out/cliques.tsv")" "$(wc -l < "$out/complement.tsv")" \
    "$((prior_count+count))" "$((2104151-prior_count-count))"
