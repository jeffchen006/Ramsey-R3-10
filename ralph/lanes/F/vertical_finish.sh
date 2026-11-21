#!/usr/bin/env bash
set -euo pipefail
lane=../../../ralph/lanes/F
for index in 0 1; do
    mapfile -t hits < <(awk -F '\t' 'FNR>1 { print FILENAME, $1, $2, $3 }' target"$index"_[1-4]_24.tsv)
    [[ ${#hits[@]} == 1 ]]
    read -r source row score graph <<< "${hits[0]}"
    [[ $score == 24 ]]
    hit="tie$index"
    sed -n "$((row + 1))p" "${source%_24.tsv}.q" > "$hit.q"
    printf '%s\n' "$graph" > "$hit.g6"
    ../build/relift_v2 "$hit.q" 10 23 6 9 161 180 200000 "$hit.tsv" > "$hit.log"
    python3 -B "$lane/relift_audit.py" audit "$hit.q" "$hit.tsv" "$hit.log" 10 23
    [[ $(tail -n 1 "$hit.log") == 'END rows=1 no=1 yes=0 cap=0 filter=0' ]]
    seed="$lane/round4_seed40_24.g6"
    if [[ $index == 1 ]]; then seed="$lane/round4_seed40_24_e179.g6"; fi
    ../../../opt/bin/labelg -q "$seed" "$hit.seed.canon.g6"
    ../../../opt/bin/labelg -q "$hit.g6" "$hit.canon.g6"
    cmp "$hit.seed.canon.g6" "$hit.canon.g6"
    printf 'PASS %s row=%s exact I10=%s; isomorphic to %s\n' "$source" "$row" "$score" "$seed"
done
for index in 0 1; do
    for part in 1 2 3 4; do
        stem="target${index}_${part}_24"
        awk '/^END/{print FILENAME, $0}' "$stem.log"
    done
done
cat target[01]_[1-4].q | LC_ALL=C sort > target_all.sorted.q
LC_ALL=C uniq -d target_all.sorted.q > target_duplicates.q
[[ ! -s target_duplicates.q && $(wc -l < target_all.sorted.q) == 4196 ]]
cat ../r6/full{0,1}.q ../r6/switchTarget{0,1}.q ../r6/sparseExtensions.new.q | LC_ALL=C sort -u > prior.sorted.q
LC_ALL=C comm -12 prior.sorted.q target_all.sorted.q > target_overlap.q
[[ ! -s target_overlap.q ]]
printf 'PASS 4196 distinct target rows, no overlap with round-6 rows\n'
sha256sum "$lane/vertical_trade.py" "$lane/vertical_finish.sh" "$lane/relift.cpp" \
    "$lane/round4_seed40_24.g6" "$lane/round4_seed40_24_e179.g6" \
    ../r1/fast38_m2.found.g6 ../r2/record38b.found.g6 ../r6/sparse.distinct.g6 \
    ../r6/sparseExtensions.new.q ../r6/full{0,1}.q ../r6/switchTarget{0,1}.q \
    ctl[01]_[1-4].{q,expected,log,tsv} ctl{0,1}.gate \
    target[01]_[1-4].q target[01]_[1-4]_24.{log,tsv} tie[01].{q,log,g6,canon.g6} > round7.sha256
