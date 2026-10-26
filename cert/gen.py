#!/usr/bin/env python3
"""cert/gen.py - independent CNF generator for Ramsey (3,s,n) graphs.

Written by agent `cert`. Shares no code with satcore or sms.

Edge variable for 0 <= i < j < n (1-based DIMACS id). Two orders:
  colex (default, same as satcore and graph6 bit order):
    var(i,j) = j*(j-1)/2 + i + 1
  rowmajor:
    var(i,j) = i*n - i*(i+1)/2 + (j - i)
A true edge variable means the edge is in G.

Clauses:
  triangle  : (-e_ij -e_ik -e_jk)  for every i<j<k
  indep set : (OR of e_ab over a<b in S)  for every s-subset S
A model is exactly a triangle-free graph on n vertices with alpha < s.

Usage (add --rowmajor anywhere to switch order):
  gen.py full N S            -> all triangle and all independent-set clauses
  gen.py tri  N S            -> triangle clauses only (for lazy runs)
  gen.py varmap N            -> lines "i j var"
"""
import itertools
import sys


ORDER = "colex"


def var(n, i, j):
    if i > j:
        i, j = j, i
    assert 0 <= i < j < n
    if ORDER == "colex":
        return j * (j - 1) // 2 + i + 1
    return i * n - i * (i + 1) // 2 + (j - i)


def triangle_clauses(n):
    for i, j, k in itertools.combinations(range(n), 3):
        yield (-var(n, i, j), -var(n, i, k), -var(n, j, k))


def indep_clauses(n, s):
    for S in itertools.combinations(range(n), s):
        yield tuple(var(n, a, b) for a, b in itertools.combinations(S, 2))


def write_cnf(out, n, clauses, comment):
    clauses = list(clauses)
    out.write("c %s\n" % comment)
    out.write("p cnf %d %d\n" % (n * (n - 1) // 2, len(clauses)))
    for c in clauses:
        out.write(" ".join(map(str, c)) + " 0\n")


def main(argv):
    global ORDER
    if "--rowmajor" in argv:
        ORDER = "rowmajor"
        argv = [a for a in argv if a != "--rowmajor"]
    mode = argv[1]
    n = int(argv[2])
    if mode == "varmap":
        for i, j in itertools.combinations(range(n), 2):
            print(i, j, var(n, i, j))
        return
    s = int(argv[3])
    if mode == "full":
        cl = itertools.chain(triangle_clauses(n), indep_clauses(n, s))
    elif mode == "tri":
        cl = triangle_clauses(n)
    else:
        raise SystemExit("unknown mode " + mode)
    write_cnf(sys.stdout, n, cl, "cert-gen R(3,%d) n=%d mode=%s order=%s" % (s, n, mode, ORDER))


if __name__ == "__main__":
    main(sys.argv)
