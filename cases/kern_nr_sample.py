"""Draw a reproducible kernel timing sample for one distribution D and case M (codeg <= M). Author: cases, 2026-10-26.
Weights: catalogue counts N(type, e) for e <= B_D(M); then one of the (<= 8) reservoir graphs of that (type, e) cell.
Usage: kern_nr_sample.py IDX M COUNT SEED >> sample.txt   (IDX = index in cases/out/kern_nr_bounds.json)"""
import json, random, sys
sys.argv += []
idx, M, K, seed = map(int, sys.argv[1:5])
r = json.load(open('cases/out/kern_nr_bounds.json'))[idx]
n = dict(zip(range(4, 10), r['n'])); B = r['Ball'][str(M)]
types = [(a, b) for a in range(9, 5, -1) for b in range(a, 5, -1) if n[a] and n[b] and (a != b or n[a] >= 2)]
cells, w = [], []
for a, b in types:
    tag = f'cases/out/kern_nr/a{a}b{b}M{M}'
    S = {}
    for l in open(tag + '.samp'):
        e, g = l.split(); S.setdefault(int(e), []).append(g)
    for l in open(tag + '.cnt'):
        if l.startswith('#'): continue
        e, c = map(int, l.split())
        if e <= B: cells.append((a, b, e, S[e])); w.append(c)
rng = random.Random(seed)
print(f"# D={r['n']} e={r['e']} M={M} B={B} kernels={sum(w)}")
for a, b, e, gs in rng.choices(cells, weights=w, k=K):
    print(f"{','.join(map(str, r['n']))} {M} {a} {b} {rng.choice(gs)}  # e(F)={e}")
