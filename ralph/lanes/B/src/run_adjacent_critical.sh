#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

input=${1:?order-32 parents}
prior=${2:?sorted canonical prior of e108 graphs}
out=${3:?new output directory}
workers=${4:-1}
skipped=${5:-/dev/null}
[[ $workers =~ ^[1-8]$ ]]
mkdir "$out"
sort -cu "$prior"
sort -cu "$skipped"
sha256sum "$input" "$prior" "$skipped" build/{adjacent_stems,adjacent_critical}
shortg=../../opt/bin/shortg
/usr/bin/time -f 'extract CPU %U+%S wall %e' build/adjacent_stems 4 8 108 < "$input" > "$out/raw.g6"
/usr/bin/time -f 'stem canon CPU %U+%S wall %e' "$shortg" -q -T"$out" "$out/raw.g6" "$out/all.stems.g6"
comm -23 "$out/all.stems.g6" "$skipped" > "$out/stems.g6"
rm "$out/raw.g6"
split -n "l/$workers" -d "$out/stems.g6" "$out/shard."
cat "$out"/shard.* | cmp - "$out/stems.g6"
pids=()
for shard in "$out"/shard.*; do
    /usr/bin/time -f 'pair CPU %U+%S wall %e' build/adjacent_critical 8 4 108 \
        < "$shard" > "$shard.results" 2> "$shard.log" &
    pids+=("$!")
done
failed=0
for pid in "${pids[@]}"; do
    if ! wait "$pid"; then failed=1; fi
done
cat "$out"/shard.*.log
test "$failed" -eq 0
processed=$(awk '/^Adjacent critical bases=/{ split($3, entry, "="); total+=entry[2] } END { print total+0 }' "$out"/shard.*.log)
test "$processed" -eq "$(wc -l < "$out/stems.g6")"
/usr/bin/time -f 'output canon CPU %U+%S wall %e' "$shortg" -q -T"$out" \
    <(cat "$out"/shard.*.results) "$out/outputs.g6"
comm -23 "$out/outputs.g6" "$prior" > "$out/new.g6"
delta=$(wc -l < "$out/new.g6")
if (( delta )); then
    build/audit_duals 32 108 9 "$delta" < "$out/new.g6"
    build/irreducible 9 < "$out/new.g6" | cmp - "$out/new.g6"
    "$shortg" -t -u -T"$out" "$out/new.g6" 2> "$out/traces.log"
    rg -Fxq ">Z $delta graphs produced" "$out/traces.log"
fi
sha256sum "$out/"{stems,outputs,new}.g6
printf 'PASS total_stems=%s tested=%s results=%s new_critical=%s\n' \
    "$(wc -l < "$out/all.stems.g6")" "$processed" "$(wc -l < "$out/outputs.g6")" "$delta"
