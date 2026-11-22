#!/usr/bin/env bash
set -euo pipefail
root=$(realpath "$(dirname "$0")/../../..")
scout="$root/scratch/ideas/r018_N"
retained="$root/scratch/G/round21"
lane="$root/ralph/lanes/G"
work=${2:-"$retained"}
cd "$work"
ulimit -v 524288
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 TMPDIR="$PWD"
py="$root/opt/venv/bin/python"
tools="$root/opt/bin"
impl="$lane/round21_h7.py"
clock() {
    local file=$1
    shift
    /usr/bin/time -f '%U %S %M %e %x' -o "$file" nice -n 5 \
        timeout --kill-after=2 45 prlimit --cpu=30:30 -- "$@"
}
proof_clock() {
    local file=$1
    shift
    clock "$file" prlimit --fsize=50331648:50331648 -- "$@"
}
staging() {
    local bytes
    bytes=$(du --apparent-size -sb "$retained" | cut -f1)
    if [[ $PWD != "$retained" ]]; then
        bytes=$((bytes + $(du --apparent-size -sb . | cut -f1)))
    fi
    (( bytes + ${1:-0} <= 469762048 ))
}
proof_check() {
    local folder=$1 proof=$2
    clock "$folder/lrat.time" "$tools/lrat-check" "$folder/grid.cnf" "$proof" >"$folder/lrat.log"
    rg -x 'c VERIFIED' "$folder/lrat.log"
    clock "$folder/cake.time" "$tools/cake_lpr" --CML_HEAP_SIZE=128 --CML_STACK_SIZE=32 \
        "$folder/grid.cnf" "$proof" >"$folder/cake.log"
    rg -x 's VERIFIED UNSAT' "$folder/cake.log"
}
prepare() {
    local pilot=$1 folder=p$1
    mkdir -p "$folder"
    staging 1048576
    clock "$folder/gen.time" "$py" -B "$impl" emit "$pilot" >"$folder/grid.cnf"
    clock "$folder/audit.time" "$py" -B "$impl" audit "$pilot" "$folder/grid.cnf" >"$folder/audit.log"
    cat "$folder/audit.log"
}
baseline() {
    (cd "$root"; sha256sum -c "$lane/ROUND19_FREEZE.sha256") >r19.hashes
    (cd "$scout"; sha256sum -c FREEZE.sha256) >scout.hashes
    clock build.time g++ -std=c++20 -O3 "$scout/ghost.cc" -o ghost
    clock orbits.time "$py" -B "$impl" orbits
    clock control.time "$py" -B "$impl" control
}
case ${1:-} in
    preflight)
        test "$PWD" = "$retained"
        baseline
        for pilot in {1..8}; do prepare "$pilot"; done
        ;;
    target)
        test "$PWD" = "$retained"
        (cd "$root"; sha256sum -c "$retained/target-gate.sha256")
        for pilot in {1..8}; do
            folder=p$pilot
            staging 52428800
            test ! -e "$folder/grid.lrat" && test ! -e "$folder/solve.status"
            rc=0
            proof_clock "$folder/solve.time" "$tools/cadical" -t 39 --lrat --no-binary \
                "$folder/grid.cnf" "$folder/grid.lrat" >"$folder/solve.log" 2>&1 || rc=$?
            printf '%s\n' "$rc" >"$folder/solve.status"
            test "$rc" = 20
            rg -x 's UNSATISFIABLE' "$folder/solve.log"
            staging
            clock "$folder/rebind.time" "$py" -B "$impl" emit "$pilot" >"$folder/rebind.cnf"
            cmp "$folder/grid.cnf" "$folder/rebind.cnf"
            rm "$folder/rebind.cnf"
            clock "$folder/rebind-audit.time" "$py" -B "$impl" audit "$pilot" "$folder/grid.cnf" >"$folder/rebind-audit.log"
            cmp "$folder/audit.log" "$folder/rebind-audit.log"
            proof_check "$folder" "$folder/grid.lrat"
            printf '%s\n' 'regenerated, semantically rebound, both LRAT checkers accepted' >"$folder/checked"
            printf 'pilot %s checked; proof %s bytes\n' "$pilot" "$(wc -c <"$folder/grid.lrat")"
        done
        ;;
    debit)
        clock debit.time "$py" -B "$impl" debit
        ;;
    review)
        test "$PWD" != "$retained"
        baseline
        cmp presolve-sets.json "$retained/presolve-sets.json"
        for pilot in {1..8}; do
            folder=p$pilot
            test -f "$retained/$folder/checked" || break
            prepare "$pilot"
            cmp "$folder/grid.cnf" "$retained/$folder/grid.cnf"
            cmp "$folder/audit.log" "$retained/$folder/audit.log"
            proof_check "$folder" "$retained/$folder/grid.lrat"
            cp "$retained/$folder/checked" "$folder/checked"
        done
        clock debit.time "$py" -B "$impl" debit
        cmp checked-union.json "$retained/checked-union.json"
        ;;
    *) exit 2 ;;
esac
