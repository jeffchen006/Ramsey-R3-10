"""Edge-kernel bounds for the near-regular distributions (codex_strategy_3.md Sec 3). Author: cases, 2026-10-26.
For a distribution (n4..n9) and max codegree M: 4 C4 <= U = (M+1) S - 2 M P + (M-1) T (MTF: c >= 1 on nonedges;
c(c-1) <= (M+1)c - 2M + (M-1)[c=1]; t1 <= T). Some edge has e(F) <= floor(U/e) (Ball); some edge between two
9-vertices has e(F) <= floor(U/e99) with e99 >= e - sum_{d<9} d n_d (B99; needs e99 > 0).
Usage: python3 cases/kern_nr_bounds.py [cases/out/mforce_sel.json]  -> cases/out/kern_nr_bounds.json + summary"""
import json, sys
from collections import Counter
L = [r for r in json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'cases/out/mforce_sel.json')) if r['feasible']]
out = []
for r in L:
    n = dict(zip(range(4, 10), r['n'])); e = r['e']
    assert sum(d * c for d, c in n.items()) == 2 * e and sum(n.values()) == 40
    P = 780 - e; S = sum(c * d * (d - 1) // 2 for d, c in n.items()); T = sum(c * d * (10 - d) for d, c in n.items()) // 2
    e99 = e - sum(d * c for d, c in n.items() if d < 9)
    row = {'n': r['n'], 'e': e, 'P': P, 'S': S, 'T': T, 'e99min': e99, 'Ball': {}, 'B99': {}}
    for M in range(3, 8):
        U = (M + 1) * S - 2 * M * P + (M - 1) * T
        row['Ball'][M] = U // e
        row['B99'][M] = U // e99 if e99 > 0 else None
    row['degs'] = [d for d in range(4, 10) if n[d]]
    out.append(row)
json.dump(out, open('cases/out/kern_nr_bounds.json', 'w'))
print(len(out), 'distributions')
for M in range(3, 8):
    print('M', M, 'Ball', sorted(Counter(r['Ball'][M] for r in out).items()), 'B99', sorted(Counter(r['B99'][M] for r in out).items(), key=str))
print('degree sets', Counter(tuple(r['degs']) for r in out))
print('e99min range', min(r['e99min'] for r in out), max(r['e99min'] for r in out))
