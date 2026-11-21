#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
ulimit -v 16777216
root=$(cd "$(dirname "$0")/../../.." && pwd)
for stem in "$@"; do
    status=0
    timeout 80s "$root/opt/bin/cadical" -q --lrat --no-binary "$stem.cnf" "$stem.lrat" > "$stem.solve" 2>&1 || status=$?
    if [[ "$status" != 20 ]]; then
        printf '%s solver status=%d\n' "$stem" "$status"
        rm -f "$stem.lrat"
        continue
    fi
    timeout 60s "$root/opt/bin/lrat-check" "$stem.cnf" "$stem.lrat" > "$stem.verify"
    timeout 60s "$root/opt/bin/cake_lpr" "$stem.cnf" "$stem.lrat" > "$stem.cake"
    rg -q '^c VERIFIED' "$stem.verify"
    rg -q '^s VERIFIED' "$stem.cake"
    sha256sum "$stem."{g6,cnf,lrat,verify,cake} > "$stem.sha256"
    gzip -f "$stem.lrat"
    printf '%s dual checked\n' "$stem"
done
