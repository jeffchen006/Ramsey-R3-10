#!/bin/bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
target=$(realpath "$1")
source="$root/scratch/C/r24"
lane="$root/ralph/lanes/C"
export PYTHONDONTWRITEBYTECODE=1
cd "$target"
ulimit -v 524288
ulimit -t 75
python3 -B "$lane/audit_crown24_pinned.py" > control.log
cmp "$source/control-final.log" control.log
python3 -B - "$lane" "$source" <<'PY'
import json
from pathlib import Path
import sys
from time import process_time

sys.path.insert(0, sys.argv[1])
from crown24_pinned import analyze, load_rows

source = Path(sys.argv[2])
rows = dict(map(json.loads, (source/'fixed-rows.jsonl').read_text().splitlines()))
assert rows == load_rows(source.parent.parent/'E/r24_deck/C8.plan', list(rows))
for anchored, out_file in ((False, 'pilot.jsonl'), (True, 'anchor-pilot.jsonl')):
    reference = {row['index']: row for row in map(json.loads, (source/out_file).read_text().splitlines())}
    assert rows.keys() == reference.keys()
    with Path(out_file).open('x', encoding='ascii') as out:
        for index, row in rows.items():
            before = process_time()
            result = dict(index=index, **analyze(row, anchored=anchored))
            cpu = round(process_time()-before, 6)
            expected = reference[index]
            expected.pop('cpu', None)
            assert json.loads(json.dumps(result)) == expected, index
            print(json.dumps(dict(**result, cpu=cpu), separators=(',', ':')), file=out)
print('fixed projection-row binding and primary gates match', len(rows))
PY
for mode in pilot anchor-pilot; do
    case "$mode" in
        pilot) flags=() ;;
        anchor-pilot) flags=(--anchored) ;;
    esac
    python3 -B "$lane/audit_crown24_pinned.py" "${flags[@]}" "$source/fixed-rows.jsonl" "$mode.jsonl" > "$mode.oracle.log"
    python3 -B "$lane/crown24_baseline.py" "$mode.jsonl" "$root"/scratch/E/r24_deck/pilot/{0,1,2,3,4,5,6}.tsv > "$mode.baseline.log"
done
cat control.log {pilot,anchor-pilot}.{oracle,baseline}.log
