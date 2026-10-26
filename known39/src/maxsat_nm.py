"""Exact near miss: min over independent S of #independent 9-sets missed by S (RC2 MaxSAT).
Usage: maxsat_nm.py FILE.g6   prints: n n9 min_unmet S g6(G+w)"""
import sys
sys.path.insert(0, './tools')
sys.path.insert(0, './known39/src')
from check_graph import parse_graph6, to_graph6
from sat_ext import indep_sets
from pysat.formula import WCNF
from pysat.examples.rc2 import RC2
for line in open(sys.argv[1]):
    g6 = line.split()[-1].strip()
    if not g6 or g6[0] == '#': continue
    adj = parse_graph6(g6); n = len(adj)
    T = indep_sets(adj, 9)
    w = WCNF()
    for u in range(n):
        for v in range(u + 1, n):
            if adj[u] >> v & 1: w.append([-(u + 1), -(v + 1)])
    for t in T: w.append([v + 1 for v in t], weight=1)
    with RC2(w) as r:
        m = r.compute(); cost = r.cost
    S = [v for v in range(n) if m[v] > 0]
    a = adj + [sum(1 << v for v in S)]
    for v in S: a[v] |= 1 << n
    print(n, len(T), cost, S, to_graph6(a), flush=True)
