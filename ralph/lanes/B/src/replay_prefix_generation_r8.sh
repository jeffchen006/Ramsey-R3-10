#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

src=../../ralph/lanes/B/src
pickg=../../opt/bin/pickg
out=work/prefix_r8_generation
mkdir -p "$out"
mode=${1:?control, prepare, or target}
chunk=128
total=0
bind() {
    local degree=$1 source=$2 upper=$3 size=$4
    local bound="$out/$mode.d$degree.g6" hashes expected
    timeout 1m "$pickg" -q "-e0:$upper" "$source" "$bound"
    test "$(wc -l < "$bound")" -eq "$size"
    expected=$(((size+chunk-1)/chunk))
    hashes=$(rg -l '^input_sha256=' "$directory/d${degree}_"*.log | wc -l) || test "$hashes" -eq 0
    local options=(--multi-degree)
    if (( hashes == expected )); then
        options+=(--bind "$bound")
    else
        [[ $mode != control && $hashes == 0 ]]
        printf 'Legacy d%s logs have no input digests: counts only; exact seed hashes recorded now, sample replay separate\n' "$degree"
    fi
    timeout 1m python3 "$src/audit_chunks.py" "$directory" "$degree" "$size" "$chunk" "${options[@]}"
    total=$((total+expected))
    sha256sum "$bound"
}

case "$mode" in
    control)
        export PYTHONPATH=$src
        family=prefix_r8_control16
        directory=work/$family
        timeout 1m python3 - <<'PY'
from pathlib import Path
from seed import filtered, generate

cases = []
for degree in (1, 2, 3):
    inner = 15-degree
    stem = filtered(Path(f'val/r3_6_{inner}.g6'), 22-degree*degree)
    args = ['build/glue5', '-k', 6, '-d', degree, '-e', 22]
    cases.append((degree, stem, args))
generate('prefix_r8_control16', cases, 128, 1, '20:2,21:15,22:201')
PY
        bind 1 val/r3_6_14.g6 21 17
        bind 2 val/r3_6_13.g6 18 425
        bind 3 val/r3_6_12.g6 13 25
        cmp "val/$family.g6" val/r37_16_le22.g6
        ;;
    prepare|target)
        family=r39_30_le88_mixed_prefix
        directory=work/$family
        bind 5 val/r38_24_le58.g6 58 132817
        bind 6 val/r38_23_le52.g6 51 364384
        bind 7 val/r38_22_le44.g6 42 21
        ;;
    *) exit 2 ;;
esac

test "$(find "$directory" -maxdepth 1 -type f -name '*.canon' -printf x | wc -c)" -eq "$total"
if [[ $mode == prepare ]]; then
    timeout --kill-after=5s 8m sort -mu --batch-size=256 --buffer-size=256M -T "$out" "$directory/"*.canon > "$out/independent.tmp"
    mv "$out/independent.tmp" "$out/independent.g6"
    sha256sum "$out/independent.g6"
    printf 'PASS independent merge from %s audited chunks; supervisor comparison pending\n' "$total"
else
    timeout --kill-after=5s 8m sort -mu --batch-size=256 --buffer-size=256M -T "$out" "$directory/"*.canon | cmp - "val/$family.g6"
    sha256sum "val/$family.g6"
    printf 'PASS %s generation: independent sorted canonical union (%s audited chunks)\n' "$mode" "$total"
fi
