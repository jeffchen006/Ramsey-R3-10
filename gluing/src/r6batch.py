"""R(6, f* <= 5) sub-case of the 9-regular case (notes/cases_local.md, Lemma F): batched SAT (W1, Wesley
arXiv:2606.17021 Sec 4.4) with lazy alpha (CEGAR).

G = X + 14 new vertices. X = vertices 0..25 (one graph of the batch, chosen by a selector s_H).
New: U = 26 ("0"), W = 27 ("10"), C = 28..33, A = 34..36, B = 37..39.
Fixed edges: U-C, U-A, W-C, W-B. Variables: x_yz (X pairs, fixed by the selector), A-B (9), C/A/B - X (12 x 26).
Shared clauses: triangle-free, 9-regular, alpha <= 9 (lazy: each model is checked; an independent 10-set I
gives the clause "some variable pair inside I is an edge", valid for every X), plus cases' hook
cases/r6_constraints.py: extra(vp, xv, nv, abv, batch) -> clauses (optional).
Result per batch: UNSAT (no X of the batch extends) or FOUND graphs (written to OUTDIR/FOUND_*.g6).

usage: tools/venv/bin/python r6batch.py BATCH.g6 OUTDIR [--max-iter N] [--alpha 9]  (--alpha 10 = positive control)
"""
import sys, os, time, importlib.util
from pysat.solvers import Cadical195
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

NX, N = 26, 40
U, W = 26, 27
C, A, B = list(range(28, 34)), list(range(34, 37)), list(range(37, 40))
NEW = C + A + B  # new vertices with X neighbours

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

def g6enc(n, adj):
    bits = [(adj[i] >> j) & 1 for j in range(1, n) for i in range(j)]
    while len(bits) % 6: bits.append(0)
    return chr(63 + n) + ''.join(chr(63 + int(''.join(map(str, bits[k:k + 6])), 2)) for k in range(0, len(bits), 6))

def find_indep(adj, m, k):
    if k <= 0: return 0
    if bin(m).count('1') < k: return None
    best, bd, t = -1, -1, m
    while t:
        v = (t & -t).bit_length() - 1; t &= t - 1
        d = bin(adj[v] & m).count('1')
        if d > bd: bd, best = d, v
    if bd == 0:
        r, t, c = 0, m, 0
        while c < k:
            v = (t & -t).bit_length() - 1; t &= t - 1; r |= 1 << v; c += 1
        return r
    r = find_indep(adj, m & ~adj[best] & ~(1 << best), k - 1)
    if r is not None: return r | (1 << best)
    return find_indep(adj, m & ~(1 << best), k)

def main():
    fn, outdir = sys.argv[1], sys.argv[2]
    maxit = int(sys.argv[sys.argv.index('--max-iter') + 1]) if '--max-iter' in sys.argv else 10 ** 9
    K = int(sys.argv[sys.argv.index('--alpha') + 1]) + 1 if '--alpha' in sys.argv else 10  # forbidden indep. set size
    os.makedirs(outdir, exist_ok=True)
    graphs = [l.strip() for l in open(fn) if l.strip()]
    t0 = time.time()
    vp = IDPool()
    xv = {(i, j): vp.id(('x', i, j)) for j in range(NX) for i in range(j)}
    nv = {(p, y): vp.id(('n', p, y)) for p in NEW for y in range(NX)}
    abv = {(a, b): vp.id(('ab', a, b)) for a in A for b in B}
    sel = [vp.id(('s', h)) for h in range(len(graphs))]
    def X(i, j): return xv[(min(i, j), max(i, j))]
    def pairvar(p, q):  # variable for pair p,q of G, or None if the pair is fixed
        if p > q: p, q = q, p
        if q < NX: return xv[(p, q)]
        if p < NX and q in NEW: return nv[(q, p)]
        if p in A and q in B: return abv[(p, q)]
        return None
    fixed_edges = [(U, c) for c in C + A] + [(W, c) for c in C + B]
    S = Cadical195()
    def add(cl): S.add_clause(cl)
    # selectors: s_H -> X = H
    for h, g in enumerate(graphs):
        n, adj = g6dec(g); assert n == NX
        s = sel[h]
        for (i, j), v in xv.items():
            add([-s, v] if (adj[i] >> j) & 1 else [-s, -v])
    add(list(sel))
    # triangle-free
    for p in NEW:
        for (i, j), v in xv.items(): add([-nv[(p, i)], -nv[(p, j)], -v])
    for (a, b), v in abv.items():
        for y in range(NX): add([-v, -nv[(a, y)], -nv[(b, y)]])
    # degrees (9-regular)
    def card_eq(lits, k):
        for cl in CardEnc.equals(lits=lits, bound=k, vpool=vp, encoding=EncType.totalizer).clauses: add(cl)
    for y in range(NX):
        card_eq([X(y, z) for z in range(NX) if z != y] + [nv[(p, y)] for p in NEW], 9)
    for c in C: card_eq([nv[(c, y)] for y in range(NX)], 7)
    for a in A: card_eq([nv[(a, y)] for y in range(NX)] + [abv[(a, b)] for b in B], 8)
    for b in B: card_eq([nv[(b, y)] for y in range(NX)] + [abv[(a, b)] for a in A], 8)
    # cases' extra constraints
    hook = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../cases/r6_constraints.py')
    nextra = 0
    if os.path.exists(hook):
        spec = importlib.util.spec_from_file_location('r6c', hook); m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        for cl in m.extra(vp, xv, nv, abv, graphs): add(cl); nextra += 1
    tb = time.time() - t0
    print(f"built {len(graphs)} graphs in {tb:.1f}s", file=sys.stderr, flush=True)
    it, nlazy, found = 0, 0, 0
    full = (1 << N) - 1
    while it < maxit:
        it += 1
        if it % 10 == 0: print(f"  iter {it} lazy {nlazy} t={time.time() - t0:.0f}s", file=sys.stderr, flush=True)
        ts = time.time(); r = S.solve(); print(f"  solve {time.time()-ts:.2f}s", file=sys.stderr, flush=True)
        if not r:
            print(f"{fn}: UNSAT graphs={len(graphs)} iter={it} lazy={nlazy} found={found} extra={nextra} "
                  f"build={tb:.1f}s total={time.time() - t0:.1f}s", flush=True)
            return
        model = S.get_model(); val = lambda v: model[v - 1] > 0
        adj = [0] * N
        def edge(p, q): adj[p] |= 1 << q; adj[q] |= 1 << p
        for (i, j), v in xv.items():
            if val(v): edge(i, j)
        for (p, y), v in nv.items():
            if val(v): edge(p, y)
        for (a, b), v in abv.items():
            if val(v): edge(a, b)
        for p, q in fixed_edges: edge(p, q)
        # alpha check: collect several independent 10-sets
        sets, seen = [], set()
        I = find_indep(adj, full, K)
        if I is not None:
            sets.append(I); seen.add(I)
            for v in range(N):
                if (I >> v) & 1:
                    J = find_indep(adj, full & ~(1 << v), K)
                    if J is not None and J not in seen: sets.append(J); seen.add(J)
        if not sets:
            h = next(h for h in range(len(graphs)) if val(sel[h]))
            g = g6enc(N, adj); found += 1
            with open(os.path.join(outdir, f"FOUND_{os.path.basename(fn)}_{h}.g6"), 'a') as f: f.write(g + '\n')
            print(f"FOUND graph from X #{h}: {g}", flush=True)
            add([-sel[h]])  # go on with the rest of the batch
            continue
        for I in sets:
            vs = [v for v in range(N) if (I >> v) & 1]
            cl = [pairvar(vs[a], vs[b]) for a in range(K) for b in range(a + 1, K)]
            add([l for l in cl if l is not None]); nlazy += 1
    print(f"{fn}: STOPPED at max-iter graphs={len(graphs)} iter={it} lazy={nlazy} found={found} total={time.time() - t0:.1f}s")

main()
