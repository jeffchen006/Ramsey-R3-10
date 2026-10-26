#!/usr/bin/env python3
import json, sys
rows = []
for l in open(sys.argv[1]):
    d = json.loads(l)
    rows.append((d.get('n', 0), d.get('K', 0), d.get('p', 0), d.get('f', 0), d['result'], d.get('time_s'), d.get('iters'), d.get('vars'), d.get('job', '')))
for r in sorted(rows): print(*r)
