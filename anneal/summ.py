#!/usr/bin/env python3
"""summ.py: summary of n=40 production runs (runs/anneal/prod).
Prints best bad-set count (independent 10-sets, K) per mode, and writes
runs/anneal/near40.g6 (best graph of each run, sorted by K) and near40.txt (K, e, run)."""
import glob, os, re
D = './runs/anneal'
rows = []
for log in glob.glob(D + '/prod/*.log'):
    run = os.path.basename(log)[:-4]
    txt = open(log).read()
    if '# ls n=40' not in txt:
        continue
    ks = [int(x) for x in re.findall(r'best K=(\d+)', txt)] + [int(x) for x in re.findall(r'\(K=(\d+)\)', txt)]
    bf = D + '/prod/' + run + '.best.g6'
    if not ks or not os.path.exists(bf):
        continue
    g = open(bf).read().strip()
    rows.append((min(ks), run, g))
rows.sort()
best = {}
for k, run, g in rows:
    mode = run.split('_c')[0]
    best.setdefault(mode, []).append(k)
for mode in sorted(best):
    v = best[mode]
    print('%-6s runs=%3d bestK=%d median=%d' % (mode, len(v), min(v), sorted(v)[len(v) // 2]))
with open(D + '/near40.g6', 'w') as f, open(D + '/near40.txt', 'w') as t:
    t.write('# K = independent 10-sets of the graph on the same line of near40.g6 (triangle-free, n=40)\n')
    for k, run, g in rows:
        e = 0
        f.write(g + '\n')
        t.write('%d %s\n' % (k, run))
print('near40.g6: %d graphs, best K=%s' % (len(rows), rows[0][0] if rows else '-'))
