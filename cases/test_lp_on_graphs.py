#!/usr/bin/env python3
"""Soundness test for the LP rows of degseq.build_lp: evaluate every row on REAL graphs.
For a (3,10,n)-graph G, the true edge counts m_ij between degree classes must satisfy all
rows, with L_i = true min e(H_v) over class i.  The pair-lemma forced rows use
d(u)+d(v) <= n - 30 (from R(3,8) = 28: |V - N[u] - N[v]| = n-2-d(u)-d(v)+c <= 27).
Usage: tools/venv/bin/python cases/test_lp_on_graphs.py FILE.g6 [...]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import networkx as nx
import degseq as D

bad = 0
for path in sys.argv[1:]:
    for line in open(path):
        line = line.strip()
        if line.startswith('>>graph6<<'):
            line = line[len('>>graph6<<'):]
        if not line:
            continue
        G = nx.from_graph6_bytes(line.encode())
        nv = G.number_of_nodes()
        deg = dict(G.degree())
        degs = tuple(sorted(set(deg.values())))
        D.DEGS = degs
        n = tuple(sum(1 for v in G if deg[v] == d) for d in degs)
        L = {}
        for v in G:
            H = G.copy(); H.remove_nodes_from(list(G[v]) + [v])
            L[deg[v]] = min(L.get(deg[v], 10**9), H.number_of_edges())
        var, rows, ub = D.build_lp(n, L, forced_max=nv - 30)
        m = {k: 0 for k in var}
        for a, b in G.edges():
            i, j = sorted((deg[a], deg[b]))
            m[(i, j)] += 1
        for c, rhs, name in rows:
            lhs = sum(v * m[k] for k, v in c.items())
            if lhs > rhs:
                bad += 1
                print("VIOLATED", path, name, c, lhs, rhs, n)
        print(f"ok n={nv} e={G.number_of_edges()} dist={dict(zip(degs, n))} rows={len(rows)}")
print("violations:", bad)
