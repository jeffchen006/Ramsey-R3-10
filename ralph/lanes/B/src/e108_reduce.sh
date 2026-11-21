#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

directory=work/e108_r5
parent=work/e162_r5/lateral2.union.g6
source=../../ralph/lanes/B
timeout 1m sha256sum -c "$source/E162_E107.sha256"
test "$(wc -l < "$parent")" -eq 234681
rg -qx 'complete e107 cover: 231455 demand cliques plus 3226 rebuilt, dual-checked LRATs' logs/e107_floor108_replay.log
/usr/bin/time -f 'edgeup CPU %U+%S wall %e' timeout 5m build/edgeup < "$parent" > "$directory/reducible.raw"
/usr/bin/time -f 'canonical CPU %U+%S wall %e' timeout 7m ../../opt/bin/shortg -q -T"$directory" "$directory/reducible.raw" "$directory/reducible.g6"
rm "$directory/reducible.raw"
count=$(wc -l < "$directory/reducible.g6")
test "$count" -le 2104151
/usr/bin/time -f 'direct audits CPU %U+%S wall %e' timeout 4m build/audit_duals 32 108 9 "$count" < "$directory/reducible.g6"
sha256sum "$parent" "$directory/reducible.g6"
printf 'complete reducible e108 partition: %s of 2104151, critical complement %s\n' "$count" "$((2104151-count))"
