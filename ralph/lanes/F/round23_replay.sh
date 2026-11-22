#!/bin/bash
set -euo pipefail
lane=$(cd "$(dirname "$0")" && pwd); root=$(cd "$lane/../../.." && pwd); store="$root/scratch/F/r23"; py="$root/opt/venv/bin/python"
case "$PWD" in "$root"/scratch/*/*) ;; *) echo 'use an empty lane-owned scratch directory' >&2; exit 2;; esac
test "$PWD" != "$store"; test -z "$(ls -A .)"; export TMPDIR=$PWD PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 1048576;ulimit -f 32768; run(){ nice -n 5 timeout "$1" prlimit --cpu="$2" -- "${@:3}"; }
ln -s "$store/columns.tsv" "$store/bank.tsv" .
run 60 50 g++ -std=c++17 -O3 -march=native "$lane/six_complete.cpp" -o six
case "${1:-quick}" in
 quick)
    run 90 75 "$py" -B "$lane/six_audit.py" bank
    run 220 200 "$py" -B "$lane/six_branch.py" control
    for path in "$store"/trial*.{rows,count} "$store"/price*.{rows,count,time} "$store"/strata*.{rows,count,time} "$store"/trial*.time "$store"/work_* "$store"/plan_*.tsv; do ln -s "$path" .;done
    run 240 200 "$py" -B "$lane/six_audit.py" summary
    mkdir receipts; (cd receipts; for ext in cnf lrat cores masks pairs.gz cuts; do for path in "$store"/receipts/*."$ext"; do test ! -e "$path" || ln -s "$path" .;done;done
      for path in ./*.masks; do tag=${path#./};tag=${tag%.masks};run 200 170 "$py" -B "$lane/six_receipt.py" "$tag" bind;done
      for path in ./*.cuts;do test -e "$path" || continue;tag=${path#./};tag=${tag%.cuts};run 120 100 "$py" -B "$lane/six_prefix_cert.py" "$tag" verify;done)
    ;;
 interval)
    tag=$2; index=$3; test "$tag" = first || test "$tag" = all; read -r id start end < <(sed -n "$((index+1))p" "$store/plan_$tag.tsv");test "$id" = "$index"
    run 250 200 ./six 2000000 11 576 "$start" "$end" count >rows
    stem=$(printf '%s/work_%s/s%05d' "$store" "$tag" "$index");cmp count "$stem.count";gzip -dc "$stem.rows.gz" | cmp rows -;echo "same signed outcomes $tag $index";;
 *) exit 2;;
esac
