#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1 TMPDIR=$PWD/work

scout=../ideas/astra_N
catalogues=../G/round4
known=work/e108_r8_import/critical1756.g6
out=${1:?new output directory}
limit=${2:?per-family host limit}
[[ $limit =~ ^[1-9][0-9]*$ ]]
mkdir "$out"
shortg=../../opt/bin/shortg
run() { timeout --kill-after=5s 90s "$@"; }
canon() { run "$shortg" -q -T"$out" "$1" "$2"; }
sha256sum "$scout/descend.c" "$known"
run gcc -O3 -march=native -Wall -Wextra -o "$out/descend" "$scout/descend.c" -I../../ralph/lanes/B/src
run "$out/descend" 3 6 < ../../gluing/val/r3_4_8.g6 > "$out/control.raw.g6"
run "$shortg" -tq -T"$out" "$out/control.raw.g6" "$out/control.g6"
run ../../opt/bin/pickg -q -e6 ../../gluing/val/r3_4_7.g6 - | run "$shortg" -tq -T"$out" > "$out/control.ref.g6"
cmp "$out/control.g6" "$out/control.ref.g6"
test "$(wc -l < "$out/control.g6")" -eq 1

cat "$scout/"{sample121,sample122,stratified,sample5,five33}.g6 \
    ../../ralph/lanes/G/root_certs/complete33_le119.g6 > "$out/scout.raw.g6"
canon "$out/scout.raw.g6" "$out/excluded.g6"
for spec in 120:e120.frozen.from121 121:e121.frozen 122:all122.latest 123:edgecritical123.up; do
    level=${spec%:*}
    host="$catalogues/${spec#*:}.g6"
    sha256sum "$host"
    canon "$host" "$out/$level.source.g6"
    comm -23 "$out/$level.source.g6" "$out/excluded.g6" > "$out/$level.population.g6"
    size=$(wc -l < "$out/$level.population.g6")
    test "$size" -gt 0
    awk -v total="$size" -v cap="$limit" 'BEGIN { count=cap<total ? cap : total; slot=0 }
        NR==int((slot+0.5)*total/count)+1 && slot<count { print; ++slot }
        END { if (slot!=count) exit 2 }' "$out/$level.population.g6" > "$out/$level.hosts.g6"
    hosts=$(wc -l < "$out/$level.hosts.g6")
    timeout 30s build/audit_duals 33 "$level" 9 "$hosts" < "$out/$level.hosts.g6"
    /usr/bin/time -f 'descent CPU %U+%S wall %e' timeout --kill-after=5s 90s "$out/descend" 8 108 \
        < "$out/$level.hosts.g6" > "$out/$level.raw.g6"
    canon "$out/$level.raw.g6" "$out/$level.canon.g6"
    comm -23 "$out/$level.canon.g6" "$known" > "$out/$level.new.g6"
    printf 'e%s: population=%s hosts=%s direct=%s novel=%s\n' "$level" "$size" "$hosts" \
        "$(wc -l < "$out/$level.canon.g6")" "$(wc -l < "$out/$level.new.g6")"
done
sort -mu "$out/"{120,121,122,123}.new.g6 > "$out/new.g6"
novel=$(wc -l < "$out/new.g6")
if (( novel )); then
    timeout 30s build/audit_duals 32 108 9 "$novel" < "$out/new.g6"
    timeout 30s build/irreducible 9 < "$out/new.g6" | cmp - "$out/new.g6"
fi
sha256sum "$out/"{120,121,122,123}.hosts.g6 "$out/new.g6"
printf 'PASS direct pilot: %s distinct novel keys\n' "$novel"
