#!/usr/bin/env bash
set -euo pipefail
root=$(realpath "$(dirname "$0")/../../..")
base="$root/scratch/G/round22"
impl="$root/ralph/lanes/G/round22_fold.py"
tools="$root/opt/bin"
python="$root/opt/venv/bin/python"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 LC_ALL=C
ulimit -v 5242880
test "$PWD" = "$base"
mkdir -p archive
rawcap=335544320
if test "$1" = pilot; then cpu=100; wall=165; else cpu=900; wall=1800; fi
run() {
    local timer=$1 limit=$2 seconds=$3 rc=0
    shift 3
    /usr/bin/time -o "$timer" -f '%U %S %M %e %x' timeout --kill-after=5 "$limit" \
      prlimit --cpu="$seconds:$seconds" -- "$@" || rc=$?
    return "$rc"
}
one() (
    set -euo pipefail
    local board=$1 id=$2 strength=$3
    shift 3
    local folder="$base/work/$id" rc=0 bytes=0 open='' token
    mkdir -p "$base/work"
    mkdir "$folder" || exit 104
    cd "$folder" || exit 104
    printf '%s %s %s %s\n' "$board" "$id" "$strength" "$*" >job
    date -Is >start
    export TMPDIR="$PWD"
    if test "$(df -B1 --output=avail . | tail -1)" -lt 100000000000; then
        printf 'OPEN free-space guard\n' >result; return 0
    fi
    if ! run gen.time 125 65 "$python" -B "$impl" emit "$base/manifest.json" "$board" --strength "$strength" "$@" >grid.cnf 2>binding.json; then
        printf 'OPEN generator failed\n' >result
        exit 105
    fi
    run solve.time "$wall" "$cpu" prlimit --fsize="$rawcap:$rawcap" -- \
        "$tools/cadical" --lrat --no-binary grid.cnf grid.lrat >solve.log 2>&1 || rc=$?
    printf '%s\n' "$rc" >solve.status
    if test -f grid.lrat; then bytes=$(stat -c %s grid.lrat); fi
    printf '%s\n' "$bytes" >raw.bytes
    if test "$rc" != 20; then
        case "$rc" in
            10) open='SAT relaxation model (not a graph verdict)' ;;
            124) open='wall timeout' ;;
            153) open='raw proof cap' ;;
            137|152) open='SIGKILL/resource signal, consult solve.log; no claim' ;;
            *) open="solver exit $rc" ;;
        esac
        if test "$bytes" -eq "$rawcap"; then open="raw proof cap (exit $rc)"; fi
        rm -f grid.lrat
        printf 'OPEN %s\n' "$open" >result
        return 0
    fi
    if ! rg -x 's UNSATISFIABLE' solve.log ||
        ! run rebind.time 125 65 "$python" -B "$impl" emit "$base/manifest.json" "$board" --strength "$strength" "$@" >rebind.cnf 2>rebind.json ||
        ! cmp grid.cnf rebind.cnf || ! cmp binding.json rebind.json; then
        printf 'OPEN unsat/rebind receipt absent; raw proof retained\n' >result
        exit 105
    fi
    rm rebind.cnf rebind.json
    run lrat.time 230 150 "$tools/lrat-check" grid.cnf grid.lrat >lrat.log || open='lrat-check exit'
    if ! rg -x 'c VERIFIED' lrat.log; then open='lrat-check receipt absent'; fi
    run cake.time 230 150 "$tools/cake_lpr" --CML_HEAP_SIZE=512 --CML_STACK_SIZE=48 grid.cnf grid.lrat >cake.log || open='cake_lpr exit'
    if ! rg -x 's VERIFIED UNSAT' cake.log; then open='cake_lpr receipt absent'; fi
    sha256sum grid.cnf grid.lrat >sha256 || exit 105
    (
        flock -x 9
        token=$(du -sb "$base/archive" | cut -f1)
        if test $((token + bytes + bytes / 100 + 64)) -gt 5368709120; then exit 100; fi
        run zstd.time 155 95 zstd -q -T1 -3 grid.lrat -o "$base/archive/$id.lrat.zst.tmp" || exit 101
        run expand.time 90 60 zstd -q -t "$base/archive/$id.lrat.zst.tmp" || exit 102
        mv "$base/archive/$id.lrat.zst.tmp" "$base/archive/$id.lrat.zst"
    ) 9>"$base/archive.lock" || rc=$?
    if test "$rc" -ne 20; then
        printf 'OPEN archive failure exit %s; raw proof retained\n' "$rc" >result
        exit 105
    fi
    stat -c %s "$base/archive/$id.lrat.zst" >archived.bytes || exit 105
    sha256sum "$base/archive/$id.lrat.zst" >>sha256 || exit 105
    rm grid.lrat
    if test -n "$open"; then
        printf 'OPEN %s; compressed proof retained\n' "$open" >result
    else
        printf 'CHECKED board=%s strength=%s split=%s\n' "$board" "$strength" "$*" >result
    fi
    date -Is >end
)
case "$1" in
    pilot)
        shift
        one "$@"
        ;;
    shard)
        shard=$2
        queue=$3
        sha256sum -c launch.sha256
        while read -r owner board id strength side slot sign; do
            test "$owner" = "$shard" || continue
            rc=0
            if test "$side" = '-'; then
                one "$board" "$id" "$strength" || rc=$?
            else
                one "$board" "$id" "$strength" --split "$side" "$slot" "$sign" || rc=$?
            fi
            if test "$rc" -ne 0; then
                printf 'OPEN wrapper exit %s %s\n' "$rc" "$id"
            fi
            if test -f "work/$id/result"; then cat "work/$id/result"; fi
            if test "$rc" -ne 0; then exit "$rc"; fi
        done < "$queue"
        ;;
    *) exit 2 ;;
esac
