#!/usr/bin/env bash
set -euo pipefail
root=$(realpath "$(dirname "$0")/../../..")
scout="$root/scratch/ideas/r018_N"
retained="$root/scratch/G/round20"
work=${2:-"$retained"}
cd "$work"
ulimit -v 524288
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 LC_ALL=C TMPDIR="$PWD"
py="$root/opt/venv/bin/python"
impl="$root/ralph/lanes/G/round20_matching.py"
tools="$root/opt/bin"
bound() { nice -n 5 timeout --kill-after=2 45 prlimit --cpu=45:45 -- "$@"; }
checks() {
    bound "$tools/lrat-check" "$1" "$2" >"$3.lrat-check"
    rg -x 'c VERIFIED' "$3.lrat-check"
    bound "$tools/cake_lpr" --CML_HEAP_SIZE=128 --CML_STACK_SIZE=32 "$1" "$2" >"$3.cake"
    rg -x 's VERIFIED UNSAT' "$3.cake"
}
baseline() {
    (cd "$root"; sha256sum -c ralph/lanes/G/ROUND19_FREEZE.sha256) >r19.hashes
    (cd "$scout"; sha256sum -c FREEZE.sha256) >scout.hashes
    bound g++ -std=c++20 -O3 "$scout/ghost.cc" -o ghost
    bound "$py" -B "$impl" control
    bound "$py" -B "$impl" emit >matching.cnf
    bound "$py" -B "$impl" audit
    bound "$py" -B "$impl" crosswalk
    checks "$scout/broad.8.cnf" "$scout/broad.8.lrat" leaf
    checks "$root/scratch/G/round19/middle.cnf" "$root/scratch/G/round19/middle.lrat" middle
}
case ${1:-} in
    baseline) baseline ;;
    target)
        test "$PWD" = "$retained"
        (cd "$root"; sha256sum -c "$retained/target-gate.sha256")
        test ! -e matching.lrat && test ! -e solve.status
        rc=0
        /usr/bin/time -f '%U %S %M %e %x' -o solve.time nice -n 5 timeout --kill-after=2 45 \
            prlimit --cpu=30:30 --fsize=100663296:100663296 -- \
            "$tools/cadical" -t 39 --lrat --no-binary matching.cnf matching.lrat >solve.log 2>&1 || rc=$?
        printf '%s\n' "$rc" >solve.status
        test "$rc" = 20
        rg -x 's UNSATISFIABLE' solve.log
        bound "$py" -B "$impl" audit
        checks matching.cnf matching.lrat matching
        ;;
    review)
        baseline
        for artifact in matching.cnf matching-physical.tsv matching-crosswalk.json matching-debit-if-verified.json outstanding-if-verified.json; do
            cmp "$artifact" "$retained/$artifact"
        done
        checks matching.cnf "$retained/matching.lrat" matching
        ;;
    *) exit 2 ;;
esac
