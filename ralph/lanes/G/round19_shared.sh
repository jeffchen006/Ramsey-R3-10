#!/usr/bin/env bash
set -euo pipefail
root=$(realpath "$(dirname "$0")/../../..")
src="$root/scratch/ideas/r018_N"
work=${2:-"$root/scratch/G/round19"}
cd "$work"
ulimit -v 524288
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 LC_ALL=C TMPDIR="$PWD"
py="$root/opt/venv/bin/python"
impl="$root/ralph/lanes/G/round19_shared.py"
tools="$root/opt/bin"
bound() { nice -n 5 timeout --kill-after=2 60 prlimit --cpu=60:60 -- "$@"; }
checks() {
    bound "$tools/lrat-check" "$1" "$2" >"$3.lrat-check"
    rg -x 'c VERIFIED' "$3.lrat-check"
    bound "$tools/cake_lpr" --CML_HEAP_SIZE=128 --CML_STACK_SIZE=32 "$1" "$2" >"$3.cake"
    rg -x 's VERIFIED UNSAT' "$3.cake"
}
baseline() {
    (cd "$src"; sha256sum -c FREEZE.sha256) >scout.hashes
    bound g++ -std=c++20 -O3 "$src/ghost.cc" -o ghost
    bound "$py" -B "$impl" control
    bound "$py" -B "$impl" leaf
    checks "$src/broad.8.cnf" "$src/broad.8.lrat" leaf
    bound "$py" -B "$impl" emit >middle.cnf
    bound "$py" -B "$impl" audit
    bound "$py" -B "$impl" crosswalk
    bound "$py" -B "$impl" preregister
}
case ${1:-} in
    baseline) baseline ;;
    target)
        test "$PWD" = "$root/scratch/G/round19"
        sha256sum -c target-gate.sha256
        test ! -e middle.lrat && test ! -e solve.status
        rc=0
        /usr/bin/time -f '%U %S %M %e %x' -o solve.time nice -n 5 timeout --kill-after=2 45 \
            prlimit --cpu=30:30 --fsize=100663296:100663296 -- \
            "$tools/cadical" -t 39 --lrat --no-binary middle.cnf middle.lrat >solve.log 2>&1 || rc=$?
        printf '%s\n' "$rc" >solve.status
        test "$rc" = 20
        rg -x 's UNSATISFIABLE' solve.log
        bound "$py" -B "$impl" audit
        checks middle.cnf middle.lrat middle
        ;;
    review)
        baseline
        retained="$root/scratch/G/round19"
        for artifact in middle.cnf physical.tsv crosswalk.json outstanding-if-verified.json h7-prereg.json; do
            cmp "$artifact" "$retained/$artifact"
        done
        checks middle.cnf "$retained/middle.lrat" middle
        ;;
    *) exit 2 ;;
esac
