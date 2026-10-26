#!/bin/bash
# rerun2: subcases still TIMEOUT after rerun1, 24 h each, 11 parallel.
cd ./symsat
python3 - <<'PY'
import json
T=[]
for l in open('../runs/symsat/rerun1.jsonl'):
    d=json.loads(l)
    if d.get('result')=='TIMEOUT': T.append(f"{d['p']} {d['f']} --n 40 --K 10 --amax {d['amax']}")
    elif 'job' in d: T.append(d['job'])
open('../runs/symsat/rerun2_jobs.txt','w').write("\n".join(T)+"\n")
PY
./runjobs2.sh ../runs/symsat/rerun2_jobs.txt ../runs/symsat/rerun2.jsonl 86400 11 --dmin 5 --engine satcore --sbfull --seed 5 --work ../runs/symsat/work --out ../runs/symsat/found40_candidates.g6
