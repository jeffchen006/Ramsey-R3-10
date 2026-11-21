#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
scratch="$root/scratch/H"
project="$root/lean"
export PATH="${ELAN_HOME:-$HOME/.elan}/bin:$PATH"
export LEAN_NUM_THREADS=2 LEAN_STACK_SIZE_KB=65536
export XDG_CACHE_HOME="$scratch/cache" MATHLIB_CACHE_DIR="$scratch/cache"
export GIT_TERMINAL_PROMPT=0
ulimit -v 16777216
mkdir -p "$scratch/lean-artifacts"
cd "$project"
jq '.packages |= map(del(.url, .rev, .inputRev, .subDir) +
    {type:"path", dir:(".lake/packages/" + .name)})' lake-manifest.json > "$scratch/packages-local.json"
while IFS=$'\t' read -r name expected; do
    actual=$(git -C ".lake/packages/$name" rev-parse HEAD)
    test "$actual" = "$expected"
    printf '%s %s\n' "$name" "$actual"
    destination="$scratch/lean-artifacts/$name"
    directory=".lake/packages/$name/.lake"
    mkdir -p "$directory" "$destination"
    if ! test -L "$directory/build"; then
        if test -d "$directory/build"; then
            cp -a "$directory/build/." "$destination/"
            test ! -e "$directory/build.initial"
            mv "$directory/build" "$directory/build.initial"
        fi
        ln -s "$destination" "$directory/build"
    fi
done < <(jq -r '.packages[] | [.name, .rev] | @tsv' lake-manifest.json)
lake_cmd=(lake --packages="$scratch/packages-local.json")
timed=(/usr/bin/time -f 'wall=%e user=%U sys=%S maxrss=%M exit=%x')
if [[ ${1:-} == dynamic ]]; then
    export LEAN_SRC_PATH="$project"
    for dependency in "$project/.lake/packages/"*; do
        LEAN_SRC_PATH="$LEAN_SRC_PATH:$dependency"
    done
    "${timed[@]}" timeout 1500 stdbuf -oL -eL "$scratch/cache-dyn" get \
        --repo=leanprover-community/mathlib4 > "$scratch/cache-download.log" 2>&1
else
    "${timed[@]}" timeout 1500 stdbuf -oL -eL "${lake_cmd[@]}" exe cache get \
        > "$scratch/cache-download.log" 2>&1
fi
test -f "$scratch/lean-artifacts/mathlib/lib/lean/Mathlib.olean"
"${timed[@]}" timeout 900 "${lake_cmd[@]}" --old --no-build build mathlib/+Mathlib \
    > "$scratch/mathlib-cache-check.log" 2>&1
"${timed[@]}" timeout 900 "${lake_cmd[@]}" build --old > "$scratch/lake-build.log" 2>&1
"${timed[@]}" timeout 240 "${lake_cmd[@]}" env lean -j1 -s8192 scripts/Axioms.lean \
    > "$scratch/axioms.log" 2>&1
python3 -B "$root/ralph/lanes/H/check_axioms.py" scripts/Axioms.lean "$scratch/axioms.log" \
    > "$scratch/axioms-audit.log"
bash "$root/ralph/lanes/H/check_round1_exports.sh" > "$scratch/project-export.log" 2>&1
new_axioms="$root/ralph/lanes/H/AxiomsRound1.lean"
"${timed[@]}" timeout 240 "${lake_cmd[@]}" env lean -j1 -s8192 "$new_axioms" \
    > "$scratch/axioms-new.log" 2>&1
python3 -B "$root/ralph/lanes/H/check_axioms.py" "$new_axioms" "$scratch/axioms-new.log" \
    > "$scratch/axioms-new-audit.log"
