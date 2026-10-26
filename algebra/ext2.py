"""Exact check: can a (3,10,n)-graph G be extended by 2 new vertices u, w to a (3,10,n+2)-graph?
Variables x_v = [v ~ u], y_v = [v ~ w], e = [u ~ w].
Constraints: N(u), N(w) independent in G; e -> N(u), N(w) disjoint;
every independent 9-set I of G meets N(u) and meets N(w);
if not e: every independent 8-set I of G meets N(u) or N(w).
usage: ext2.py file.g6   (each line one graph)
"""
import sys, itertools
sys.path.insert(0, './algebra')
import ev
from pysat.solvers import Cadical153

def indep_sets(adj, k):
    n = len(adj); out = []
    def rec(cand, S):
        if len(S) == k: out.append(S); return
        while cand:
            if bin(cand).count('1') < k - len(S): return
            v = (cand & -cand).bit_length() - 1; cand &= cand - 1
            rec(cand & ~adj[v], S + [v])
    rec((1 << n) - 1, []); return out

def extend2(adj, K=10):
    n = len(adj); X = lambda v: v + 1; Y = lambda v: n + v + 1; E = 2 * n + 1
    s = Cadical153()
    for a in range(n):
        for b in range(a + 1, n):
            if adj[a] >> b & 1:
                s.add_clause([-X(a), -X(b)]); s.add_clause([-Y(a), -Y(b)])
    for v in range(n): s.add_clause([-E, -X(v), -Y(v)])
    I9 = indep_sets(adj, K - 1); I8 = indep_sets(adj, K - 2)
    for I in I9:
        s.add_clause([X(v) for v in I]); s.add_clause([Y(v) for v in I])
    for I in I8:
        s.add_clause([E] + [X(v) for v in I] + [Y(v) for v in I])
    r = s.solve()
    res = None
    if r:
        m = set(l for l in s.get_model() if l > 0)
        new = adj + [0, 0]
        for v in range(n):
            if X(v) in m: new[v] |= 1 << n; new[n] |= 1 << v
            if Y(v) in m: new[v] |= 1 << (n + 1); new[n + 1] |= 1 << v
        if E in m: new[n] |= 1 << (n + 1); new[n + 1] |= 1 << n
        res = new
    return r, len(I9), len(I8), res

if __name__ == '__main__':
    for line in open(sys.argv[1]):
        if not line.strip(): continue
        adj = ev.from_graph6(line)
        r, a, b, new = extend2(adj)
        print(line.strip(), 'n', len(adj), 'I9', a, 'I8', b, 'SAT' if r else 'UNSAT', flush=True)
        if r:
            print('EXT', ev.to_graph6(new), ev.score(new))
