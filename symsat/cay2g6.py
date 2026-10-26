#!/usr/bin/env python3
"""cay2g6.py GROUPFILE "{s1,s2,...}" -> graph6 of Cay(G,S) on stdout (g~h iff g^-1 h in S)."""
import sys
sys.path.insert(0, "./tools")
from check_graph import to_graph6
rows = open(sys.argv[1]).read().split("\n")
n = int(rows[0]); T = [list(map(int, r.split())) for r in rows[1:n+1]]
S = set(map(int, sys.argv[2].strip("{}").split(",")))
inv = [next(h for h in range(n) if T[g][h] == 0) for g in range(n)]
adj = [0]*n
for g in range(n):
    for h in range(n):
        if T[inv[g]][h] in S: adj[g] |= 1 << h
assert all(not (adj[g] >> g) & 1 for g in range(n)) and all(((adj[h] >> g) & 1) == ((adj[g] >> h) & 1) for g in range(n) for h in range(n))
print(to_graph6(adj))
