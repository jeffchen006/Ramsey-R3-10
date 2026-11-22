#!/usr/bin/env bash
set -euo pipefail
root=$(realpath "$(dirname "$0")/../../..")
src="$root/ralph/lanes/G"
stage="$root/scratch/G/round24"
test "$PWD" = "$stage"
export PYTHONDONTWRITEBYTECODE=1 LC_ALL=C OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 5242880
board=$1 prefix=$2
work="h4-price-$board-$prefix"
mkdir "$work"
cd "$work"
run() {
    local name=$1 cpu=$2
    shift 2
    /usr/bin/time -o "$name.time" -f '%U %S %M %e %x' timeout --foreground --kill-after=5 "$((3 * cpu + 15))" \
        prlimit --cpu="$cpu:$cpu" -- "$@"
}
trap 'rm -f binary.tmp' EXIT
run generate 45 "$root/opt/venv/bin/python" -B "$src/round24_h4.py" emit "$stage/inventory-16.json" "$board" "$prefix" >grid.cnf 2>binding.json
rc=0
run solve 75 prlimit --fsize=65000000:65000000 -- "$root/opt/bin/cadical" --lrat --binary grid.cnf binary.tmp >solve.log 2>&1 || rc=$?
size=0
if test -f binary.tmp; then size=$(stat -c %s binary.tmp); fi
printf 'Board %s/%s: exit=%s binary bytes=%s\n' "$board" "$prefix" "$rc" "$size" | tee result
if test "$rc" != 20 || test "$size" -ge 65000000; then
    printf 'OPEN no checked proof\n' | tee -a result
    exit 0
fi
if run pack 70 bash -o pipefail -c '"$1" "$2" binary.tmp /dev/stdout | prlimit --fsize=35000000:35000000 -- zstd -q -T1 -3 -o grid.lrat.zst' bash \
   "$root/scratch/G/round23/trim/binary_lrat" "$(awk 'NR==1 {print $4}' grid.cnf)" &&
   run checker1 70 bash -o pipefail -c 'zstd -qdc grid.lrat.zst | { "$1" grid.cnf; code=$?; cat >/dev/null; exit "$code"; }' bash "$root/opt/bin/lrat-check" >lrat.log &&
   run checker2 70 bash -o pipefail -c 'zstd -qdc grid.lrat.zst | { "$1" --CML_HEAP_SIZE=512 --CML_STACK_SIZE=48 grid.cnf /dev/stdin; code=$?; cat >/dev/null; exit "$code"; }' bash "$root/opt/bin/cake_lpr" >cake.log &&
   rg -qx 'c VERIFIED' lrat.log && rg -qx 's VERIFIED UNSAT' cake.log; then
    sha256sum grid.cnf grid.lrat.zst >sha256
    printf 'local CNF cert; pending independent h4 formula binding\n' | tee -a result
else
    printf 'OPEN proof transport or checker failed\n' | tee -a result
fi
