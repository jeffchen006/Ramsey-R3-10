#!/usr/bin/env python3
"""analyze.py K FILE...: degree histogram, independent K-sets, how many are N(v) sets."""
import sys, itertools
sys.path.insert(0, './tools')
from check_graph import parse_graph6
def indep_sets(adj, k):
    n = len(adj); out = []
    def rec(S, P, need):
        if need == 0: out.append(S); return
        while P and bin(P).count('1') >= need:
            v = (P & -P).bit_length() - 1; P &= P - 1
            rec(S | 1 << v, P & ~adj[v], need - 1)
    rec(0, (1 << n) - 1, k); return out
k = int(sys.argv[1])
for fn in sys.argv[2:]:
    for line in open(fn):
        if not line.strip(): continue
        adj = parse_graph6(line.strip()); n = len(adj)
        deg = [bin(a).count('1') for a in adj]
        hist = {d: deg.count(d) for d in sorted(set(deg))}
        bad = indep_sets(adj, k)
        nb = sum(1 for S in bad if any(S & ~adj[v] == 0 and bin(adj[v] & S).count('1') == k for v in range(n)))
        print(fn.split('/')[-1], 'n=%d e=%d deg=%s bad=%d in_nbhd=%d' % (n, sum(deg)//2, hist, len(bad), nb))
