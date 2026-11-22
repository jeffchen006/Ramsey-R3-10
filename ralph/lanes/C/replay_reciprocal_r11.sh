#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
lane="$root/ralph/lanes/C"
py="$root/opt/venv/bin/python"
work="$root/scratch/C/${R310_C_REPLAY_DIR:-r11-replay}"
test "$(realpath -m "$work")" = "$work"
test "$work" != "$root/scratch/C"
mkdir -p "$work"
cd "$work"
ulimit -v 16777216
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 TMPDIR="$PWD"
run() { nice -n 5 timeout "$@"; }

case "$1" in
    prepare)
        test ! -e inputs.tsv
        { sed '/^int main(/,$d' "$lane/reciprocal_stream.cpp"; cat "$lane/reciprocal_stream_batch.inc"; } > reciprocal_combined.cpp
        run 60 g++ -std=c++20 -O3 -mpopcnt -Wall -Wextra reciprocal_combined.cpp -o reciprocal_stream
        run 60 "$py" -B "$lane/reciprocal_census.py" prepare
        run 110 bash "$lane/reciprocal_census_worker.sh" controls > controls.log
        for prefix in cal-10.g6 cal-11.g6 cal-planted.tsv; do
            ln -s "$root/scratch/C/r10/$prefix" "$prefix"
        done
        ;;
    worker)
        run 1800 bash "$lane/reciprocal_census_worker.sh" stream "$2"
        run 3700 bash "$lane/reciprocal_census_worker.sh" audit "$2"
        ;;
    audit)
        run 3700 bash "$lane/reciprocal_census_worker.sh" audit "$2"
        ;;
    live)
        rg --sort path --no-heading --glob maps.tsv '^.* live 0$' > live.tsv
        run 170 "$py" -B "$lane/reciprocal_live.py" > live.log
        run 180 "$py" -B "$lane/reciprocal_live.py" --dense > live-dense.log
        ;;
    pricing)
        run 120 "$py" -B "$lane/reciprocal_row_support.py" cal > proof-support-cal.log
        for quartile in 0 3; do
            run 420 "$py" -B "$lane/reciprocal_census_proofs.py" "$quartile" > "proof-stage-$quartile.log"
            run 150 "$py" -B "$lane/reciprocal_row_support.py" replay "$quartile" > "proof-support-$quartile.log"
        done
        run 210 "$py" -B "$lane/reciprocal_census_proofs.py" 2 --budget 6 --interval 645234 661618 > proof-extra.log
        run 100 "$py" -B "$lane/reciprocal_proof_reuse.py" cal > proof-reuse-cal.log
        run 100 "$py" -B "$lane/reciprocal_proof_reuse.py" ratio > proof-reuse-stage.log
        run 100 "$py" -B "$lane/reciprocal_proof_ledger.py" > proof-ledger.log
        ;;
    verify)
        run 300 "$py" -B "$lane/reciprocal_census_ledger.py" --complete > coverage.log
        run 100 "$py" -B "$lane/reciprocal_proof_ledger.py" > proof-ledger.log
        ;;
    *) exit 2 ;;
esac
