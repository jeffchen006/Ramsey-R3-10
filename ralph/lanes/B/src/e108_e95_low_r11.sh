#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
ulimit -t 300
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
out=${1:?new output directory}
main=work/e108_r11
opt=../../opt/bin
src=../../ralph/lanes/B/src
input=work/hog_31_95.canon
mkdir "$out"
export TMPDIR="$PWD/$out"
canon() { timeout 60s "$opt/labelg" -q | sort -u; }
timed() { /usr/bin/time -f 'CPU user=%U sys=%S wall=%e' "$@"; }
for degree in 4 5; do
    timeout 20s "$main/stitch" 6 22 "$degree" < "$main/control/small.parents" > "$out/control.$degree.raw"
    cmp "$out/control.$degree.raw" "$main/control/small.$degree.raw"
    test -s "$out/control.$degree.raw"
done
timeout 20s build/audit_duals 31 95 9 560 < "$input"
timeout 20s build/irreducible 9 < "$input" | cmp - "$input"
timeout 20s "$opt/shortg" -tu "$input" 2> "$out/traces.log"
rg -qx '>Z 560 graphs produced' "$out/traces.log"
timeout 20s python3 "$src/stratified_g6.py" 32 r11-e95-low < "$input" | sort > "$out/sample.g6"
test "$(wc -l < "$out/sample.g6")" -eq 32
comm -23 "$input" "$out/sample.g6" > "$out/rest.g6"
test "$(wc -l < "$out/rest.g6")" -eq 528
mkdir "$out/sample" "$out/rest"
for degree in 4 5; do
    { timed timeout 30s "$main/stitch" 8 108 "$degree" < "$out/sample.g6" > "$out/sample/$degree.raw"; } 2> "$out/sample/$degree.log"
    cat "$out/sample/$degree.log"
    awk '/^CPU / { split($2,u,"="); split($3,s,"="); forecast=(u[2]+s[2])*528/32; print "remaining CPU-s forecast", forecast; exit (forecast>110) }' "$out/sample/$degree.log"
    { timed timeout --kill-after=5s 3m "$main/stitch" 8 108 "$degree" < "$out/rest.g6" > "$out/rest/$degree.raw"; } 2> "$out/rest/$degree.log"
    cat "$out/rest/$degree.log"
    rg -q '^inputs 32 ' "$out/sample/$degree.log"
    rg -q '^inputs 528 ' "$out/rest/$degree.log"
    cat "$out/sample/$degree.raw" "$out/rest/$degree.raw" | canon > "$out/$degree.g6"
    comm -23 "$out/$degree.g6" "$main/union.g6" > "$out/$degree.novel"
    wc -l "$out/$degree."{g6,novel}
done
sort -mu "$out/"{4,5}.g6 > "$out/keys.g6"
sort -mu "$out/"{4,5}.novel > "$out/novel.g6"
sha256sum "$out/"{sample.g6,rest.g6,keys.g6,novel.g6}
