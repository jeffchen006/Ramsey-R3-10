#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

source_dir=../../ralph/lanes/B/src
directory=work/e162_r5
input="$directory/lateral2.union.g6"
trace="$directory/lateral2.hex"
timeout 30s sha256sum -c ../../ralph/lanes/B/E162_E107.sha256
/usr/bin/time -f 'validity CPU %U+%S wall %e' timeout 3m build/audit_duals 32 107 9 234681 < "$input"
/usr/bin/time -f 'Traces CPU %U+%S wall %e' timeout 3m ../../opt/bin/shortg -t -u -T"$directory" "$input" 2> "$directory/audit.traces"
cat "$directory/audit.traces"
rg -q '^>Z 234681 graphs read ' "$directory/audit.traces"
rg -qx '>Z 234681 graphs produced' "$directory/audit.traces"
/usr/bin/time -f 'pair replay CPU %U+%S wall %e' timeout 3m build/row_support 67 "$trace" < "$input"
/usr/bin/time -f 'SAT sample CPU %U+%S wall %e' timeout 2m \
    ../../opt/venv/bin/python "$source_dir/sat_row_support.py" "$input" "$trace" 64
printf 'e162 adjacent-degree-seven: complete e107 replay passed\n'
