#!/bin/bash
set -euo pipefail
src=../../../ralph/lanes/E
python=../../../opt/venv/bin/python
mapfile -t old_pids < <(awk -F'\t' '$5 ~ /^oldreplay\.[0-6]\.log$/ {print $1}' jobs.tsv)
[[ ${#old_pids[@]} == 7 ]]
for pid in "${old_pids[@]}"; do
    while :; do
        state=$(ps -o stat= -p "$pid" || :)
        [[ -n "$state" && "$state" != Z* ]] || break
        sleep 1
    done
done
cmp <(sort -n oldreplay/{0,1,2,3,4,5,6}.ids) <(seq 0 15349)
"$python" -B - <<'PY'
from pathlib import Path
paths = [Path(f'oldreplay/{slot}.tsv') for slot in range(7)]
seen = set()
for slot, path in enumerate(paths):
    contents = path.read_bytes()
    assert not contents or contents.endswith(b'\n')
    for record in contents.splitlines():
        index, status, *values = record.split(b'\t')
        index = int(index)
        assert status == b'CHECKED' and index % 7 == slot and 0 <= index < 15350 and index not in seen
        seen.add(index)
missing = sorted(set(range(15350)) - seen)
print('exact replay tail', len(seen), 'checked before tail;', len(missing), 'IDs absent')
Path('oldreplay/tail.ids').write_text(''.join(f'{index}\n' for index in missing))
PY
if [[ -s oldreplay/tail.ids ]]; then
    "$python" -B "$src/compact_deck24.py" old --plan ../r23_deck/e8ext.first.plan \
        --indexes oldreplay/tail.ids --output oldreplay/tail
fi
awk -F'\t' '
    NF!=7 || $1<0 || $1>=15350 || $2!="CHECKED" || (seen[$1]++) {bad=1}
    {cpu+=$7; cuts+=$6}
    END {if (bad || length(seen)!=15350) exit 1; printf "final 2C4 join %d / 15350 CHECKED, %d I8 witnesses, %.3f replay CPU-s\n", length(seen), cuts, cpu}
' oldreplay/*.tsv | tee 2c4.final.log
sha256sum ../r23_deck/e8ext.first.plan 2c4.old.json 2c4.repair.ids oldreplay/*.tsv \
    oldreplay/*.ids cover2/*.jsonl "$src/cover_deck24.py" "$src/compact_deck24.py" \
    "$src/rebind_projection23.py" "$src/audit_deck24.py" > freeze.2c4.sha256
sha256sum --quiet -c freeze.2c4.sha256
touch replay-tail.done
