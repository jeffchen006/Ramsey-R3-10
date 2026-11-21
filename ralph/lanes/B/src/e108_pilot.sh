#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

src=../../ralph/lanes/B/src
previous=work/e162_r5
directory=work/e108_r5
mkdir -p "$directory"
test -r "$previous/lateral2.union.g6"

/usr/bin/time -f 'addition control CPU %U+%S wall %e' timeout 2m build/edgeup < ../G/round3/e106.add.g6 > "$directory/e107.control.raw"
timeout 3m ../../opt/bin/shortg -q -T"$directory" "$directory/e107.control.raw" "$directory/e107.control.g6"
cmp "$directory/e107.control.g6" ../G/round3/e107.add.g6
rm "$directory/e107.control.raw"
printf 'exact known e106 -> e107 addition equality (234341 canonical children)\n'

timeout 1m python3 "$src/sample_levels.py" "$previous/lateral2.union.g6" 32 107 1024 108107 > "$directory/access.g6"
/usr/bin/time -f 'pilot edgeup CPU %U+%S wall %e' timeout 2m build/edgeup < "$directory/access.g6" > "$directory/children.raw"
/usr/bin/time -f 'pilot canon CPU %U+%S wall %e' timeout 2m ../../opt/bin/shortg -q -T"$directory" "$directory/children.raw" "$directory/children.g6"
rm "$directory/children.raw"
count=$(wc -l < "$directory/children.g6")
timeout 1m build/audit_duals 32 108 9 "$count" < "$directory/children.g6"
timeout 1m python3 "$src/sample_levels.py" "$directory/children.g6" 32 108 1024 108108 > "$directory/glue-sample.g6"
/usr/bin/time -f 'pilot gluing CPU %U+%S wall %e' timeout 2m build/mtfcover_r5 -X -k 9 -d 7 -m 6 -M 9 -E 161 -e 180 < "$directory/glue-sample.g6" > "$directory/glue-out.g6"
if [[ -s "$directory/glue-out.g6" ]]; then
    cp "$directory/glue-out.g6" ../../ralph/found/B_e108_pilot.g6
    timeout 1m python3 ../../tools/check_graph.py --n 40 --k 10 ../../ralph/found/B_e108_pilot.g6
    timeout 1m python3 ../../.hmz/flows/r310_ralph/gate.py ../.. check ../../ralph/found/B_e108_pilot.g6 40 10
fi
timeout 2m bash "$src/e107_cliques.sh" "$directory/glue-sample.g6" "$directory/clique-sample"
