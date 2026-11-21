#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
source "$root/opt/env.sh"
cd "$root/scratch/A/tests"
ulimit -v 16777216

python3 - <<'PY'
from itertools import combinations
clauses = [[pigeon * 5 + hole + 1 for hole in range(5)] for pigeon in range(6)]
clauses += [[-first * 5 - hole - 1, -second * 5 - hole - 1]
            for first, second in combinations(range(6), 2) for hole in range(5)]
with open('php6_5.cnf', 'w') as out:
    print('p cnf 30', len(clauses), file=out)
    for clause in clauses:
        print(*clause, 0, file=out)
PY

unsat() {
    local status=0
    nice -n 5 timeout 30 "$@" || status=$?
    test "$status" -eq 20
}
cadical --version
kissat --version
unsat cadical -q php6_5.cnf cadical.drat
unsat cadical -q --lrat --binary=false php6_5.cnf cadical.lrat
unsat kissat -q php6_5.cnf kissat.drat
nice -n 5 timeout 30 drat-trim php6_5.cnf cadical.drat | tee cadical.drat.log
nice -n 5 timeout 30 drat-trim php6_5.cnf kissat.drat | tee kissat.drat.log
nice -n 5 timeout 30 lrat-check php6_5.cnf cadical.lrat | tee cadical.lrat.log
nice -n 5 timeout 30 cake_lpr --CML_HEAP_SIZE=128 --CML_STACK_SIZE=32 php6_5.cnf cadical.lrat | tee php.cake.log
tr -d '\r' <cadical.drat.log | grep -x 's VERIFIED'
tr -d '\r' <kissat.drat.log | grep -x 's VERIFIED'
grep -qx 'c VERIFIED' cadical.lrat.log
grep -qx 's VERIFIED UNSAT' php.cake.log
