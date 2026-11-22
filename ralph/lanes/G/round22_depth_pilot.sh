#!/usr/bin/env bash
set -euo pipefail
root=$(realpath "$(dirname "$0")/../../..")
base="$root/scratch/G/round22/h5"
tools="$root/opt/bin"
export PYTHONDONTWRITEBYTECODE=1 LC_ALL=C OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 5242880
test "$PWD" = "$base"
board=$1
orig=$(printf 'b%03d' "$board")
test "$(cat "work/$orig/solve.status")" = 10
stem="depth$board"
mkdir "work/$stem"
cd "work/$stem"
run() {
    local name=$1 wall=$2 cpu=$3
    shift 3
    /usr/bin/time -o "$name.time" -f '%U %S %M %e %x' timeout --kill-after=3 "$wall" \
        prlimit --cpu="$cpu:$cpu" -- "$@"
}
gen() {
    run "$1" 90 65 "$root/opt/venv/bin/python" -B "$root/ralph/lanes/G/round22_deep.py" emit \
        "$base/manifest.json" "$board" --strength full+depth --old-model "$base/work/$orig/solve.log" \
        >"$1.cnf" 2>"$1.json"
}
gen grid
rc=0
run solve 95 65 prlimit --fsize=201326592:201326592 -- \
    "$tools/cadical" --lrat --no-binary grid.cnf grid.lrat >solve.log 2>&1 || rc=$?
printf '%s\n' "$rc" >solve.status
stat -c %s grid.lrat >raw.bytes
if test "$rc" -ne 20; then
    rm grid.lrat
    printf 'OPEN depth-pilot solver exit %s\n' "$rc" >result
    exit 0
fi
rg -x 's UNSATISFIABLE' solve.log
gen rebind
cmp grid.cnf rebind.cnf
cmp grid.json rebind.json
run lrat 80 60 "$tools/lrat-check" grid.cnf grid.lrat >lrat.log || true
run cake 80 60 "$tools/cake_lpr" --CML_HEAP_SIZE=512 --CML_STACK_SIZE=48 grid.cnf grid.lrat >cake.log || true
if ! rg -x 'c VERIFIED' lrat.log || ! rg -x 's VERIFIED UNSAT' cake.log; then
    rm grid.lrat
    printf 'OPEN depth proof did not verify\n' >result
    exit 0
fi
cp grid.json binding.json
sha256sum grid.cnf grid.lrat >sha256
(
    flock -x 9
    available=$(du -sb "$base/archive" | cut -f1)
    bytes=$(cat raw.bytes)
    test $((available + bytes + bytes / 100 + 64)) -le 4294967296
    run zstd 90 55 zstd -q -T1 -3 grid.lrat -o "$base/archive/$stem.lrat.zst.tmp"
    run expand 90 55 zstd -q -t "$base/archive/$stem.lrat.zst.tmp"
    mv "$base/archive/$stem.lrat.zst.tmp" "$base/archive/$stem.lrat.zst"
) 9>"$base/archive.lock"
stat -c %s "$base/archive/$stem.lrat.zst" >archived.bytes
sha256sum "$base/archive/$stem.lrat.zst" >>sha256
rm grid.lrat
printf 'CHECKED board=%s strength=full+depth split=\n' "$board" >result
