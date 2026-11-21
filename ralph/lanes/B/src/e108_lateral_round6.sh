#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

input=${1:?canonical inputs}
prior=${2:?ordered canonical prior}
out=${3:?new output directory}
workers=${4:-4}
[[ $workers =~ ^[1-4]$ ]]
mkdir "$out"
sort -cu "$prior"
sha256sum "$input" "$prior" build/{lateral_critical,irreducible,audit_duals}
split -n "l/$workers" -d "$input" "$out/in."
cat "$out"/in.* | cmp - "$input"
pids=()
for shard in "$out"/in.*; do
    /usr/bin/time -f 'swap CPU %U+%S wall %e' timeout --kill-after=15s 12m build/lateral_critical 8 4 \
        < "$shard" > "$shard.raw" 2> "$shard.log" &
    pids+=("$!")
done
failed=0
for pid in "${pids[@]}"; do
    if ! wait "$pid"; then failed=1; fi
done
cat "$out"/in.*.log
test "$failed" -eq 0
parents=$(awk '/^lateral graphs=/{ split($2, entry, "="); total+=entry[2] } END { print total+0 }' "$out"/in.*.log)
test "$parents" -eq "$(wc -l < "$input")"
count=$(wc -l < "$prior")
/usr/bin/time -f 'canon CPU %U+%S wall %e' timeout --kill-after=15s 6m ../../opt/bin/shortg -q -T"$out" \
    <(cat "$out"/in.*.raw) "$out/swap.g6"
rm "$out"/in.*.raw
sort -cu "$out/swap.g6"
comm -23 "$out/swap.g6" "$prior" > "$out/new.g6"
delta=$(wc -l < "$out/new.g6")
if (( delta )); then
    timeout 2m build/audit_duals 32 108 9 "$delta" < "$out/new.g6"
    timeout 2m build/irreducible 9 < "$out/new.g6" | cmp - "$out/new.g6"
fi
sort -mu "$prior" "$out/new.g6" > "$out/union.g6"
test "$(wc -l < "$out/union.g6")" -eq "$((count+delta))"
sha256sum "$out/new.g6" "$out/union.g6"
printf 'PASS parents=%s prior=%s delta=%s union=%s\n' "$parents" "$count" "$delta" "$((count+delta))"
