"""Hybrid test 2: fix X = G - N[u] - N[w] (u, w non-adjacent) in R(3,8;27), i.e. |X| = 27,
and let SAT find the other 13 vertices (u, w, Y = N(u) | N(w), |Y| = 11) of a (3,10;40)-graph.
No degree or regularity assumption beyond Delta <= 9.

vars: au[y], aw[y] (y ~ u, y ~ w), with au|aw for all y (every y is in N(u) | N(w));
      e[y][y'] (11*10/2), f[y][x] (11*27).
constraints: triangle-free; Delta <= 9 (seq counters); alpha <= 9 lazily (CEGAR: independent
10-set found in a model -> clause "one of its variable pairs is an edge");
symmetry: rows of Y lex-ordered (Y vertices are interchangeable).
usage: python3 satx.py X.g6 [max] [skip]
"""
import sys, time, itertools
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

sys.setrecursionlimit(10000)

def g6dec(s):
    n = ord(s[0]) - 63; bits = []
    for ch in s[1:]:
        x = ord(ch) - 63; bits += [(x >> (5 - t)) & 1 for t in range(6)]
    adj = [0] * n; k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]: adj[i] |= 1 << j; adj[j] |= 1 << i
            k += 1
    return n, adj

def find_indep(adj, m, k):
    if k <= 0: return 0
    if bin(m).count('1') < k: return None
    best, bd = -1, -1; t = m
    while t:
        v = (t & -t).bit_length() - 1; t &= t - 1
        d = bin(adj[v] & m).count('1')
        if d > bd: bd, best = d, v
    if bd == 0:
        r = 0; t = m
        for _ in range(k):
            v = (t & -t).bit_length() - 1; t &= t - 1; r |= 1 << v
        return r
    r = find_indep(adj, m & ~adj[best] & ~(1 << best), k - 1)
    if r is not None: return r | (1 << best)
    return find_indep(adj, m & ~(1 << best), k)

def all_indep(adj, m, k, cur, out, cap):
    if len(out) >= cap: return
    if k == 0:
        out.append(cur); return
    if bin(m).count('1') < k: return
    v = (m & -m).bit_length() - 1
    all_indep(adj, m & ~adj[v] & ~(1 << v), k - 1, cur | (1 << v), out, cap)
    all_indep(adj, m & ~(1 << v), k, cur, out, cap)

CAP = int(__import__('os').environ.get('SATX_CAP', '200'))

def solve(s):
    nX, xadj = g6dec(s)
    NY = 11
    # vertex ids in G: X = 0..26, Y = 27..37, u = 38, w = 39
    Y = list(range(nX, nX + NY)); U, Wv = nX + NY, nX + NY + 1
    pool = IDPool()
    var = {}
    def ev(a, b):
        if a > b: a, b = b, a
        return var.setdefault((a, b), pool.id((a, b)))
    S = Cadical153()
    for y in Y:
        S.add_clause([ev(y, U), ev(y, Wv)])
    # triangle-free
    for y in Y:
        for x in range(nX):
            for x2 in range(x + 1, nX):
                if xadj[x] >> x2 & 1:
                    S.add_clause([-ev(y, x), -ev(y, x2)])
        for y2 in Y:
            if y2 <= y: continue
            for x in range(nX):
                S.add_clause([-ev(y, y2), -ev(y, x), -ev(y2, x)])
            for z in (U, Wv):
                S.add_clause([-ev(y, y2), -ev(y, z), -ev(y2, z)])
            for y3 in Y:
                if y3 <= y2: continue
                S.add_clause([-ev(y, y2), -ev(y, y3), -ev(y2, y3)])
    # degrees <= 9
    def atmost(lits, b):
        if b < 0:
            S.add_clause([]); return
        if len(lits) <= b: return
        for c in CardEnc.atmost(lits=lits, bound=b, vpool=pool, encoding=EncType.seqcounter).clauses:
            S.add_clause(c)
    atmost([ev(y, U) for y in Y], 9)
    atmost([ev(y, Wv) for y in Y], 9)
    for y in Y:
        atmost([ev(y, z) for z in list(range(nX)) + [q for q in Y if q != y] + [U, Wv]], 9)
    for x in range(nX):
        atmost([ev(y, x) for y in Y], 9 - bin(xadj[x]).count('1'))
    # lex order of Y rows: row(y) = [au, aw, f[y][0..26]] (edges among Y excluded for simplicity)
    rows = [[ev(y, U), ev(y, Wv)] + [ev(y, x) for x in range(nX)] for y in Y]
    for i in range(NY - 1):
        a, b = rows[i], rows[i + 1]; L = len(a)
        eq = [pool.id(('eq', i, h)) for h in range(L)]
        S.add_clause([eq[0]])
        for h in range(L):
            S.add_clause([-eq[h], a[h], -b[h]])
            if h + 1 < L:
                S.add_clause([-eq[h + 1], eq[h]])
                S.add_clause([-eq[h + 1], -a[h], b[h]]); S.add_clause([-eq[h + 1], a[h], -b[h]])
                S.add_clause([-eq[h], a[h], b[h], eq[h + 1]]); S.add_clause([-eq[h], -a[h], -b[h], eq[h + 1]])
    N = nX + NY + 2
    it = 0; T0 = time.time()
    while True:
        it += 1
        if it % 200 == 0:
            print(f'  iter {it} t={time.time()-T0:.1f}s', flush=True)
        if not S.solve():
            S.delete(); return 'UNSAT', it
        model = set(l for l in S.get_model() if l > 0)
        gadj = xadj[:] + [0] * (NY + 2)
        for (a, b), v in var.items():
            if v in model:
                gadj[a] |= 1 << b; gadj[b] |= 1 << a
        Js = []
        all_indep(gadj, (1 << N) - 1, 10, 0, Js, CAP)
        if not Js:
            S.delete(); return 'SAT', it
        for J in Js:
            vs = [i for i in range(N) if J >> i & 1]
            cl = []
            for a, b in itertools.combinations(vs, 2):
                if a < nX and b < nX: continue
                if {a, b} == {U, Wv}: continue
                if (a in (U, Wv) and b < nX) or (b in (U, Wv) and a < nX): continue
                cl.append(ev(a, b))
            S.add_clause(cl)

def main():
    fn = sys.argv[1]; mx = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
    skip = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    tot = 0; res = {}; k = 0
    for i, line in enumerate(open(fn)):
        if i % skip: continue
        if k >= mx: break
        k += 1
        t = time.time(); r, it = solve(line.strip()); dt = time.time() - t
        tot += dt; res[r] = res.get(r, 0) + 1
        print(f'{i} {r} iters={it} {dt:.2f}s', flush=True)
    print('total', round(tot, 1), 'per graph', tot / max(1, k), res)

main()
