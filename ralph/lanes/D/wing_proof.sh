#!/usr/bin/env bash
set -eu
root=$(cd "$(dirname "$0")/../../.." && pwd); ulimit -v 16777216
for name in "$@"; do
    tag="$root/scratch/D/book14/$name"; set +e
    /usr/bin/time -f 'CPU %U %S RSS %M' -o "$tag.solve.time" nice -n 5 timeout 140 prlimit --cpu=95:96 "$root/opt/bin/cadical" -q -n --lrat --no-binary "$tag.cnf" "$tag.lrat" >"$tag.solve"; rc=$?;set -e;[[ $rc == 20 ]]
    for check in cake_lpr lrat-check; do /usr/bin/time -f 'CPU %U %S RSS %M' -o "$tag.$check.time" nice -n 5 timeout 180 prlimit --cpu=150:151 "$root/opt/bin/$check" "$tag.cnf" "$tag.lrat" >"$tag.$check.log"; done
    rg -q 'VERIFIED UNSAT' "$tag.cake_lpr.log"; rg -q '^c VERIFIED' "$tag.lrat-check.log"
done
