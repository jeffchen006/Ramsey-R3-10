#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

input=${1:?ordered canonical input}
prior=${2:?ordered canonical prior}
out=${3:?output stem}
/usr/bin/time -f 'lateral CPU %U+%S wall %e' timeout 12m build/lateral_critical 8 4 < "$input" > "$out.raw"
/usr/bin/time -f 'canonical CPU %U+%S wall %e' timeout 6m ../../opt/bin/shortg -q -Twork/e162_r5 "$out.raw" "$out.g6"
rm "$out.raw"
sort -cu "$out.g6"
sort -cu "$prior"
comm -23 "$out.g6" "$prior" > "$out.new.g6"
sort -mu "$out.new.g6" "$prior" > "$out.union.g6"
wc -l "$input" "$out.g6" "$out.new.g6" "$out.union.g6"
sha256sum "$input" "$prior" "$out.new.g6" "$out.union.g6"
