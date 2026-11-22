#!/usr/bin/env bash
set -eu
ulimit -v 16777216
root=$(cd "$(dirname "$0")/../../.." && pwd)
file=$1
tag=${file%.cnf}
set +e
/usr/bin/time -f 'CPU %U %S RSS %M' -o "$tag.solve.time" nice -n 5 timeout 35 prlimit --cpu=15:16 "$root/opt/bin/cadical" -q -n --lrat --no-binary "$file" "$tag.lrat" >"$tag.solve"
status=$?
set -e
[[ $status == 20 ]]
for checker in cake_lpr lrat-check; do
    /usr/bin/time -f 'CPU %U %S RSS %M' -o "$tag.$checker.time" nice -n 5 timeout 45 prlimit --cpu=25:26 "$root/opt/bin/$checker" "$file" "$tag.lrat" >"$tag.$checker.log"
done
rg -q '^s VERIFIED UNSAT' "$tag.cake_lpr.log"
rg -q '^c VERIFIED' "$tag.lrat-check.log"
