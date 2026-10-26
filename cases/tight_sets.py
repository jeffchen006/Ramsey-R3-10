#!/usr/bin/env python3
"""Per graph: max |X_S| over independent s-sets (s = 3..6) and #tight sets (|X_S| = R(3,k-s)-1).
Usage: tools/venv/bin/python cases/tight_sets.py FILE.g6 [--k 10] [--limit N]"""
import argparse, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
import networkx as nx
from local_slack import indep_sets

R = {3: 6, 4: 9, 5: 14, 6: 18, 7: 23, 8: 28, 9: 36}
ap = argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--k", type=int, default=10)
ap.add_argument("--limit", type=int, default=10**9); a = ap.parse_args()
summary = {s: Counter() for s in range(3, 7)}
ng = 0
for line in open(a.file):
    line = line.strip().replace(">>graph6<<", "")
    if not line:
        continue
    ng += 1
    if ng > a.limit:
        ng -= 1; break
    G = nx.from_graph6_bytes(line.encode()); n = G.number_of_nodes()
    adj = [0] * n
    for u, v in G.edges():
        adj[u] |= 1 << v; adj[v] |= 1 << u
    row = []
    for s in range(3, 7):
        bound = R[a.k - s] - 1
        mx = 0; tight = 0
        for I in indep_sets(adj, n, s):
            cov = 0
            for v in I:
                cov |= adj[v] | (1 << v)
            m = n - bin(cov).count("1")
            mx = max(mx, m); tight += (m == bound)
        summary[s][(mx, tight > 0)] += 1
        row.append(f"s{s}:max{mx}/{bound},tight{tight}")
    print(n, G.number_of_edges(), " ".join(row), flush=True)
print("graphs:", ng)
for s, c in summary.items():
    print(f"s={s}: (max m, has tight) -> #graphs: {dict(sorted(c.items()))}")
