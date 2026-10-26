#!/usr/bin/env python3
"""table.py RESULTS.jsonl [CERTLOG] -> markdown table of (p, f) cases (last result per case wins,
a decided result beats a timeout)."""
import json
import sys

best = {}
for line in open(sys.argv[1]):
    d = json.loads(line)
    if "job" in d:
        p, f = map(int, d["job"].split()[:2])
        d = dict(p=p, f=f, result="TIMEOUT", time_s=None, k=None, vars=None, solver="", n=None)
    key = (d["p"], d["f"])
    old = best.get(key)
    if old is None or old["result"] in ("TIMEOUT", "KILLED") or d["result"] in ("SAT", "UNSAT"):
        best[key] = d
cert = {}
if len(sys.argv) > 2:
    for line in open(sys.argv[2]):
        t = line.split()
        if len(t) >= 3:
            cert[(int(t[0]), int(t[1]))] = t[2]
print("| p | f | p-cycles | orbit vars | result | time (s) | solver | DRAT certificate |")
print("|---|---|---|---|---|---|---|---|")
cases = [(7, 5)] + [(5, f) for f in (15, 10, 5, 0)] + [(3, f) for f in range(28, 0, -3)] + [(2, f) for f in range(34, -1, -2)]
for c in cases:
    best.setdefault(c, dict(result="OPEN (running or queued)", time_s=None, vars=None, solver=""))
for (p, f), d in sorted(best.items(), key=lambda x: (-x[0][0], -x[0][1])):
    k = (40 - f) // p
    print(f"| {p} | {f} | {k} | {d.get('vars') or ''} | {d['result']} | {d.get('time_s') or ''} | {d.get('solver','').strip()} | {cert.get((p, f), 'no')} |")
