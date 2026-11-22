#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd); dest=$root/scratch/D/roles15
ulimit -v 16777216
for tag in "$@"; do
    set +e
    /usr/bin/time -o "$dest/$tag.solve.time" -f '%U %S %M' nice -n 5 timeout 110 prlimit --cpu=80:81 "$root/opt/bin/cadical" -q -n --lrat --no-binary "$dest/$tag.cnf" "$dest/$tag.lrat" >"$dest/$tag.solve.log"
    ret=$?; set -e; [[ $ret == 20 ]]
    for check in cake_lpr lrat-check; do
        /usr/bin/time -o "$dest/$tag.$check.time" -f '%U %S %M' nice -n 5 timeout 110 prlimit --cpu=80:81 "$root/opt/bin/$check" "$dest/$tag.cnf" "$dest/$tag.lrat" >"$dest/$tag.$check.log"
        rg -q VERIFIED "$dest/$tag.$check.log"
    done
done
