#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
scratch="$root/scratch/H"
export PATH="${ELAN_HOME:-$HOME/.elan}/bin:$PATH"
cd "$root/lean"
case ${1:-} in
    cache) response=.lake/packages/mathlib/.lake/build/bin/cache.rsp; libraries=(-lLake_shared) ;;
    sbcheck) response=.lake/build/bin/sbcheck.rsp; libraries=() ;;
    *) printf 'usage: %s cache|sbcheck\n' "$0" >&2; exit 2 ;;
esac
mapfile -t objects < <(sed -n 's/^"\(.*\.c\.o\.export\)"$/\1/p' "$response")
test "${#objects[@]}" -gt 0
runtime="$(lean --print-prefix)/lib/lean"
ulimit -v 16777216
exec timeout 180 nice -n 5 gcc -o "$scratch/$1-dyn" "${objects[@]}" \
    -L"$runtime" -Wl,-rpath,"$runtime" "${libraries[@]}" -lleanshared -ldl -lm -pthread
