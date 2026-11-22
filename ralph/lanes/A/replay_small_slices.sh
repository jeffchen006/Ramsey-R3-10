#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
lane="$root/ralph/lanes/A"
prior="$root/scratch/A/r16"
weights="$root/scratch/A/r17-stream"
catalogue="$root/gluing/val"
mode=${1:-all}
[[ $mode = all || $mode = small || $mode = literal ]]
name=${2:-r18-replay}
[[ $name =~ ^r18(-[[:alnum:]_]+)?$ ]]
mkdir -p "$root/scratch/A/$name"
cd "$root/scratch/A/$name"
export TMPDIR="$PWD" LC_ALL=C
ulimit -v 524288 -f 262144 -c 0
run() {
    local tag=$1
    shift
    nice -n 5 timeout 120 prlimit --cpu=100:110 /usr/bin/time -o "$tag.time" -f '%U %S %e %M' "$@"
}
if [[ $mode = literal ]]; then
    test -s raw.cases.tsv && test -s raw.flags.tsv && test ! -e literal.oracle.tsv
    run build_oracle g++ -std=c++20 -O3 -Wall -Wextra -Werror "$lane/profile_oracle.cpp" -o oracle
    awk 'NR%97==1' raw.cases.tsv > price.cases.tsv
    awk 'NR%97==1' raw.flags.tsv > price.flags.tsv
    run price ./oracle pilot "$catalogue"/r3_6_{16,17}.g6 price.cases.tsv > price.oracle.tsv
    cmp price.flags.tsv price.oracle.tsv
    n=$(wc -l < raw.cases.tsv)
    ns=$(wc -l < price.cases.tsv)
    awk -v n="$n" -v ns="$ns" '{printf "literal sample: %d of %d, %.2f CPU-s, estimate %.2f CPU-s (not a tail bound)\n", ns,n,$1+$2,($1+$2)*n/ns}' price.time > literal-price.txt
    nice -n 5 timeout 390 prlimit --cpu=280:300 /usr/bin/time -o literal.time -f '%U %S %e %M' \
        ./oracle pilot "$catalogue"/r3_6_{16,17}.g6 raw.cases.tsv > literal.oracle.tsv
    cmp raw.flags.tsv literal.oracle.tsv
    printf 'literal: %s complete rows and all ordered group bits agree\n' "$n"
    exit
fi
test -z "$(ls -A)"
run build_gate g++ -std=c++20 -O3 -Wall -Wextra -Werror "$lane/slice_predicate.cpp" -o gate
mkdir small
cd small
small_args=("$root" "$prior"/small{6,7}.g6 "$prior"/small{6,7}.frames)
run prepare python3 -B "$lane/bind_small_slices.py" small queries "${small_args[@]}" > queries.tsv
run receipts ../gate "$prior"/small{6,7}.g6 5 4 2 < queries.tsv > receipts.tsv
run finish python3 -B "$lane/bind_small_slices.py" small finish "${small_args[@]}" > result.log
cat result.log
cd ..
if [[ $mode = all ]]; then
    run build_frames g++ -std=c++20 -O3 -Wall -Wextra -Werror "$lane/one_neutral_frames.cpp" -o frames
    for order in 16 17; do
        if [[ $order == 16 ]]; then count=2576; else count=7; fi
        run "frames$order" ./frames frames "$catalogue/r3_6_$order.g6" "$order" "$count" 4 9 5 5 0 "$count" |
            run "extract$order" python3 -B "$lane/bind_small_slices.py" extract "$catalogue/r3_6_$order.g6" \
                "$prior/count$order.tsv" > "selected$order.tsv" 2> "extract$order.log"
    done
    target_args=("$root" "$catalogue"/r3_6_{16,17}.g6 selected{16,17}.tsv "$weights"/weights{16,17}.tsv)
    run prepare python3 -B "$lane/bind_small_slices.py" target queries "${target_args[@]}" > queries.tsv
    run receipts ./gate "$catalogue"/r3_6_{16,17}.g6 9 5 4 < queries.tsv > receipts.tsv
    run finish python3 -B "$lane/bind_small_slices.py" target finish "${target_args[@]}" > result.log
    cat extract{16,17}.log result.log
fi
