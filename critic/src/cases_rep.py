"""critic: independent re-implementation of cases' degree-distribution pipeline (notes/cases.md).
Written from the lemma statements, not from cases/degseq.py. Float LP only (for comparison).
LP row families are a SUPERSET of cases' (extra Mantel weights in {0..3}^classes), so
expected: my t9 <= cases' t9 everywhere; my t9 > cases' t9 would point to a bug."""
import itertools, json, sys
import numpy as np
from scipy.optimize import linprog
E9 = {30: 86, 31: 95, 32: 104, 33: 118, 34: 129, 35: 140}
D = [4, 5, 6, 7, 8, 9]
mtf = "--mtf" in sys.argv
ELB = 159 if "--self-e" in sys.argv else 161

def simple(n):
    c = dict(zip(D, n)); s = sum(d * c[d] for d in D)
    if s % 2: return False
    e = s // 2
    if not ELB <= e <= 180: return False
    if mtf and (c[4] or c[5]): return False
    if sum(c[d] * (d * (20 - d) - E9[39 - d]) for d in D) < 0: return False
    if c[4] + c[5] > 2: return False
    if c[4] and c[4] - 1 + c[5] + c[6] > 4: return False
    if c[4] == 2 and c[6]: return False
    if c[4]:  # L7: neighbour degrees d1..d4 of a 4-vertex
        okk = False
        for ds in itertools.combinations_with_replacement(D, 4):
            if any(a + b < 12 for a, b in itertools.combinations(ds, 2)): continue
            m = {d: ds.count(d) for d in D}; s1 = sum(d - 1 for d in ds)
            want = {4: 1 + m[4], 5: m[5], 6: m[6], 7: m[7], 8: 35 - s1 + m[8], 9: s1 + m[9]}
            if all(want[d] == c[d] for d in D) and 140 + sum(ds) == e: okk = True
        if not okk: return False
    pool = sorted(d for d in D for _ in range(c[d]))
    for d in D:
        if not c[d]: continue
        o = list(pool); o.remove(d); z = sum(o[:d])
        if mtf: z = max(z, d * d - 11 * d + 78)
        if z > e - E9[39 - d]: return False
    return True

def feasible(n, L):
    c = dict(zip(D, n)); P = [d for d in D if c[d]]; e = sum(d * c[d] for d in D) // 2
    V = [(i, j) for i in P for j in P if i <= j]; ix = {v: k for k, v in enumerate(V)}
    Aub, bub, Aeq, beq = [], [], [], []
    def row(): return [0.0] * len(V)
    for i in P:
        r = row(); z = row()
        for j in P:
            k = ix[(min(i, j), max(i, j))]; mult = 2 if i == j else 1
            r[k] += mult; z[k] += mult * j
        Aeq.append(r); beq.append(i * c[i])
        Aub.append(z); bub.append(c[i] * (e - L[i]))
        if mtf: Aub.append([-t for t in z]); bub.append(-c[i] * (i * i - 11 * i + 78))
    W = set(itertools.product(range(4), repeat=len(P)))
    W |= {tuple(9 - d for d in P), tuple(10 - d for d in P), tuple((9 - d) ** 2 for d in P)}
    for x in W:
        xs = dict(zip(P, x)); tot = sum(xs[d] * c[d] for d in P)
        r = row()
        for (i, j) in V: r[ix[(i, j)]] = xs[i] * xs[j]
        if any(r): Aub.append(r); bub.append(tot * tot // 4)
    bnd = []
    for (i, j) in V:
        hi = c[i] ** 2 // 4 if i == j else min(c[i] * min(i, c[j]), c[j] * min(j, c[i]))
        lo = 0
        if i + j <= 10: lo = c[i] * (c[i] - 1) // 2 if i == j else c[i] * c[j]
        bnd.append((lo, hi))
    if any(lo > hi for lo, hi in bnd): return False
    r = linprog(np.zeros(len(V)), A_ub=np.array(Aub), b_ub=np.array(bub), A_eq=np.array(Aeq),
                b_eq=np.array(beq), bounds=bnd, method='highs')
    return r.status == 0

def t9(n, U):
    L = {d: max(E9[39 - d], U.get(d, -1) + 1) for d in D}
    for T in range(85, 100):
        L[9] = T + 1
        if not feasible(n, L): return T
    return None

surv = []
def comps(t, k):
    if k == 1: yield (t,); return
    for a in range(t + 1):
        for r in comps(t - a, k - 1): yield (a,) + r
for n in comps(40, 6):
    if simple(n): surv.append(n)
print('simple-check survivors:', len(surv))
base = {d: E9[39 - d] for d in D}
lpkill = [n for n in surv if not feasible(n, base)]
print('LP kills:', len(lpkill))
ref = {tuple(r['n']): r for r in json.load(open(sys.argv[1]))['survivors']}
mine = set(surv) - set(lpkill)
print('my survivors', len(mine), 'cases', len(ref), 'only mine', len(mine - set(ref)), 'only cases', len(set(ref) - mine))
if '--t9' in sys.argv:
    hi = lo = eq = 0
    for n in sorted(mine & set(ref)):
        if n == (0, 0, 0, 0, 0, 40): continue
        a = t9(n, {8: 96}); b = ref[n]['t9_U8']
        if a is None or a > b: hi += 1; print('MINE HIGHER', n, a, b)
        elif a < b: lo += 1
        else: eq += 1
    print('t9_U8: equal', eq, 'mine lower', lo, 'mine higher', hi)
