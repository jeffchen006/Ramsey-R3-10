#!/usr/bin/env bash
set -eu
root=$(cd "$(dirname "$0")/../../.." && pwd)
src="$root/ralph/lanes/D"; dest="$root/scratch/D/join13"; out="$dest/rebound"; mkdir -p "$out"
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1
ulimit -v 16777216
run() { nice -n 5 timeout 180 prlimit --cpu=125:126 "$@"; }
for name in "$@"; do
    case "$name" in
        119-general) cmd=(book_reroot.py --key 119 --cap 60000);;
        179-general) cmd=(book_reroot.py --key 179 --no-covers --cap 60000);;
        119-two) cmd=(book_obstructions.py --key 119 --kind two --cap 40000);;
        high3-179) cmd=(book_select.py --key 179 --family 119,121,122,175,178,179,191 --cap 15000);;
        *) exit 2;;
    esac
    run "$root/opt/venv/bin/python" -B "$src/${cmd[0]}" "$dest" "${cmd[@]:1}" --dump "$out/$name.cnf" >"$out/$name.build"
    cmp "$out/$name.cnf" "$dest/proof/$name.cnf"
    for checker in cake_lpr lrat-check; do
        run "$root/opt/bin/$checker" "$out/$name.cnf" "$dest/proof/$name.lrat" >"$out/$name.$checker.log"
        rg -q 'VERIFIED' "$out/$name.$checker.log"
    done
    sha256sum "$out/$name.cnf" "$dest/proof/$name.lrat"; rm "$out/$name.cnf"
done
