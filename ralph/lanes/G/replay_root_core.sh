#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
certs="$root/ralph/lanes/G/root_certs"
if (( $# < 1 || $# > 3 )); then
    echo "usage: $0 scratch-directory [catalogue-to-test [root-degree]]" >&2
    exit 2
fi
work=$1
catalogue=$(realpath -- "${2:-$certs/hog33_118.g6}")
mkdir -p -- "$work"
cd -- "$work"
ulimit -v 16777216
hard_cpu=$(ulimit -Ht)
if [[ $hard_cpu == unlimited || $hard_cpu -gt 90 ]]; then
    ulimit -t 90
fi
nice -n 5 timeout 100s python3 -S -B "$root/ralph/lanes/G/root_core.py" "$catalogue" . --root "${3:-6}"
count=$(wc -l < "$catalogue")
if (( count == 0 )); then
    echo 'empty catalogue' >&2
    exit 2
fi
failures=0
for (( index=1; index<=count; index++ )); do
    printf -v name '%04d' "$index"
    if (( $# == 1 )); then
        gzip -dc "$certs/$name.lrat.gz" > "$name.lrat"
    else
        status=0
        nice -n 5 timeout 30s /usr/bin/time -f 'CPU=%U+%S' "$root/opt/bin/cadical" \
            -q --lrat --no-binary "$name.cnf" "$name.lrat" > "$name.solve" 2>&1 || status=$?
        if (( status != 20 )); then
            printf '%s not_certified exit=%d\n' "$name" "$status"
            failures=$((failures + 1))
            continue
        fi
    fi
    nice -n 5 timeout 35s "$root/opt/bin/lrat-check" "$name.cnf" "$name.lrat" > "$name.verify"
    nice -n 5 timeout 35s "$root/opt/bin/cake_lpr" "$name.cnf" "$name.lrat" > "$name.cake"
    rg -q '^c VERIFIED$' "$name.verify"
    rg -q '^s VERIFIED UNSAT$' "$name.cake"
    printf '%s cert\n' "$name"
done
if (( $# == 1 )); then
    sha256sum -c "$certs/dimacs_lrat.sha256"
fi
(( failures == 0 ))
