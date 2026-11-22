#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
overlay="$root/scratch/H/r24-lean"
mkdir -p "$overlay/R310"
cd "$root/lean"
export LEAN_NUM_THREADS=1 LEAN_STACK_SIZE_KB=8192
lean="$HOME/.elan/toolchains/leanprover--lean4---v4.35.0/bin/lean"
for artifact in "$PWD"/.lake/build/lib/lean/R310/*; do
    name=${artifact##*/}
    case "$name" in WingProjection.*) continue ;; esac
    if [[ ! -e "$overlay/R310/$name" ]]; then
        ln -sT "$artifact" "$overlay/R310/$name"
    fi
done
export LEAN_PATH="$overlay:$PWD/.lake/build/lib/lean"
for pkg in "$PWD"/.lake/packages/*; do
    LEAN_PATH="$LEAN_PATH:$pkg/.lake/build/lib/lean"
done
ulimit -v 16777216
run() {
    /usr/bin/time -f 'wall=%e user=%U sys=%S maxrss_kib=%M exit=%x' \
        timeout 420 nice -n 5 prlimit --cpu=240 "$lean" -j 1 "$@"
}
run -o "$overlay/R310/WingProjection.olean" R310/WingProjection.lean > "$overlay/wing.log" 2>&1
run "$root/ralph/lanes/H/WingProjectionAxioms.lean" > "$overlay/targeted.log" 2>&1
python3 -BS "$root/ralph/lanes/H/check_axioms.py" "$root/ralph/lanes/H/WingProjectionAxioms.lean" "$overlay/targeted.log"
if [[ ${1:-} == --targeted ]]; then
    exit 0
fi
run -o "$overlay/R310.olean" R310.lean > "$overlay/aggregate.log" 2>&1
run scripts/Axioms.lean > "$overlay/project.log" 2>&1
python3 -BS "$root/ralph/lanes/H/check_axioms.py" scripts/Axioms.lean "$overlay/project.log"
