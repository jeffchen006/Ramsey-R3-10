#!/usr/bin/env python3
"""Compare amax-subcase calibration with ground truth: a (n,p,f) case is SAT iff some subcase is SAT."""
import json, sys
truth = {17: {(2,1),(2,3),(2,9)}, 22: {(2,0),(2,2),(2,6),(2,8),(5,2),(11,0)},
         27: {(2,1),(2,3),(2,5),(2,7),(2,9),(2,17)}, 35: {(2,1),(3,5),(5,0),(7,0)}}
res = {}
for l in open(sys.argv[1]):
    d = json.loads(l)
    if 'job' in d:
        t = d['job'].split(); key = (int(t[3]), int(t[0]), int(t[1])); r = 'TIMEOUT'
    else:
        key = (d['n'], d['p'], d['f']); r = d['result']
    res.setdefault(key, []).append(r)
bad, open_ = [], []
nsat = nuns = 0
for (n, p, f), rs in sorted(res.items()):
    exp = (p, f) in truth[n]
    if 'SAT' in rs:
        nsat += 1
        if not exp: bad.append((n, p, f, 'SAT but not in truth'))
    elif all(r == 'UNSAT' for r in rs):
        nuns += 1
        if exp: bad.append((n, p, f, 'all subcases UNSAT but truth has it'))
    else:
        open_.append((n, p, f, rs.count('TIMEOUT')))
print(f"cases {len(res)}: SAT {nsat}, UNSAT {nuns}, undecided {len(open_)}; MISMATCHES {bad}")
print("undecided (n,p,f,#timeouts):", open_)
