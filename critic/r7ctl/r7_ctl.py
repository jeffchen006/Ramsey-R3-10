#!/usr/bin/env python3
"""Case R7 (notes/cases_local.md, Lemma R7): a 9-regular (3,10,40)-graph G with non-adjacent
u, v having c = 7 common neighbours.  Then X = V - N[u] - N[v] is in R(3,8,27,85) (4 graphs,
[GR] Table 13; HoG file Ramseygraphs_3_8_27_e85.g6), and with C = N(u) & N(v) (7 vertices),
A = N(u) - C (2), B = N(v) - C (2), every vertex of A is adjacent to every vertex of B.

This script writes, for each X, a COMPLETE CNF for "X extends to such a G" (no lazy clauses):
Vertices: X = 0..26 (fixed graph), u = 27, v = 28, C = 29..35, A = 36,37, B = 38,39.
Fixed edges: X; u-C, u-A, v-C, v-B, A-B.  Unknown: x[s,y] for s in S = C+A+B, y in X.
  (T) triangle-free: x[s,y] & x[s,y'] false if y ~ y' in X; x[a,y] & x[b,y] false for a in A, b in B.
      (Fixed part is triangle-free; u, v have no X-neighbours, so no other triangles.)
  (D) 9-regular: |N(s) & X| = 7 for s in C, = 6 for s in A + B; |N(y) & S| = 9 - deg_X(y).
  (I) no independent 10-set J.  J = T' + I, T' = J - X independent in the fixed part on
      {u, v} + S, I = J & X independent in X, |I| <= alpha(X) = 7, so |T'| >= 3.  Independent T'
      with |T'| >= 3 are: C' + A' or C' + B' (C' in C, A' in A, B' in B), {u} + B, {v} + A
      ({u, v} + I needs |I| = 8, impossible).  Clause: OR of x[t,y], t in T' & S, y in I.
Run: tools/venv/bin/python cases/r7_glue.py data/graphs/hog/Ramseygraphs_3_8_27_e85.g6 OUTDIR
then solve OUTDIR/r7_X<i>.cnf with cadical + DRAT (see notes/cases_local.md Sec 4).
"""
import itertools
import os
import sys

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool

U, V = 27, 28
C = list(range(29, 36))
A = [36, 37]
B = [38, 39]
S = C + A + B
NX = 27
KK = int(os.environ.get("KK", "10"))


def all_indep(adj, n, k):
    """All independent k-sets of a graph given by neighbour bitmasks."""
    def rec(start, chosen, forbid):
        if len(chosen) == k:
            yield list(chosen)
            return
        for w in range(start, n):
            if not (forbid >> w) & 1:
                yield from rec(w + 1, chosen + [w], forbid | adj[w] | (1 << w))
    yield from rec(0, [], 0)


def fixed_indep_sets():
    """All independent T' in the fixed graph on {u, v} + S with |T'| >= 3, as
    (T' & S, |T'|).  T' containing u or v contributes only its S-part to clauses."""
    out = []
    for kc in range(0, 8):
        for Cp in itertools.combinations(C, kc):
            for side in (A, B):
                for ks in range(1 if side is B else 0, 3):   # A' may be empty; B' nonempty
                    for Sp in itertools.combinations(side, ks):
                        T = list(Cp) + list(Sp)
                        if len(T) >= KK - 7:
                            out.append((T, len(T)))
    out.append((list(B), 3))   # {u} + B
    out.append((list(A), 3))   # {v} + A
    return out


def build(X):
    pool = IDPool()
    x = {(s, y): pool.id(("x", s, y)) for s in S for y in range(NX)}
    cnf = CNF()
    adjX = [0] * NX
    for a, b in X.edges():
        adjX[a] |= 1 << b
        adjX[b] |= 1 << a
    for s in S:                                   # (T)
        for a, b in X.edges():
            cnf.append([-x[(s, a)], -x[(s, b)]])
    for a in A:
        for b in B:
            for y in range(NX):
                cnf.append([-x[(a, y)], -x[(b, y)]])
    for s in S:                                   # (D)
        need = 7 if s in C else 6
        cnf.extend(CardEnc.equals([x[(s, y)] for y in range(NX)], bound=need, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
    for y in range(NX):
        need = 9 - bin(adjX[y]).count("1")
        cnf.extend(CardEnc.equals([x[(s, y)] for s in S], bound=need, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
    indep = {k: list(all_indep(adjX, NX, k)) for k in range(1, 8)}
    assert not list(all_indep(adjX, NX, 8)), "alpha(X) must be 7"
    nI = 0
    for T, t in fixed_indep_sets():               # (I)
        for I in (indep[KK - t] if 0 < KK - t <= 7 else []):
            cnf.append([x[(s, y)] for s in T for y in I])
            nI += 1
    return cnf, nI


def main():
    src, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    idx = 0
    for line in open(src):
        line = line.strip()
        if line.startswith(">>graph6<<"):
            line = line[10:]
        if not line:
            continue
        X = nx.from_graph6_bytes(line.encode())
        assert X.number_of_nodes() == 27 and X.number_of_edges() == 85
        assert nx.is_triangle_free(X) if hasattr(nx, "is_triangle_free") else True
        cnf, nI = build(X)
        path = os.path.join(outdir, f"r7_X{idx}.cnf")
        cnf.to_file(path)
        print(f"X{idx}: {cnf.nv} vars, {len(cnf.clauses)} clauses ({nI} independence) -> {path}",
              flush=True)
        idx += 1


if __name__ == "__main__":
    main()
