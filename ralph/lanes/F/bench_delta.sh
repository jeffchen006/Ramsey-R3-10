#!/usr/bin/env bash
set -euo pipefail
for spec in '35 9 35 30000 35 3.5 11' '35 9 7 30000 7 .35 1121' '35 9 5 30000 5 .35 1121' '38 10 2 30000 3 .25 1121'; do
    read -r n k symmetry moves hot cold seed <<< "$spec"
    prefix="bench_${n}_m${symmetry}_s${seed}"
    for mode in seq batch check; do
        extra=()
        case $mode in
            batch) extra+=(-symbatch);;
            check) extra+=(-symverify);;
        esac
        rc=0
        /usr/bin/time -f 'cpu_user=%U cpu_sys=%S elapsed=%e maxrss_kb=%M exit=%x' -o "$prefix.$mode.time" \
            ../build/ls_sym -n "$n" -k "$k" -sym "$symmetry" -symfast -w9 0 -maxdeg "$((k-1))" \
            -T0 "$hot" -T1 "$cold" -sweep 50000 -moves "$moves" -time 60 -seed "$seed" \
            -out "$prefix.$mode" "${extra[@]}" || rc=$?
        if ((rc > 1)); then exit "$rc"; fi
    done
    cmp "$prefix.seq.best.g6" "$prefix.batch.best.g6"
    cmp "$prefix.seq.best.g6" "$prefix.check.best.g6"
    printf '\n%s\n' "$prefix"
    for mode in seq batch check; do
        printf '%s ' "$mode"; tail -1 "$prefix.$mode.time"
        rg '^(END|ORBIT_VERIFY|WARN)' "$prefix.$mode.log"
    done
done
