#!/usr/bin/env python3
"""cert/mtf.py - VeriPB derivation of "G is maximal triangle-free" (MTF).

Written by agent `cert`. Design: notes/cert_design.md sec. 3.2.
Aux variable c(i,j,l) <-> x(i,l) and x(j,l)  (l is a common neighbour of i,j),
for i<j, l not in {i,j}; DIMACS id = nedge + 1 + pair_index(i,j)*(n-2) + rank(l).
Per pair (i,j), in order:
  red  ~c + x(i,l) >= 1            : c -> 0     (fresh c)
  red  ~c + x(j,l) >= 1            : c -> 0
  red  c + ~x(i,l) + ~x(j,l) >= 1  : c -> 1
  ... for all l, then
  red  x(i,j) + sum_l c(i,j,l) >= 1 : x(i,j) -> 1, c(a,b,m) -> other edge literal
       for every existing c whose definition contains x(i,j).
No order is loaded during these steps. Valid because adding a non-edge with no
common neighbour keeps the graph triangle-free and cannot create an independent set.
"""
import sb


def pairs(n):
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


class MTF:
    def __init__(self, n):
        self.n = n
        self.nedge = n * (n - 1) // 2
        self.pidx = {p: k for k, p in enumerate(pairs(n))}

    def c(self, i, j, l):
        if i > j:
            i, j = j, i
        rank = l - (l > i) - (l > j)
        return self.nedge + 1 + self.pidx[(i, j)] * (self.n - 2) + rank

    @property
    def nvars(self):
        return self.nedge + self.nedge * (self.n - 2)

    def clauses(self):
        """All clauses the proof adds, in proof order (DIMACS literals)."""
        out = []
        n = self.n
        for i, j in pairs(n):
            for l in range(n):
                if l in (i, j):
                    continue
                c = self.c(i, j, l)
                out.append([-c, sb.var(i, l)])
                out.append([-c, sb.var(j, l)])
                out.append([c, -sb.var(i, l), -sb.var(j, l)])
            out.append([sb.var(i, j)] + [self.c(i, j, l) for l in range(n) if l not in (i, j)])
        return out

    def proof_lines(self):
        n = self.n
        lines = []
        done = []  # pairs whose aux vars exist
        for i, j in pairs(n):
            for l in range(n):
                if l in (i, j):
                    continue
                c = self.c(i, j, l)
                lines.append("red %s : x%d -> 0 ;" % (sb.opb_clause([-c, sb.var(i, l)]), c))
                lines.append("red %s : x%d -> 0 ;" % (sb.opb_clause([-c, sb.var(j, l)]), c))
                lines.append("red %s : x%d -> 1 ;" % (sb.opb_clause([c, -sb.var(i, l), -sb.var(j, l)]), c))
            done.append((i, j))
            w = ["x%d -> 1" % sb.var(i, j)]
            for a, b in done:
                for m in range(n):
                    if m in (a, b):
                        continue
                    # c(a,b,m) <-> x(a,m) & x(b,m); contains x(i,j) iff {a,m} or {b,m} = {i,j}
                    if {a, m} == {i, j}:
                        w.append("x%d -> x%d" % (self.c(a, b, m), sb.var(b, m)))
                    elif {b, m} == {i, j}:
                        w.append("x%d -> x%d" % (self.c(a, b, m), sb.var(a, m)))
            cl = [sb.var(i, j)] + [self.c(i, j, l) for l in range(n) if l not in (i, j)]
            lines.append("red %s : %s ;" % (sb.opb_clause(cl), " ".join(w)))
        return lines

    def aux_witness(self, pi):
        """Rename aux vars with the vertex permutation (same convention as sb.witness)."""
        n = self.n
        pinv = [0] * n
        for v, w in enumerate(pi):
            pinv[w] = v
        parts = []
        for i, j in pairs(n):
            for l in range(n):
                if l in (i, j):
                    continue
                a, b, m = pinv[i], pinv[j], pinv[l]
                if (a, b, m) != (i, j, l) and not ({a, b} == {i, j} and m == l):
                    parts.append("x%d -> x%d" % (self.c(i, j, l), self.c(a, b, m)))
        return " ".join(parts)
