#!/usr/bin/env bash
set -euo pipefail
root=$(realpath "$(dirname "$0")/../../..")
base="$root/scratch/G/round23"
past="$root/scratch/G/round22/h5"
tools="$root/opt/bin"
src="$root/ralph/lanes/G"
test "$PWD" = "$base"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 LC_ALL=C
ulimit -v 5242880
bin_cap=${BIN_CAP:-160000000}
ascii_cap=${ASCII_CAP:-420000000}
archive_cap=${ARCHIVE_CAP:-3150000000}
cpu=${SOLVE_CPU:-320}

run() {
    local timer=$1 limit=$2 seconds=$3 rc=0
    shift 3
    /usr/bin/time -o "$timer" -f '%U %S %M %e %x' timeout --kill-after=5 "$limit" \
        prlimit --cpu="$seconds:$seconds" -- "$@" || rc=$?
    return "$rc"
}

test "$1" = pilot
origin="$base/work/$2"
id=$3
read -r board prefix mode old < "$origin/job"
test "$old" = "$2"
rg -q '^OPEN (raw|archive|resource|wall)' "$origin/result"
mkdir "$base/work/$id"
cd "$base/work/$id"
export TMPDIR="$PWD"
printf '%s %s %s %s\n' "$board" "$prefix" "$mode" "$id" >job
date -Is >start
if test "$(df -B1 --output=avail . | tail -1)" -lt 100000000000; then
    printf 'OPEN free-space guard\n' >result
    exit 0
fi
args=(emit "$past/manifest.json" "$board" "$prefix")
impl="$src/round23_h5.py"
audit="$src/round23_h5_audit.py"
if [[ $mode == *D* ]]; then
    args+=(--deficit)
    impl="$src/round23_deficit.py"
    audit="$src/round23_deficit_audit.py"
fi
if [[ $mode == *B* ]]; then args+=(--budget); fi
if [[ $mode == *M* ]]; then
    cp "$origin/witness.jsonl" witness.jsonl
    args+=(--witnesses "$PWD/witness.jsonl")
fi
if ! run gen.time 95 55 "$root/opt/venv/bin/python" -B "$impl" "${args[@]}" >grid.cnf 2>binding.json ||
   ! cmp -s grid.cnf "$origin/grid.cnf" || ! cmp -s binding.json "$origin/binding.json" ||
   ! run audit.time 95 55 "$root/opt/venv/bin/python" -B "$audit" "$past/manifest.json" "$past" "$board" "$prefix" "$mode" >audit.log 2>&1; then
    printf 'OPEN binary CNF rebind failed\n' >result
    exit 0
fi
rc=0
run solve.time "$((cpu * 3 + 20))" "$cpu" prlimit --fsize="$bin_cap:$bin_cap" -- \
    "$tools/cadical" --lrat --binary grid.cnf binary.lrat >solve.log 2>&1 || rc=$?
printf '%s\n' "$rc" >solve.status
test ! -f binary.lrat || stat -c %s binary.lrat >raw.bytes
if test "$rc" != 20 || ! rg -qx 's UNSATISFIABLE' solve.log ||
   test "$(cat raw.bytes 2>/dev/null || printf 0)" -ge "$bin_cap"; then
    rm -f binary.lrat
    printf 'OPEN binary solve exit %s/cap\n' "$rc" >result
    exit 0
fi
count=$(awk 'NR==1{print $4}' grid.cnf)
if ! run convert.time 130 75 prlimit --fsize="$ascii_cap:$ascii_cap" -- \
   "$base/trim/binary_lrat" "$count" binary.lrat grid.lrat >convert.log 2>&1; then
    rm -f binary.lrat grid.lrat
    printf 'OPEN binary conversion failed/capped\n' >result
    exit 0
fi
sha256sum binary.lrat >binary.sha256
rm binary.lrat
stat -c %s grid.lrat >converted.bytes
if ! run lrat.time 280 160 "$tools/lrat-check" grid.cnf grid.lrat >lrat.log ||
   ! rg -qx 'c VERIFIED' lrat.log ||
   ! run cake.time 280 160 "$tools/cake_lpr" --CML_HEAP_SIZE=512 --CML_STACK_SIZE=48 grid.cnf grid.lrat >cake.log ||
   ! rg -qx 's VERIFIED UNSAT' cake.log; then
    rm -f grid.lrat
    printf 'OPEN binary proof checker failed\n' >result
    exit 0
fi
sha256sum grid.cnf grid.lrat >sha256
rc=0
(
    flock -x 9
    used=$(du -sb "$base/archive" | cut -f1)
    if test "$used" -ge "$archive_cap"; then exit 100; fi
    run zstd.time 160 90 prlimit --fsize="$((archive_cap-used)):$((archive_cap-used))" -- \
        zstd -q -T1 -4 grid.lrat -o "$base/archive/$id.lrat.zst.tmp" || exit 101
    run expand.time 100 60 zstd -q -t "$base/archive/$id.lrat.zst.tmp" || exit 102
    mv "$base/archive/$id.lrat.zst.tmp" "$base/archive/$id.lrat.zst"
) 9>"$base/archive.lock" || rc=$?
if test "$rc" != 0; then
    rm -f "$base/archive/$id.lrat.zst.tmp" grid.lrat
    printf 'OPEN archive envelope exit %s\n' "$rc" >result
    exit 0
fi
stat -c %s "$base/archive/$id.lrat.zst" >archived.bytes
sha256sum "$base/archive/$id.lrat.zst" >>sha256
rm grid.lrat
date -Is >end
printf 'CHECKED %s %s %s %s\n' "$board" "$prefix" "$mode" "$id" >result
