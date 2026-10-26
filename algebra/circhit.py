"""For triangle-free circulants C_N(S) with alpha <= 10, N in 41..45: min #vertices hitting all independent 10-sets.
A hitting set of size N-40 gives a (3,10,40)-graph. Vertex-transitivity: need N-40 >= N/10 * (overlap) -> only N=45 possible."""
import sys
sys.path.insert(0, './algebra')
import ev, circ, ext2
from pysat.solvers import Cadical153
from pysat.card import CardEnc
for N in [int(x) for x in sys.argv[1:]]:
    sets = circ.search(N, 11)
    print(N, 'circulants with alpha<=10:', len(sets), flush=True)
    for S in sets:
        adj = circ.circ(N, S); I = ext2.indep_sets(adj, 10); d = N - 40
        s = Cadical153()
        for T in I: s.add_clause([v + 1 for v in T])
        s.add_clause([1])  # WLOG vertex 0 deleted (vertex-transitive)
        for c in CardEnc.atmost(list(range(1, N + 1)), bound=d, top_id=N).clauses: s.add_clause(c)
        r = s.solve()
        print(f"  S={S} c10={len(I)} hit with {d}: {r}", flush=True)
        if r: print('  FOUND?', [l - 1 for l in s.get_model()[:N] if l > 0])
