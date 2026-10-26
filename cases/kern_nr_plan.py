"""Plan + per-distribution counts for near-regular edge kernels (codex_strategy_3.md Sec 3). Author: cases, 2026-10-26.
Case (D, M): D = degree distribution (200 sel list), M = max codegree over nonedges, Mmin(D) = ceil(S/P) <= M <= 7.
Kernel at the edge uv minimising e(F) (Ball bound B_D(M), kern_nr_bounds.py), endpoint degrees a >= b (WLOG; the
swap u <-> v), F on A (a-1) x B (b-1): d_F(x in A) = c(x,v)-1 <= min(M, b-2)-1 (codeg <= M and L6 with d(x) <= 9),
d_F(y in B) <= min(M, a-2)-1, two A-vertices (or two B-vertices) have <= M-1 common F-nbrs, nu(F) >= a+b-11.
Type (a,b) allowed in D iff n_a, n_b > 0 (n_a >= 2 if a = b).
  plan:   prints genbg/kagg commands (one per (a,b,M), e up to max_D B_D(M))
  counts: reads cases/out/kern_nr/*.cnt, writes cases/out/kern_nr_counts.json and a summary."""
import json, math, os, sys
D = json.load(open('cases/out/kern_nr_bounds.json'))
OUT = 'cases/out/kern_nr'
def types(r):
    n = dict(zip(range(4, 10), r['n']))
    return [(a, b) for a in range(9, 5, -1) for b in range(a, 5, -1) if n[a] and n[b] and (a != b or n[a] >= 2)]
def Mrange(r):
    return range(max(3, math.ceil(r['S'] / r['P'])), 8)
def caps(a, b, M):
    return min(M, b - 2) - 1, min(M, a - 2) - 1
jobs = {}
for r in D:
    for M in Mrange(r):
        for a, b in types(r):
            k = (a, b, M); jobs[k] = max(jobs.get(k, 0), r['Ball'][str(M)] if isinstance(next(iter(r['Ball'])), str) else r['Ball'][M])
if sys.argv[1] == 'plan':
    for (a, b, M), E in sorted(jobs.items()):
        dA, dB = caps(a, b, M); nu = max(0, a + b - 11)
        if dA < 0 or dB < 0: continue
        tag = f'{OUT}/a{a}b{b}M{M}'
        print(f'tools/bin/genbg -q -d0:0 -D{dA}:{dB} -Z{M-1} {a-1} {b-1} {nu}:{E} | cases/kagg {a-1} {nu} {M-1} 8 {a*100+b*10+M} {tag}.cnt {tag}.samp')
else:
    cnt = {}
    for (a, b, M) in jobs:
        f = f'{OUT}/a{a}b{b}M{M}.cnt'
        if os.path.exists(f):
            cnt[(a, b, M)] = {int(l.split()[0]): int(l.split()[1]) for l in open(f) if not l.startswith('#')}
    res = []
    for r in D:
        row = {'n': r['n'], 'e': r['e'], 'cases': {}}
        for M in Mrange(r):
            B = r['Ball'][str(M)] if isinstance(next(iter(r['Ball'])), str) else r['Ball'][M]
            row['cases'][M] = {f'{a}{b}': sum(c for e, c in cnt.get((a, b, M), {}).items() if e <= B) for a, b in types(r)}
            row['cases'][M]['B'] = B
        res.append(row)
    json.dump(res, open('cases/out/kern_nr_counts.json', 'w'))
    tot = sum(v for r in res for M in r['cases'] for k, v in r['cases'][M].items() if k != 'B')
    print('total kernels over all (D, M, type):', tot)
    for M in range(3, 8):
        s = sum(v for r in res if M in r['cases'] for k, v in r['cases'][M].items() if k != 'B')
        print('M', M, 'kernels', s, 'cases', sum(1 for r in res if M in r['cases']))
    bytype = {}
    for r in res:
        for M in r['cases']:
            for k, v in r['cases'][M].items():
                if k != 'B': bytype[k] = bytype.get(k, 0) + v
    print('by type', sorted(bytype.items()))
