#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
if (( $# < 1 || $# > 3 )); then
    echo "usage: $0 output-directory [catalogue [edge-count|any]]" >&2
    exit 2
fi
work=$1
catalogue=$(realpath -- "${2:-$root/ralph/lanes/G/root_certs/hog33_118.g6}")
edges=${3:-166}
mkdir -p -- "$work"
cd -- "$work"
ulimit -v 16777216
ulimit -t 240
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
if [[ $edges == any ]]; then
    edge_args=(--any-edges)
else
    edge_args=(--edges "$edges")
fi
nice -n 5 timeout 300s "$root/opt/venv/bin/python" -B "$root/ralph/lanes/G/root_glue.py" \
    --catalogue "$catalogue" --out . "${edge_args[@]}" --relaxed
order=$(wc -l < "$catalogue")
for (( index=1; index <= order; index++ )); do
    printf -v name '%04d' "$index"
    if nice -n 5 timeout 45s /usr/bin/time -f 'CPU=%U+%S' "$root/opt/bin/cadical" \
        -q --lrat --no-binary "$name.cnf" "$name.lrat" > "$name.solve" 2>&1; then
        status=0
    else
        status=$?
    fi
    case "$status" in
        20)
            nice -n 5 timeout 30s "$root/opt/bin/lrat-check" "$name.cnf" "$name.lrat" > "$name.verify"
            nice -n 5 timeout 30s "$root/opt/bin/cake_lpr" "$name.cnf" "$name.lrat" > "$name.cake"
            rg -q '^c VERIFIED$' "$name.verify"
            rg -q '^s VERIFIED UNSAT$' "$name.cake"
            printf '%s cert %s\n' "$name" "$(tail -1 "$name.solve")"
            ;;
        10) printf '%s feasible %s\n' "$name" "$(tail -1 "$name.solve")" ;;
        124) printf '%s timeout\n' "$name" ;;
        *) printf '%s unexpected_status_%s\n' "$name" "$status"; exit 1 ;;
    esac
done
