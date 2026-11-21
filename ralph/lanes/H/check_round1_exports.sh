#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
project="$root/lean"
scratch="$root/scratch/H"
output="$scratch/project-export"
export PATH="${ELAN_HOME:-$HOME/.elan}/bin:$PATH"
export LEAN_NUM_THREADS=2 LEAN_STACK_SIZE_KB=65536
ulimit -v 16777216
mkdir -p "$output"
cd "$project"
lake_cmd=(lake --packages="$scratch/packages-local.json")
timer=(/usr/bin/time -f 'wall=%e user=%U sys=%S maxrss=%M exit=%x')

test -f "$project/.lake/build/lib/lean/R310/Files.olean"
"${timer[@]}" timeout 240 "${lake_cmd[@]}" env bash -c \
    'cd "$1"; exec lean --root="$2" "$2/scripts/EmitCubes.lean"' _ "$output" "$project"
for name in R S8 N; do
    file="cube_$name.opb"
    cmp "$output/out/$file" "$scratch/emit/out/$file"
    sha256sum "$output/out/$file"
done
printf 'All three formal OPB exports match the provisional bytes.\n'
