#!/bin/bash
set -euo pipefail
lane=$(cd "$(dirname "$0")" && pwd); root=$(cd "$lane/../../.." && pwd); py=$root/opt/venv/bin/python
case "$PWD" in "$root"/scratch/*/*);; *) echo 'Use an empty scratch directory in your own lane';exit 2;; esac
test -z "$(ls -A .)"; export TMPDIR=$PWD PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1;ulimit -v 1048576;ulimit -f 32768
run(){ nice -n 5 timeout "$1" prlimit --cpu="$2" -- "${@:3}"; }
run 80 65 g++ -std=c++17 -O3 -march=native "$lane/chart_sieve24.cpp" -o sieve
run 90 75 "$py" -B "$lane/chart_bank24.py"; run 60 50 "$py" -B "$lane/chart_ctl24.py"
mkdir fixed shape; (cd fixed;run 90 70 g++ -std=c++17 -O3 -march=native -DORDERED24 "$lane/fixed24.cpp" -o ordered;export F_CARDS24_BIN=$PWD/ordered;run 70 55 "$py" -B "$lane/fixed_small24.py";run 180 150 "$py" -B "$lane/cards24.py" control)
(cd shape;run 90 70 g++ -std=c++17 -O3 -march=native "$lane/shape24.cpp" -o pattern;export F_SOURCE24_BIN=$PWD/pattern;run 120 100 "$py" -B "$lane/source24.py" control;run 80 65 "$py" -B "$lane/shapes_check24.py")
run 90 75 "$py" -B "$lane/audit24.py"; echo 'clean controls, chart census and tail binder passed'
