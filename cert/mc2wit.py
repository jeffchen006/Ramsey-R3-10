#!/usr/bin/env python3
"""cert/mc2wit.py - MathCheckRamsey trusted clauses -> cert witness file.
Reads the 't' lines of a MathCheck DRAT proof and the .perm file (same order; perm
line = vertex list, extended by the missing vertices as check-perm.py does). MathCheck
check-perm.py places vertex v at position inv(perm)[v]; in cert's convention
(pi x)_p = x_{pi^-1 p}, so pi = inv(extended perm). Vertices are 0-based here.
Usage: mc2wit.py N PROOF.drat PROOF.perm OUT.wit"""
import sys
n = int(sys.argv[1])
ts = [l.split() for l in open(sys.argv[2]) if l.startswith("t ")]
ps = open(sys.argv[3]).read().splitlines()
assert len(ts) == len(ps), (len(ts), len(ps))
with open(sys.argv[4], "w") as f:
    for t, p in zip(ts, ps):
        assert "Complete solution" not in p
        perm = [int(x) for x in p.split()]
        perm += [v for v in range(n) if v not in perm]
        pi = [0] * n
        for v, w in enumerate(perm):
            pi[w] = v
        f.write("%s | %s\n" % (" ".join(t[1:]), " ".join(map(str, pi))))
print("wrote", len(ts), "clauses")
