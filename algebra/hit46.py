"""Delete d vertices from a (3,11,n)-graph to obtain a (3,10,n-d)-graph: minimum hitting set of independent 10-sets."""
import sys
sys.path.insert(0, './algebra')
import ev, ext2
from pysat.solvers import Cadical153
from pysat.card import CardEnc

def load_lists(fn):
    L = [list(map(int, l.split())) for l in open(fn) if l.strip()]
    n = len(L); return ev.from_edges(n, [(i, j) for i in range(n) for j in L[i]])
def load_matrix(fn):
    M = [l.strip() for l in open(fn) if l.strip()]; n = len(M)
    a = ev.from_edges(n, [(i, j) for i in range(n) for j in range(n) if M[i][j] == '1'])
    b = ev.from_edges(n, [(i, j) for i in range(n) for j in range(i + 1, n) if M[i][j] == '0'])
    return a if ev.tri(a) == 0 else b

for name, adj in [('g.3.11.46', load_lists('../data/graphs/exoo/g.3.11.46')), ('r3.11.46', load_matrix('../data/graphs/exoo/r3.11.46'))]:
    n = len(adj)
    print(name, 'n', n, 'tri', ev.tri(adj), 'alpha', ev.alpha(adj), 'c10', ev.indep(adj, 10), 'c11', ev.indep(adj, 11), flush=True)
    I = ext2.indep_sets(adj, 10)
    for d in range(int(sys.argv[1]) if len(sys.argv) > 1 else 1, n):
        s = Cadical153()
        for S in I: s.add_clause([v + 1 for v in S])
        enc = CardEnc.atmost(list(range(1, n + 1)), bound=d, top_id=n)
        for c in enc.clauses: s.add_clause(c)
        r = s.solve(); print(f'  delete <= {d} vertices hits all 10-sets: {r}', flush=True)
        if r:
            m = [l - 1 for l in s.get_model()[:n] if l > 0]; print('  hitting set', m); break
