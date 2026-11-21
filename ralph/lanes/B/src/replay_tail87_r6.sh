#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

source_dir=../../ralph/lanes/B/src
prior=work/edgeup2/up86
tail=work/edgeup2/up87tail
out=work/up87_r6_replay
mkdir -p "$out"
add() {
    timeout 1m python3 "$source_dir/replay_edge_children.py" < "$1" |
        timeout 2m ../../opt/bin/shortg -q -T"$out" - "$2"
}
control=work/round4_tail_control
add "$control/all20.g6" "$out/control21.g6"
cmp "$out/control21.g6" "$control/prior21.g6"
cmp "$tail/all87.g6" work/prefix_checkpoint_r4/union87.g6
comm -23 "$prior/e87.g6" "$tail/all87.g6" > "$out/invalid87.g6"
test ! -s "$out/invalid87.g6"
comm -23 "$tail/all87.g6" "$prior/e87.g6" > "$out/fresh_tail87.g6"
cmp "$out/fresh_tail87.g6" "$tail/tail87.g6"
add "$out/fresh_tail87.g6" "$out/fresh88.g6"
cmp "$out/fresh88.g6" "$tail/e88.g6"
comm -12 "$out/fresh88.g6" "$prior/e88.g6" | cmp - "$tail/overlap88.g6"
comm -23 "$out/fresh88.g6" "$prior/e88.g6" | cmp - "$tail/tail88.g6"
test "$(wc -l < "$tail/tail88.g6")" -eq 967613
sha256sum "$tail/"{all87,tail87,overlap88,tail88}.g6
printf 'PASS independent e87/e88 incidence replay: 13901 parents, 967613 e88 keys disjoint from up86\n'
if [[ ${1:-} == terminal ]]; then
    rg -Fxq 'MTF up87tail e=88 checked all input chunks; output 0 graphs' logs/up87tail_checkpoint.log
    rg -Fxq 'up87tail terminal; all 967613 novel canonical e88 inputs scanned' logs/up87tail_checkpoint.log
    timeout 3m bash "$source_dir/audit_e88_scans.sh" up86
    timeout 2m python3 "$source_dir/audit_chunks.py" work/mtf_up87tail_e88 9 967613 1024 --bind "$tail/tail88.g6"
    cmp "$tail/tail88.g6" work/mtf_up87tail_e88/inputs.g6
    printf 'PASS terminal zero: all 5719576 deletion-reducible e88 classes scanned by disjoint up86 and tail87 batches\n'
fi
