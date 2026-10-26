#!/usr/bin/env python3
"""DIMACS encoding of (3,k,n)-graphs for SMS (agent sms, R(3,10) project).

Graph: n vertices, triangle-free, no independent set of size k.
Edge variables use the SMS numbering: row-wise upper triangle, e(0,1)=1, e(0,2)=2, ...

Options:
  --eager-is        add all C(n,k) "no independent k-set" clauses (else use smsg --forbid-independent-set k)
  --dmin/--dmax     degree bounds (sequential counter)
  --emin/--emax     edge-count bounds (sequential counter)
  --h-emax T        with --fix-nbhd d: e(G - N[0]) <= T (also --h-emin)
  --codeg-max c     every pair has <= c common neighbours
  --codeg-pair c    with --fix-nbhd d: N(d+1) & N(0) = {1..c} (max-codegree split; add --codeg-max c)
  --mtf             maximal triangle-free (diameter 2); WLOG for an existence search
  --fix-nbhd d      vertex 0 is adjacent exactly to 1..d; then call smsg with --initial-partition 1 d n-1-d
"""
import argparse
import sys
from itertools import combinations


class Enc:
    def __init__(self, n):
        self.n = n
        self.var = {}
        c = 0
        for i in range(n):
            for j in range(i + 1, n):
                c += 1
                self.var[(i, j)] = c
        self.nvars = c
        self.clauses = []

    def e(self, i, j):
        return self.var[(min(i, j), max(i, j))]

    def new(self):
        self.nvars += 1
        return self.nvars

    def atmost(self, lits, K):
        """Sinz sequential counter: sum(lits) <= K."""
        m = len(lits)
        if K >= m:
            return
        if K == 0:
            for x in lits:
                self.clauses.append([-x])
            return
        s = [[self.new() for _ in range(K)] for _ in range(m - 1)]
        C = self.clauses
        C.append([-lits[0], s[0][0]])
        for j in range(1, K):
            C.append([-s[0][j]])
        for i in range(1, m - 1):
            C.append([-lits[i], s[i][0]])
            C.append([-s[i - 1][0], s[i][0]])
            for j in range(1, K):
                C.append([-lits[i], -s[i - 1][j - 1], s[i][j]])
                C.append([-s[i - 1][j], s[i][j]])
            C.append([-lits[i], -s[i - 1][K - 1]])
        C.append([-lits[m - 1], -s[m - 2][K - 1]])

    def counter(self, lits, lo, hi):
        """lo <= sum(lits) <= hi."""
        self.atmost(lits, hi)
        if lo > 0:
            self.atmost([-x for x in lits], len(lits) - lo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, required=True)
    ap.add_argument("-k", type=int, required=True, help="forbid independent sets of size k")
    ap.add_argument("--eager-is", action="store_true")
    ap.add_argument("--dmin", type=int, default=0)
    ap.add_argument("--dmax", type=int, default=None)
    ap.add_argument("--emin", type=int, default=0)
    ap.add_argument("--emax", type=int, default=None)
    ap.add_argument("--fix-nbhd", type=int, default=None)
    ap.add_argument("--h-emax", type=int, default=None, help="with --fix-nbhd d: at most this many edges inside {d+1..n-1}")
    ap.add_argument("--h-emin", type=int, default=0)
    ap.add_argument("--codeg-max", type=int, default=None, help="every pair has at most this many common neighbours")
    ap.add_argument("--codeg-pair", type=int, default=None,
                    help="with --fix-nbhd d: vertex d+1 has N(d+1) & N(0) = {1..c} (use smsg --initial-partition 1 c d-c 1 n-d-2)")
    ap.add_argument("--edges", default="", help="forced edges 'i-j,i-j,...'")
    ap.add_argument("--nonedges", default="", help="forced non-edges 'i-j,...'")
    ap.add_argument("--block-from", type=int, default=None, help="with --block-e: block = {b..n-1}")
    ap.add_argument("--block-e", type=int, default=None, help="exact number of edges inside the block")
    ap.add_argument("--mtf", action="store_true", help="maximal triangle-free: non-adjacent pairs have a common neighbour")
    ap.add_argument("-o", "--out", default="-")
    a = ap.parse_args()
    n, k = a.n, a.k
    E = Enc(n)
    V = range(n)
    for i, j, l in combinations(V, 3):
        E.clauses.append([-E.e(i, j), -E.e(i, l), -E.e(j, l)])
    if a.eager_is:
        for S in combinations(V, k):
            E.clauses.append([E.e(i, j) for i, j in combinations(S, 2)])
    dmax = a.dmax if a.dmax is not None else n - 1
    if a.dmin > 0 or dmax < n - 1:
        for v in V:
            E.counter([E.e(v, u) for u in V if u != v], a.dmin, dmax)
    m = n * (n - 1) // 2
    emax = a.emax if a.emax is not None else m
    if a.emin > 0 or emax < m:
        E.counter(list(range(1, m + 1)), a.emin, emax)
    if a.mtf:
        for i, j in combinations(V, 2):
            cl = [E.e(i, j)]
            for l in V:
                if l in (i, j):
                    continue
                c = E.new()
                E.clauses.append([-c, E.e(i, l)])
                E.clauses.append([-c, E.e(j, l)])
                cl.append(c)
            E.clauses.append(cl)
    if a.h_emax is not None or a.h_emin > 0:
        d = a.fix_nbhd
        hl = [E.e(i, j) for i in range(d + 1, n) for j in range(i + 1, n)]
        E.counter(hl, a.h_emin, a.h_emax if a.h_emax is not None else len(hl))
    if a.codeg_max is not None:
        for u, v in combinations(V, 2):
            cs = []
            for w in V:
                if w in (u, v):
                    continue
                c = E.new()
                E.clauses.append([-E.e(u, w), -E.e(v, w), c])
                cs.append(c)
            E.atmost(cs, a.codeg_max)
    if a.fix_nbhd is not None:
        d = a.fix_nbhd
        for u in range(1, n):
            E.clauses.append([E.e(0, u)] if u <= d else [-E.e(0, u)])
    for spec, sign in ((a.edges, 1), (a.nonedges, -1)):
        for t in filter(None, spec.split(",")):
            i, j = map(int, t.split("-"))
            E.clauses.append([sign * E.e(i, j)])
    if a.block_e is not None:
        b = a.block_from
        bl = [E.e(i, j) for i in range(b, n) for j in range(i + 1, n)]
        E.counter(bl, a.block_e, a.block_e)
    if a.codeg_pair is not None:
        d, c, w = a.fix_nbhd, a.codeg_pair, a.fix_nbhd + 1
        for i in range(1, d + 1):
            E.clauses.append([E.e(w, i)] if i <= c else [-E.e(w, i)])
    f = sys.stdout if a.out == "-" else open(a.out, "w")
    f.write(f"p cnf {E.nvars} {len(E.clauses)}\n")
    for c in E.clauses:
        f.write(" ".join(map(str, c)) + " 0\n")
    if f is not sys.stdout:
        f.close()


if __name__ == "__main__":
    main()
