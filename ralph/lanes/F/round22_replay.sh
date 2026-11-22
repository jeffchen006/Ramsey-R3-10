#!/bin/bash
set -euo pipefail
lane=$(cd "$(dirname "$0")" && pwd); root=$(cd "$lane/../../.." && pwd); store="$root/scratch/F/r22"
case "$PWD" in "$root"/scratch/F/*) ;; *) exit 2;; esac
test "$PWD" != "$store"; test -z "$(ls -A .)"
export PYTHONDONTWRITEBYTECODE=1 TMPDIR=$PWD OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 1048576;ulimit -f 40960
run(){ nice -n 5 timeout "$1" prlimit --cpu="$2" -- "${@:3}"; }
py="$root/opt/venv/bin/python"
(cd "$root"; run 600 300 sha256sum --quiet -c ralph/lanes/F/ROUND22_FREEZE.sha256)
(cd "$store"; run 1200 300 sha256sum --quiet -c receipts.sha256)
run 1800 1500 "$py" -B "$lane/exception_finish.py" all "$store" 0 1 > bare-and-pole.log
for file in "$store"/signcount/*; do
    case "$file" in *.pairs|*.masks|*.cnf|*.lrat|*.result|*.trace|*.signs|*.plant) ln -s "$file" .;; esac
done
for tag in plainpos 3024_0 3032_0 6049_0 6064_0 14241_0; do run 90 75 "$py" -B "$lane/exception_cover.py" "$tag" verify; done
for tag in plainpos fixedpos 3024_0 3032_0 6049_0 6064_0 14241_0; do run 180 150 "$py" -B "$lane/exception_fixedbind.py" "$tag"; done
tail -1 bare-and-pole.log
