#!/usr/bin/env bash
set -euo pipefail
root=$(realpath "$(dirname "$0")/../../..")
base="$root/scratch/G/round23"
previous="$root/scratch/G/round22/h5"
impl=${IMPLEMENTATION:-"$root/ralph/lanes/G/round23_h5.py"}
auditor=${AUDITOR:-"$root/ralph/lanes/G/round23_h5_audit.py"}
python="$root/opt/venv/bin/python"
tools="$root/opt/bin"
manifest="$previous/manifest.json"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 LC_ALL=C
ulimit -v 5242880
test "$PWD" = "$base"
mkdir -p work archive
rawcap=${RAW_CAP:-268435456}
archivecap=${ARCHIVE_CAP:-2650000000}
learn_cpu=${LEARN_CPU:-95}
solve_cpu=${SOLVE_CPU:-220}
solve_wall=${SOLVE_WALL:-540}

run() {
    local timer=$1 limit=$2 seconds=$3 rc=0
    shift 3
    /usr/bin/time -o "$timer" -f '%U %S %M %e %x' timeout --kill-after=5 "$limit" \
        prlimit --cpu="$seconds:$seconds" -- "$@" || rc=$?
    return "$rc"
}

one() (
    set -euo pipefail
    local board=$1 prefix=$2 mode=$3 id=$4 rc=0 bytes=0 used state
    local -a options=()
    mkdir "$base/work/$id"
    cd "$base/work/$id"
    export TMPDIR="$PWD"
    printf '%s %s %s %s\n' "$board" "$prefix" "$mode" "$id" >job
    date -Is >start
    if test "$(df -B1 --output=avail . | tail -1)" -lt 100000000000; then
        printf 'OPEN free-space guard\n' >result
        return 0
    fi
    if [[ $mode == *B* ]]; then options+=(--budget); fi
    if [[ $mode == *D* ]]; then options+=(--deficit); fi
    if [[ $mode == *M* ]]; then
        options+=(--witnesses "$PWD/witness.jsonl")
        if test -f "$base/seeds/$board.jsonl"; then
            cp "$base/seeds/$board.jsonl" witness.jsonl
        else
            : >witness.jsonl
        fi
        run learn.time "$((learn_cpu * 2 + 5))" "$learn_cpu" "$python" -B "$impl" learn "$manifest" "$board" "$prefix" \
            "${options[@]}" --rounds 750 --conflicts 250000 >learn.log 2>&1 || rc=$?
        printf '%s\n' "$rc" >learn.status
        grep -E '"graph":' learn.log >graph.json || true
        if test -s graph.json; then
            printf 'OPEN candidate-like model; check graph separately\n' >result
            return 0
        fi
    fi
    if ! run gen.time 95 55 "$python" -B "$impl" emit "$manifest" "$board" "$prefix" "${options[@]}" >grid.cnf 2>binding.json; then
        printf 'OPEN generator/binder error\n' >result
        return 0
    fi
    if ! run audit.time 75 45 "$python" -B "$auditor" "$manifest" "$previous" "$board" "$prefix" "$mode" >audit.log 2>&1; then
        printf 'OPEN independent delta audit failed\n' >result
        return 0
    fi
    rc=0
    run solve.time "$solve_wall" "$solve_cpu" prlimit --fsize="$rawcap:$rawcap" -- \
        "$tools/cadical" --lrat --no-binary grid.cnf grid.lrat >solve.log 2>&1 || rc=$?
    printf '%s\n' "$rc" >solve.status
    if test -f grid.lrat; then bytes=$(stat -c %s grid.lrat); fi
    printf '%s\n' "$bytes" >raw.bytes
    if test "$bytes" -ge "$rawcap"; then
        sha256sum grid.lrat >failed-raw.sha256
        rm grid.lrat
        printf 'OPEN raw cap (%s bytes; solver exit %s)\n' "$bytes" "$rc" >result
        return 0
    fi
    if test "$rc" != 20; then
        rm -f grid.lrat
        case "$rc" in
            10) state='SAT relaxation (not a graph verdict)' ;;
            124) state='wall timeout' ;;
            137|152) state='resource signal (consult solve.log)' ;;
            *) state="solver exit $rc" ;;
        esac
        printf 'OPEN %s\n' "$state" >result
        return 0
    fi
    if ! rg -qx 's UNSATISFIABLE' solve.log ||
       ! run regenerate.time 95 55 "$python" -B "$impl" emit "$manifest" "$board" "$prefix" "${options[@]}" >rebind.cnf 2>rebind.json ||
       ! cmp -s grid.cnf rebind.cnf || ! cmp -s binding.json rebind.json; then
        rm -f rebind.cnf rebind.json grid.lrat
        printf 'OPEN missing UNSAT or rebind receipt\n' >result
        return 0
    fi
    rm rebind.cnf rebind.json
    state=''
    run lrat.time 220 130 "$tools/lrat-check" grid.cnf grid.lrat >lrat.log || state='lrat-check exit'
    if ! rg -qx 'c VERIFIED' lrat.log; then state='lrat-check receipt absent'; fi
    run cake.time 220 130 "$tools/cake_lpr" --CML_HEAP_SIZE=512 --CML_STACK_SIZE=48 grid.cnf grid.lrat >cake.log || state='cake_lpr exit'
    if ! rg -qx 's VERIFIED UNSAT' cake.log; then state='cake_lpr receipt absent'; fi
    sha256sum grid.cnf grid.lrat >sha256
    if test -n "$state"; then
        rm grid.lrat
        printf 'OPEN %s\n' "$state" >result
        return 0
    fi
    rc=0
    (
        flock -x 9
        used=$(du -sb "$base/archive" | cut -f1)
        if test "$used" -ge "$archivecap"; then exit 100; fi
        run zstd.time 140 85 prlimit --fsize="$((archivecap - used)):$((archivecap - used))" -- \
            zstd -q -T1 -3 grid.lrat -o "$base/archive/$id.lrat.zst.tmp" || exit 101
        run expand.time 85 55 zstd -q -t "$base/archive/$id.lrat.zst.tmp" || exit 102
        mv "$base/archive/$id.lrat.zst.tmp" "$base/archive/$id.lrat.zst"
    ) 9>"$base/archive.lock" || rc=$?
    if test "$rc" != 0; then
        rm -f "$base/archive/$id.lrat.zst.tmp" grid.lrat
        printf 'OPEN archive envelope exit %s\n' "$rc" >result
        return 0
    fi
    stat -c %s "$base/archive/$id.lrat.zst" >archived.bytes
    sha256sum "$base/archive/$id.lrat.zst" >>sha256
    rm grid.lrat
    date -Is >end
    printf 'CHECKED %s %s %s %s\n' "$board" "$prefix" "$mode" "$id" >result
)

case "$1" in
    pilot)
        shift
        one "$@"
        ;;
    shard)
        shard=$2
        queue=$3
        sha256sum --quiet -c "$queue.sha256"
        while read -r owner board prefix mode id; do
            test "$owner" = "$shard" || continue
            rc=0
            ( set -e; one "$board" "$prefix" "$mode" "$id" ) || rc=$?
            if test "$rc" -ne 0; then printf 'OPEN wrapper failed: %s %s\n' "$rc" "$id"; fi
            if test -f "work/$id/result"; then cat "work/$id/result"; fi
        done < "$queue"
        ;;
    *) exit 2 ;;
esac
