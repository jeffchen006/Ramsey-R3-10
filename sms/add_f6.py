#!/usr/bin/env python3
"""Add Lemma F (cases) cube R(6, f*>=6) to an R(c*=6) CNF from gen_ramsey.py (agent sms).

Layout: N(0) = {1..9}, N(10) & N(0) = {1..6}. For a non-adjacent pair (u,w),
f(u,w) = e(N(u)-N(w), N(w)-N(u)) = number of paths u-a-b-w (triangle-free).
Adds, for every y in 10..n-1:  codeg(0,y) >= F  ->  f(0,y) >= F   (F = 6; y = 10 always has codeg 6).
This is a relaxation of "every codeg-6 pair has f >= 6" (only pairs through vertex 0), so UNSAT is sound.
usage: add_f6.py IN.cnf OUT.cnf [F] [N] [CSTAR]
"""
import sys
from itertools import combinations

inp, out = sys.argv[1], sys.argv[2]
F = int(sys.argv[3]) if len(sys.argv) > 3 else 6
n = int(sys.argv[4]) if len(sys.argv) > 4 else 40
cs = int(sys.argv[5]) if len(sys.argv) > 5 else 6
d = 9
var = {}
c = 0
for i in range(n):
    for j in range(i + 1, n):
        c += 1
        var[(i, j)] = c
e = lambda i, j: var[(min(i, j), max(i, j))]
with open(inp) as fh:
    hdr = fh.readline().split()
    body = fh.read()
nv = int(hdr[2])
C = []


def new():
    global nv
    nv += 1
    return nv


def atleast_if(lits, K, cond):
    """cond -> sum(lits) >= K. s[i][j]: >= j+1 true among lits[0..i]."""
    m = len(lits)
    s = [[new() for _ in range(K)] for _ in range(m)]
    C.append([-s[0][0], lits[0]])
    for j in range(1, K):
        C.append([-s[0][j]])
    for i in range(1, m):
        for j in range(K):
            C.append([-s[i][j], s[i - 1][j], lits[i]])
            if j > 0:
                C.append([-s[i][j], s[i - 1][j], s[i - 1][j - 1]])
    C.append([-cond, s[m - 1][K - 1]])


for y in range(d + 1, n):
    # g -> codeg(0,y) >= F detection: any F of e(y,1..9) true -> g
    if y == d + 1:
        g = None
    else:
        g = new()
        for S in combinations(range(1, d + 1), F):
            C.append([-e(y, a) for a in S] + [g])
    ts = []
    for a in range(1, d + 1):
        for b in range(d + 1, n):
            if b == y:
                continue
            t = new()
            C.append([-t, e(a, b)])
            C.append([-t, e(b, y)])
            C.append([-t, -e(y, a)])  # a not in N(y) (implied by triangle-free)
            ts.append(t)
    if g is None:
        g = new()
        C.append([g])
    atleast_if(ts, F, g)
with open(out, "w") as fh:
    fh.write(f"p cnf {nv} {int(hdr[3]) + len(C)}\n")
    fh.write(body)
    for cl in C:
        fh.write(" ".join(map(str, cl)) + " 0\n")
print(f"{out}: vars {nv}, added {len(C)} clauses")
