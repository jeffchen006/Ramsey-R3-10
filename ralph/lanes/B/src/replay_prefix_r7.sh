#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

source_dir=../../ralph/lanes/B/src
pickg=../../opt/bin/pickg
out=work/prefix_r7_replay
mkdir -p "$out"

partition() {
    local universe=$1 reducible=$2 target=$3
    sort -cu "$universe"
    sort -cu "$reducible"
    comm -23 "$universe" "$reducible" > "$target"
    local count common critical
    count=$(wc -l < "$universe")
    common=$(comm -12 "$universe" "$reducible" | wc -l)
    critical=$(wc -l < "$target")
    test "$count" -eq "$((critical+common))"
    printf 'Prefix partition: total=%s reducible=%s critical=%s\n' "$count" "$common" "$critical"
}

if [[ ${1:-} == control ]]; then
    control=work/round4_tail_control
    partition "$control/all22.g6" "$control/reducible22.g6" "$out/control.critical.g6"
    cmp "$out/control.critical.g6" "$control/critical22.g6"
    build/irreducible 7 < "$out/control.critical.g6" | cmp - "$out/control.critical.g6"
    printf 'PASS exact order-16/e22 critical partition\n'
    exit 0
fi

[[ $# == 1 && ( $1 == lower || $1 == terminal ) ]]
input=val/r39_30_le88_mixed_prefix.g6
test -s "$input"
sort -cu "$input"
"$pickg" -q -e86 "$input" "$out/e86.g6"
"$pickg" -q -e87 "$input" "$out/e87.g6"
cmp "$out/e86.g6" work/prefix_checkpoint_r4/e86.g6
cmp "$out/e87.g6" work/prefix_checkpoint_r4/union87.g6
"$pickg" -q -e0:87 "$input" "$out/lower.g6"
sort -mu "$out/e86.g6" "$out/e87.g6" | cmp - "$out/lower.g6"
python3 "$source_dir/ecount.py" "$out/lower.g6" '86:1800,87:147335'
sha256sum "$out/"{e86,e87,lower}.g6
printf 'PASS independently materialized full <=87 prefix equals checkpoint byte-for-byte\n'
if [[ $1 == lower ]]; then exit 0; fi

rg -Fxq 'MTF prefix e=88 checked all input chunks; output 0 graphs' logs/prefix_pipeline.log
"$pickg" -q -e88 "$input" "$out/e88.g6"
cmp "$out/e88.g6" work/mtf_prefix_e88/inputs.g6
count=$(wc -l < "$out/e88.g6")
python3 "$source_dir/audit_chunks.py" work/mtf_prefix_e88 9 "$count" 1024 --bind "$out/e88.g6"
sort -mu work/edgeup2/up86/e88.g6 work/edgeup2/up87tail/tail88.g6 > "$out/reducible.g6"
test "$(wc -l < "$out/reducible.g6")" -eq 5719576
test -f val/d7_e43_outside_prefix.g6
test ! -s val/d7_e43_outside_prefix.g6
partition "$out/e88.g6" "$out/reducible.g6" "$out/prefix.critical.g6"
critical=$(wc -l < "$out/prefix.critical.g6")
if (( critical )); then
    build/audit_duals 30 88 9 "$critical" < "$out/prefix.critical.g6"
    build/irreducible 9 < "$out/prefix.critical.g6" | cmp - "$out/prefix.critical.g6"
fi
sha256sum "$out/e88.g6" "$out/prefix.critical.g6"
printf 'PASS only the prefix-critical keys are newly bound; the outside-prefix critical complement still requires d6/e52 or d7/e44\n'
