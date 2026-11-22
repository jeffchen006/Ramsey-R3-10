#!/usr/bin/env bash
set -euo pipefail
root=$(realpath "$(dirname "$0")/../../..")
src="$root/ralph/lanes/G"
previous="$root/scratch/G/round22/h5"
prior="$root/scratch/G/round23"
opt="$root/opt/bin"
python="$root/opt/venv/bin/python"
stage="$root/scratch/G/round24"
test "$PWD" = "$stage"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 LC_ALL=C
ulimit -v 5242880
board=$1 prefix=$2 mode=$3 id=$4 bcap=$5 acap=$6 cpu=$7 lcpu=$8
mkdir "$stage/work/$id"
cd "$stage/work/$id"
export TMPDIR="$PWD"
printf '%s %s %s %s\n' "$board" "$prefix" "$mode" "$id" >job
date -Is >start
finish() { printf '%s\n' "$*" >result.tmp; mv result.tmp result; }
trap 'rm -f binary.lrat "$stage/archive/$id.lrat.zst.tmp"' EXIT
run() {
    local timer=$1 limit=$2 seconds=$3
    shift 3
    /usr/bin/time -o "$timer" -f '%U %S %M %e %x' timeout --foreground --kill-after=5 "$limit" \
        prlimit --cpu="$seconds:$seconds" -- "$@"
}
if test "$(df -B1 --output=avail . | tail -1)" -lt 100000000000; then
    finish 'OPEN free-space guard'; exit 0
fi
args=("$previous/manifest.json" "$board" "$prefix" --deficit)
if [[ $mode == *M* ]]; then
    : >witness.jsonl
    for seed in "$prior/seeds/$board.jsonl" "$prior/seeds-follow/$board.jsonl" "$stage/seeds/$board.jsonl"; do
        if test -f "$seed"; then cat "$seed" >>witness.jsonl; fi
    done
    args+=(--witnesses "$PWD/witness.jsonl")
    rc=0
    run learn.time "$((lcpu * 3 + 15))" "$lcpu" prlimit --fsize=2500000:2500000 -- \
        "$python" -B "$src/round23_deficit.py" learn "${args[@]}" --rounds 1000 --conflicts 250000 >learn.log 2>&1 || rc=$?
    printf '%s\n' "$rc" >learn.status
    rg '"graph":' learn.log >graph.json || true
    if test -s graph.json; then finish 'OPEN physical model to verify'; exit 0; fi
fi
if ! run gen.time 95 55 "$python" -B "$src/round23_deficit.py" emit "${args[@]}" >grid.cnf 2>binding.json ||
   ! run audit.time 95 55 "$python" -B "$src/round23_deficit_audit.py" "$previous/manifest.json" "$previous" "$board" "$prefix" "$mode" >audit.log 2>&1; then
    finish 'OPEN formula/binding failure'; exit 0
fi
rc=0
run solve.time "$((cpu * 3 + 20))" "$cpu" prlimit --fsize="$bcap:$bcap" -- \
    "$opt/cadical" --lrat --binary grid.cnf binary.lrat >solve.log 2>&1 || rc=$?
printf '%s\n' "$rc" >solve.status
bytes=0
if test -f binary.lrat; then bytes=$(stat -c %s binary.lrat); fi
printf '%s\n' "$bytes" >raw.bytes
if test "$bytes" -ge "$bcap"; then finish "OPEN raw cap (solver exit $rc)"; exit 0; fi
if test "$rc" = 10; then finish 'OPEN SAT relaxation'; exit 0; fi
if test "$rc" != 20 || ! rg -qx 's UNSATISFIABLE' solve.log; then
    finish "OPEN solver exit $rc"; exit 0
fi
clauses=$(awk 'NR==1{print $4}' grid.cnf)
packed="$stage/archive/$id.lrat.zst.tmp"
if ! run convert.time 220 130 bash -o pipefail -c \
    '"$1" "$2" binary.lrat /dev/stdout | prlimit --fsize="$3:$3" -- zstd -q -T1 -3 -o "$4"' \
    bash "$prior/trim/binary_lrat" "$clauses" "$acap" "$packed" >convert.log 2>&1; then
    finish 'OPEN conversion/compression cap or failure'; exit 0
fi
sha256sum binary.lrat >binary.sha256
rm binary.lrat
if ! run lrat.time 280 160 bash -o pipefail -c 'zstd -qdc "$1" | { "$2" grid.cnf; code=$?; cat >/dev/null; exit "$code"; }' bash "$packed" "$opt/lrat-check" >lrat.log ||
   ! rg -qx 'c VERIFIED' lrat.log ||
   ! run cake.time 280 160 bash -o pipefail -c 'zstd -qdc "$1" | { "$2" --CML_HEAP_SIZE=512 --CML_STACK_SIZE=48 grid.cnf /dev/stdin; code=$?; cat >/dev/null; exit "$code"; }' bash "$packed" "$opt/cake_lpr" >cake.log ||
   ! rg -qx 's VERIFIED UNSAT' cake.log; then
    finish 'OPEN proof checker failure'; exit 0
fi
sha256sum grid.cnf >sha256
run digest.time 120 75 bash -o pipefail -c 'zstd -qdc "$1" | sha256sum' bash "$packed" | sed 's/  -$/  grid.lrat/' >>sha256
mv "$packed" "$stage/archive/$id.lrat.zst"
stat -c %s "$stage/archive/$id.lrat.zst" >archived.bytes
sha256sum "$stage/archive/$id.lrat.zst" >>sha256
date -Is >end
finish "CHECKED $board $prefix $mode $id"
