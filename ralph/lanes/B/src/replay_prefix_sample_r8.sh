#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

directory=work/r39_30_le88_mixed_prefix
seeds=work/prefix_r8_generation
out=work/prefix_r8_chunk_samples
mkdir "$out"
replay() {
    local degree=$1 index=$2 binary=$3 start end stem
    start=$((index*128+1))
    end=$((start+127))
    printf -v stem 'd%s_%05d' "$degree" "$index"
    sed -n "${start},${end}p;${end}q" "$seeds/prepare.d$degree.g6" > "$out/$stem.in"
    /usr/bin/time -f 'CPU %U+%S wall %e' timeout --kill-after=5s 12m prlimit --cpu=350:355 -- \
        "build/$binary" -k 8 -d "$degree" -m 2 -M 8 -e 88 < "$out/$stem.in" > "$out/$stem.raw" 2> "$out/$stem.log"
    timeout 30s ../../opt/bin/shortg -q -T"$out" "$out/$stem.raw" "$out/$stem.canon"
    cmp "$out/$stem.canon" "$directory/$stem.canon"
    printf 'PASS replay %s\n' "$stem"
    tail -n 1 "$out/$stem.log"
    sha256sum "$out/$stem.in" "$out/$stem.canon"
}

pids=()
replay 5 0 gluepair & pids+=("$!")
replay 6 1423 gluetrans & pids+=("$!")
replay 7 0 glue5 & pids+=("$!")
status=0
for pid in "${pids[@]}"; do wait "$pid" || status=1; done
test "$status" -eq 0
printf 'PASS all three independently reconstructed legacy chunk samples\n'
