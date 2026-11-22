#!/bin/bash
set -euo pipefail
lane=$(cd "$(dirname "$0")" && pwd);root=$(cd "$lane/../../.." && pwd);store=$root/scratch/F/r24;py=$root/opt/venv/bin/python
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$PWD
while [[ -e /proc/$1 ]];do sleep 2;done
echo "$(date -Is) acquired returned fixed production lease";cd "$store/shape/repair"; "$py" -B "$lane/pattern_repair24.py" control >control.stdout
head -6 first.tsv >sample.keys;tail -n +7 first.tsv >balance.keys
mkdir -p sample balance
(cd sample; "$py" -B "$lane/pattern_repair24.py" run ../sample.keys 1000000 >worker.jsonl)
"$py" -B - <<'PY'
import json
from pathlib import Path
rows=list(map(json.loads,Path('sample/worker.jsonl').read_text().splitlines()));assert len(rows)==6 and sum(row['cpu'] for row in rows)<180 and all(not row['rc'] and not row['missing'] for row in rows)
print('priced first paired closure:',len(rows),'word-size groups in',sum(row['cpu'] for row in rows),'CPU-s',flush=True)
PY
(cd balance; "$py" -B "$lane/pattern_repair24.py" run ../balance.keys 1000000 >worker.jsonl)
cd "$store/fixed/sym/work1"; "$py" -B "$lane/rebound24.py" >plan.stdout; F_CARDS24_BIN="$store/fixed/sym/fixed" "$py" -B "$lane/cards24.py" wave manifest.tsv 1000000 100 >worker.jsonl
cd "$store/clean";bash "$lane/round24_replay.sh" >../clean.stdout 2>../clean.err
