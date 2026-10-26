#!/usr/bin/env python3
"""cert/lazy.py - demo solver: lazy independent-set clauses + dynamic SB clauses.

Written by agent `cert` (demo only; the real search is satcore/sms).

Counterexample-guided loop on one cube:
  start   : all triangle clauses + static SB clauses + cube units
  repeat  : solve; if UNSAT stop.
            model G -> add clauses for up to K independent s-sets of G (lazy IS)
                    -> add lex clauses NOT(alpha) for transpositions pi with
                       pi(G) lex-better than G (dynamic SB, see sb.py)
            if neither exists, G is a (3,s,n)-graph: print it and stop (SAT).
Writes:
  <out>.cnf     final formula (sections marked by comment lines)
  <out>.is      the lazy IS clauses (DIMACS, for check_cnf)
  <out>.sbdyn   dynamic SB clauses, one per line: "<clause lits> 0 | <pi>"
Usage: lazy.py N S DEPTH "<cube lits>" OUT [K] [--mtf]
  --mtf adds the MTF clauses of cert/mtf.py (aux vars above the edge vars).
"""
import sys

from pysat.solvers import Cadical195

import mtf
import sb


def tri_clauses(n):
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                yield [-sb.var(i, j), -sb.var(i, k), -sb.var(j, k)]


def indep_sets(n, G, s, limit):
    """Up to `limit` independent s-sets of G (backtracking)."""
    adj = [set() for _ in range(n)]
    for i, j in G:
        adj[i].add(j)
        adj[j].add(i)
    out = []

    def ext(chosen, cand):
        if len(out) >= limit:
            return
        if len(chosen) == s:
            out.append(list(chosen))
            return
        for idx, v in enumerate(cand):
            if len(chosen) + len(cand) - idx < s:
                return
            ext(chosen + [v], [w for w in cand[idx + 1:] if w not in adj[v]])

    ext([], list(range(n)))
    return out


def main():
    use_mtf = "--mtf" in sys.argv
    sys.argv = [a for a in sys.argv if a != "--mtf"]
    n, s, depth = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    cube = [int(t) for t in sys.argv[4].split()]
    out = sys.argv[5]
    K = int(sys.argv[6]) if len(sys.argv) > 6 else 20
    nedge = n * (n - 1) // 2

    tri = list(tri_clauses(n))
    M = mtf.MTF(n)
    mtfc = M.clauses() if use_mtf else []
    nvars = M.nvars if use_mtf else nedge
    static = [c for c, _ in sb.static_clauses(n, depth)]
    lazy_is, dyn = [], []
    S = Cadical195()
    for c in tri + mtfc + static + [[u] for u in cube]:
        S.add_clause(c)
    it = 0
    status = "UNSAT"
    while S.solve():
        it += 1
        m = S.get_model()
        G = {(i, j) for i in range(n) for j in range(i + 1, n) if m[sb.var(i, j) - 1] > 0}
        new = 0
        for I in indep_sets(n, G, s, K):
            c = sorted(sb.var(a, b) for a in I for b in I if a < b)
            lazy_is.append(c)
            S.add_clause(c)
            new += 1
        for a in range(1, n):
            for b in range(a + 1, n):
                pi = list(range(n))
                pi[a], pi[b] = b, a
                c = sb.lex_clause(n, G, pi)
                if c is not None:
                    dyn.append((c, pi))
                    S.add_clause(c)
                    new += 1
        if new == 0:
            status = "SAT"
            print("SAT graph edges:", sorted(G))
            break
    print("cube [%s]: %s after %d iterations; lazy IS %d, dynamic SB %d"
          % (" ".join(map(str, cube)), status, it, len(lazy_is), len(dyn)))

    def dimacs(f, cls):
        for c in cls:
            f.write(" ".join(map(str, c)) + " 0\n")

    allc = len(tri) + len(mtfc) + len(static) + len(dyn) + len(lazy_is) + len(cube)
    with open(out + ".cnf", "w") as f:
        f.write("c cert lazy.py n=%d s=%d depth=%d cube=[%s]\n" % (n, s, depth, " ".join(map(str, cube))))
        f.write("p cnf %d %d\n" % (nvars, allc))
        f.write("c section triangles\n")
        dimacs(f, tri)
        f.write("c section mtf\n")
        dimacs(f, mtfc)
        f.write("c section static-sb\n")
        dimacs(f, static)
        f.write("c section dynamic-sb\n")
        dimacs(f, [c for c, _ in dyn])
        f.write("c section lazy-is\n")
        dimacs(f, lazy_is)
        f.write("c section cube-units\n")
        dimacs(f, [[u] for u in cube])
    with open(out + ".sbdyn", "w") as f:
        for c, pi in dyn:
            f.write("%s 0 | %s\n" % (" ".join(map(str, c)), " ".join(map(str, pi))))
    return 0 if status == "UNSAT" else 1


if __name__ == "__main__":
    sys.exit(main())
