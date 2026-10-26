#!/usr/bin/env python3
"""Count isomorphism classes in graph6 files (networkx). usage: isoclasses.py [--mtf] F..."""
import sys, networkx as nx
args = sys.argv[1:]; mtf = '--mtf' in args; files = [a for a in args if a != '--mtf']
def is_mtf(G):
    return all(G.has_edge(u, v) or set(G[u]) & set(G[v]) for u in G for v in G if u < v)
reps = {}
for f in files:
    for l in open(f):
        l = l.strip()
        if not l: continue
        G = nx.from_graph6_bytes(l.encode())
        if mtf and not is_mtf(G): continue
        h = nx.weisfeiler_lehman_graph_hash(G, iterations=4)
        lst = reps.setdefault(h, [])
        if not any(nx.is_isomorphic(G, H) for H in lst): lst.append(G)
print(sum(len(v) for v in reps.values()))
