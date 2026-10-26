#!/usr/bin/env python3
"""Cross-check cayley.c with orbsat: Cay(G,S) graphs = graphs invariant under the regular
left action of G. Usage: test_cayley_sat.py K [group ids]"""
import json, os, sys, time
from orbsat import Problem
K = int(sys.argv[1]); ids = sys.argv[2:] or [str(i) for i in range(14)]
for i in ids:
    rows = open(f"groups/G{i}.txt").read().split("\n")
    n = int(rows[0]); T = [list(map(int, r.split())) for r in rows[1:n+1]]
    gens = [[T[g][h] for h in range(n)] for g in range(1, n)]   # left mult by g
    t = time.time()
    P = Problem(n, K, gens, card=False)
    res, adj, it = P.solve()
    if res == "UNSAT":
        os.makedirs("certs", exist_ok=True)
        json.dump(dict(n=n, K=K, generators=gens, breakers=[],
                       indep_sets=[[v for v in range(n) if (m >> v) & 1] for m in P.indep_sets]),
                  open(f"certs/cayley_G{i}_K{K}.json", "w"))
    print(f"G{i} K={K} vars={P.nv} tri={P.n_tri} result={res} iters={it} indep={P.n_indep} t={time.time()-t:.2f}s", flush=True)
