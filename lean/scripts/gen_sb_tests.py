#!/usr/bin/env python3
"""Random n = 40 SB test clauses (one file per clause) for a differential test of
lean `sbcheck` against cert/check_sb.py.  Usage: gen_sb_tests.py OUTDIR COUNT SEED"""
import os
import random
import sys

out, count, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
n = int(sys.argv[4]) if len(sys.argv) > 4 else 40          # n: write "n=" header field
gen = len(sys.argv) > 4
rng = random.Random(seed)
rowpos = [(i, j) for i in range(n) for j in range(i + 1, n)]
colpos = [(i, j) for j in range(n) for i in range(j)]
colex_id = {(i, j): j * (j - 1) // 2 + i + 1 for (i, j) in rowpos}
row_id = {e: k + 1 for k, e in enumerate(rowpos)}
os.makedirs(out, exist_ok=True)
for t in range(count):
    positions = rng.choice(["rowmajor", "colex"])
    better = rng.choice(["min", "max"])
    vars_ = rng.choice(["colex", "rowmajor"])
    d = rng.choice([0, 0, 5, 8]) if gen else rng.choice([8, 9])
    # witness in Gamma_d, moving only a few vertices
    pi = list(range(n))
    a = list(range(1, d + 1)); b = list(range(d + 1, n))
    blocks = (a, b) if d > 0 else (list(range(n)),)
    for blk in blocks:
        k = rng.choice([0, 2, 2, 3])
        if k:
            S = rng.sample(blk, k)
            T = S[:]; rng.shuffle(T)
            for s_, t_ in zip(S, T):
                pi[s_] = t_
    pinv = [0] * n
    for v, w in enumerate(pi):
        pinv[w] = v
    pos = rowpos if positions == "rowmajor" else colpos
    N = len(pos)
    coef = {}
    for k, (i, j) in enumerate(pos):
        u, w = pinv[i], pinv[j]
        q = (min(u, w), max(u, w))
        if q == (i, j):
            continue
        c = 1 << (N - 1 - k)
        coef[(i, j)] = coef.get((i, j), 0) + c
        coef[q] = coef.get(q, 0) - c
    nz = [e for e, c in coef.items() if c != 0]
    vid = colex_id if vars_ == "colex" else row_id
    lits = []
    for e in nz:
        if rng.random() < 0.93:
            al = rng.randint(0, 1)
            lits.append(-vid[e] if al else vid[e])
    if rng.random() < 0.05 and lits:
        lits.append(-lits[0])  # tautology
    if rng.random() < 0.3:     # extra fixed edge with zero coefficient
        e = rng.choice(rowpos)
        if e not in coef:
            lits.append(rng.choice([1, -1]) * vid[e])
    rng.shuffle(lits)
    with open(os.path.join(out, "t%04d.sb" % t), "w") as f:
        extra = (" n=%d s=8" % n) if gen else ""
        f.write("c order positions=%s better=%s vars=%s d=%d%s\n" % (positions, better, vars_, d, extra))
        f.write(" ".join(map(str, lits)) + " 0 | " + " ".join(map(str, pi)) + "\n")
