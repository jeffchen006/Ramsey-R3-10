#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
python=../../opt/venv/bin/python
src=../../ralph/lanes/B/src
out=work/prefix_r8_sat
mkdir -p "$out"

timeout --kill-after=3s 30s "$python" "$src/satverify.py" work/c35_dual.g6 1 7 8 8 8 8 > "$out/control.log"
rg -q '^0 SAT ' "$out/control.log"
if [[ ${1:-} == control ]]; then
    cat "$out/control.log"
    exit 0
fi
[[ ${1:-} == target ]]
input=${2:-work/prefix_r7_replay/prefix.critical.g6}
count=$(wc -l < "$input")
if (( count == 0 )); then
    printf 'No prefix-critical keys to sample\n'
    exit 0
fi
if (( count > 24 )); then count=24; fi
timeout 30s "$python" "$src/sample_levels.py" "$input" 30 88 "$count" 8820261122 > "$out/sample.g6"
timeout --kill-after=5s 3m "$python" "$src/satverify.py" "$out/sample.g6" "$count" 8 9 6 9 9 > "$out/target.log"
cat "$out/target.log"
test "$(rg -c '^[0-9]+ UNSAT ' "$out/target.log")" -eq "$count"
test "$(rg -c '^[0-9]+ (UNSAT|SAT) ' "$out/target.log")" -eq "$count"
sha256sum "$input" "$out/sample.g6"
printf 'PASS independent SAT sample of %s prefix-critical e88 keys; not proof logging\n' "$count"
