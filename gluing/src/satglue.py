"""Hybrid test: fix H = G_v in R(3,9;30,99); SAT decides if a 9-regular (3,10;40)-graph G
with G_v = H exists. Lazy (CEGAR) alpha constraints.

vars x[i][h]: u_i ~ h (i < 9 neighbours of v, h in H).
 - N_H(u_i) independent in H, |N_H(u_i)| = 8
 - deg_G(h) = 9: sum_i x[i][h] = 9 - deg_H(h)
 - for independent sets I of H (|I| = s): #{i : u_i hits I} >= s
   (initially all I with |I| = 8, and optionally 7; others added lazily when a model
   has an independent 10-set)
 - symmetry: rows x[0] >=lex x[1] >=lex ... (u_i interchangeable)
usage: python satglue.py FILE.g6 [maxgraphs] [init_sizes, e.g. 8 or 7,8]
"""
import sys, time, itertools
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

def g6dec(s):
    n = ord(s[0]) - 63
    bits = []
    for ch in s[1:]:
        x = ord(ch) - 63
        bits += [(x >> (5 - t)) & 1 for t in range(6)]
    adj = [0] * n
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                adj[i] |= 1 << j; adj[j] |= 1 << i
            k += 1
    return n, adj

def indep_sets(n, adj, size):
    out = []
    def rec(cur, sz, allowed):
        if sz == size:
            out.append(cur); return
        while allowed:
            x = (allowed & -allowed).bit_length() - 1
            allowed &= allowed - 1
            if bin(allowed).count('1') + 1 < size - sz:
                return
            rec(cur | (1 << x), sz + 1, allowed & ~adj[x])
    rec(0, 0, (1 << n) - 1)
    return out

def find_indep(adj, m, k):
    """return an independent set of size k inside mask m (as bitmask) or None"""
    if k <= 0:
        return 0
    if bin(m).count('1') < k:
        return None
    # pick vertex of max degree
    best, bd = -1, -1
    t = m
    while t:
        v = (t & -t).bit_length() - 1; t &= t - 1
        d = bin(adj[v] & m).count('1')
        if d > bd:
            bd, best = d, v
    if bd == 0:
        r = 0; t = m; c = 0
        while c < k:
            v = (t & -t).bit_length() - 1; t &= t - 1; r |= 1 << v; c += 1
        return r
    r = find_indep(adj, m & ~adj[best] & ~(1 << best), k - 1)
    if r is not None:
        return r | (1 << best)
    return find_indep(adj, m & ~(1 << best), k)

def solve_one(s, init_sizes):
    n, adj = g6dec(s)
    deg = [bin(a).count('1') for a in adj]
    pool = IDPool()
    X = [[pool.id(('x', i, h)) for h in range(n)] for i in range(9)]
    S = Cadical153()
    for a in range(n):
        for b in range(a + 1, n):
            if adj[a] >> b & 1:
                for i in range(9):
                    S.add_clause([-X[i][a], -X[i][b]])
    for i in range(9):
        for c in CardEnc.equals(lits=X[i], bound=8, vpool=pool, encoding=EncType.seqcounter).clauses:
            S.add_clause(c)
    for h in range(n):
        for c in CardEnc.equals(lits=[X[i][h] for i in range(9)], bound=9 - deg[h], vpool=pool,
                                encoding=EncType.seqcounter).clauses:
            S.add_clause(c)
    # lex order rows (x[i] >= x[i+1]) via standard chain encoding
    for i in range(8):
        a, b = X[i], X[i + 1]
        eq = [pool.id(('eq', i, h)) for h in range(n)]  # eq[h]: prefix 0..h-1 equal
        # eq[0] true
        S.add_clause([eq[0]])
        for h in range(n):
            # if prefix equal then a[h] >= b[h]
            S.add_clause([-eq[h], a[h], -b[h]])
            if h + 1 < n:
                # eq[h+1] -> eq[h] and a[h] == b[h]
                S.add_clause([-eq[h + 1], eq[h]])
                S.add_clause([-eq[h + 1], -a[h], b[h]])
                S.add_clause([-eq[h + 1], a[h], -b[h]])
                # eq[h] and a[h]==b[h] -> eq[h+1]
                S.add_clause([-eq[h], a[h], b[h], eq[h + 1]])
                S.add_clause([-eq[h], -a[h], -b[h], eq[h + 1]])
    nI = [0]
    def add_I(I):
        hs = [h for h in range(n) if I >> h & 1]
        sz = len(hs)
        ys = []
        for i in range(9):
            y = pool.id(('y', i, I))
            S.add_clause([-y] + [X[i][h] for h in hs])
            ys.append(y)
        for c in CardEnc.atleast(lits=ys, bound=sz, vpool=pool, encoding=EncType.seqcounter).clauses:
            S.add_clause(c)
        nI[0] += 1
    for sz in init_sizes:
        for I in indep_sets(n, adj, sz):
            add_I(I)
    it = 0
    while True:
        it += 1
        if not S.solve():
            S.delete(); return 'UNSAT', it, nI[0]
        model = set(l for l in S.get_model() if l > 0)
        N = n + 10
        gadj = adj[:] + [0] * 10
        v = n + 9
        for i in range(9):
            u = n + i
            gadj[u] |= 1 << v; gadj[v] |= 1 << u
            for h in range(n):
                if X[i][h] in model:
                    gadj[u] |= 1 << h; gadj[h] |= 1 << u
        J = find_indep(gadj, (1 << N) - 1, 10)
        if J is None:
            S.delete(); return 'SAT', it, nI[0]
        I = J & ((1 << n) - 1)
        add_I(I)

def main():
    fn = sys.argv[1]
    mx = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
    init = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else [8]
    tot = 0
    res = {}
    for k, line in enumerate(open(fn)):
        if k >= mx:
            break
        t = time.time()
        r, it, nI = solve_one(line.strip(), init)
        dt = time.time() - t
        tot += dt
        res[r] = res.get(r, 0) + 1
        print(f'{k} {r} iters={it} Isets={nI} {dt:.3f}s', flush=True)
    print('total', tot, 'per graph', tot / max(1, sum(res.values())), res)

main()
