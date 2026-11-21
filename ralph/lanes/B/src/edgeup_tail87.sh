#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
ulimit -v 16777216

source_dir=../../ralph/lanes/B/src
prior=work/edgeup2/up86
out=work/edgeup2/up87tail
prefix=val/r39_30_le88_mixed_prefix.g6
case ${1:-prefix} in
    prefix)
        rg -Fq 'exact e86 HoG equality and GR T14 lower-level counts checked; full through e=87' logs/prefix_pipeline.log
        ;;
    checkpoint)
        rg -Fxq 'e86 checkpoint exact HoG equality' logs/prefix_checkpoint_r4.log
        rg -Fxq 'e87 checkpoint union reaches exact published count' logs/prefix_checkpoint_r4.log
        rg -Fxq 'checked 147335 order-30 e87 duals, triangle-free and alpha<9, strictly ordered' logs/prefix_checkpoint_r4_full_valid.log
        timeout 2m sha256sum -c logs/prefix_checkpoint_r4.sha256
        timeout 2m cmp work/prefix_checkpoint_r4/e86.g6 work/hog_30_86.canon
        ;;
    *) exit 2 ;;
esac
timeout 5m bash "$source_dir/audit_e88_scans.sh" up86
mkdir "$out"
if [[ ${1:-prefix} == checkpoint ]]; then
    cp work/prefix_checkpoint_r4/union87.g6 "$out/all87.g6"
else
    timeout 5m ../../opt/bin/pickg -q -e87 "$prefix" "$out/all87.g6"
fi
timeout 5m python3 "$source_dir/ecount.py" "$out/all87.g6" 87:147335
timeout 5m sort -cu "$out/all87.g6"
timeout 5m sort -cu "$prior/e87.g6"
timeout 5m comm -23 "$prior/e87.g6" "$out/all87.g6" >"$out/bad.g6"
test ! -s "$out/bad.g6"
timeout 5m comm -23 "$out/all87.g6" "$prior/e87.g6" >"$out/tail87.g6"
timeout 5m python3 "$source_dir/ecount.py" "$out/tail87.g6" 87:13901
timeout 5m sort -m "$prior/e87.g6" "$out/tail87.g6" >"$out/check87.g6"
cmp "$out/check87.g6" "$out/all87.g6"
rm "$out/check87.g6"
printf 'e87 partition verified by exact merge: 133434 + 13901 = 147335\n'
/usr/bin/time -f 'edgeup CPU %U+%S wall %e' timeout 15m build/edgeup <"$out/tail87.g6" >"$out/e88.raw"
/usr/bin/time -f 'shortg CPU %U+%S wall %e' timeout 20m ../../opt/bin/shortg -q -Twork "$out/e88.raw" "$out/e88.g6"
rm "$out/e88.raw"
timeout 5m sort -cu "$out/e88.g6"
timeout 5m sort -cu "$prior/e88.g6"
timeout 5m comm -12 "$out/e88.g6" "$prior/e88.g6" >"$out/overlap88.g6"
timeout 5m comm -23 "$out/e88.g6" "$prior/e88.g6" >"$out/tail88.g6"
count=$(wc -l <"$out/tail88.g6")
overlap=$(wc -l <"$out/overlap88.g6")
timeout 5m sort -m "$out/overlap88.g6" "$out/tail88.g6" >"$out/check88.g6"
cmp "$out/check88.g6" "$out/e88.g6"
rm "$out/check88.g6"
printf 'tail87 e88 partition: %s overlap + %s novel (combined disjoint coverage %s)\n' "$overlap" "$count" "$((4751963+count))"
if (( count )); then
    timeout 10m python3 "$source_dir/ecount.py" "$out/tail88.g6" "88:$count"
fi
/usr/bin/time -f 'MTF scan CPU %U+%S wall %e' timeout 2h python3 "$source_dir/scan_mtf.py" "$out/tail88.g6" --workers 1 --edge 88 --label up87tail
timeout 2m python3 "$source_dir/audit_chunks.py" work/mtf_up87tail_e88 9 "$count" 1024 --bind "$out/tail88.g6"
cmp "$out/tail88.g6" work/mtf_up87tail_e88/inputs.g6
sha256sum "$out/all87.g6" "$prior/e87.g6" "$out/tail87.g6" "$prior/e88.g6" "$out/tail88.g6"
printf 'up87tail terminal; all %s novel canonical e88 inputs scanned\n' "$count"
