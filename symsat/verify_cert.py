#!/usr/bin/env python3
"""Independent re-check of an UNSAT result of cyclic.py / orbsat.py.

It shares no code with orbsat.py. From the certificate JSON (n, K, generators of H, breakers,
list of independent K-sets) it builds its own CNF:
  vars  = H-orbits on vertex pairs (union-find), numbered by their least pair (lex order);
  (1) for every vertex triple: not all three pair-orbits are edges;
  (2) for every listed K-set I (checked: K distinct vertices): some pair of I is an edge.
      Valid for every graph with alpha < K;
  (3) for every breaker pi (checked: pi maps pair-orbits onto pair-orbits, i.e. normalizes H):
      x <=lex pi(x), full equivalence encoding with prefix-equality auxiliaries.
Then it runs CaDiCaL with a DRAT proof and checks the proof with drat-trim.
If all checks pass: no (3,K,n)-graph G with H <= Aut(G) exists (the lex-leader part is sound
because constraints (1)+(alpha<K) are invariant under the normalizer of H).
Usage: verify_cert.py CERT.json WORKDIR
"""
import itertools
import json
import os
import subprocess
import sys

BIN = "./tools/bin"


def need(cond, msg="check failed"):
    """Explicit check (not assert: must also run under python3 -O)."""
    if not cond:
        print("RESULT: NOT VERIFIED (" + msg + ")")
        sys.exit(1)


def main():
    cert = json.load(open(sys.argv[1]))
    work = sys.argv[2]
    os.makedirs(work, exist_ok=True)
    n, K = cert["n"], cert["K"]
    gens = cert["generators"]
    for g in gens + cert["breakers"]:
        need(sorted(g) == list(range(n)))
    pairs = list(itertools.combinations(range(n), 2))
    parent = {p: p for p in pairs}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def img(g, p):
        a, b = g[p[0]], g[p[1]]
        return (min(a, b), max(a, b))

    for g in gens:
        for p in pairs:
            ra, rb = find(p), find(img(g, p))
            if ra != rb:
                parent[max(ra, rb)] = min(ra, rb)
    roots = sorted({find(p) for p in pairs})
    # number orbits by least pair; with union by min root, root == least pair
    for p in pairs:
        need(find(p) <= p)
    var = {r: i + 1 for i, r in enumerate(roots)}
    V = {p: var[find(p)] for p in pairs}
    nv = len(roots)
    clauses = set()
    for a, b, c in itertools.combinations(range(n), 3):
        clauses.add(tuple(sorted({-V[(a, b)], -V[(a, c)], -V[(b, c)]})))
    for I in cert["indep_sets"]:
        need(len(I) == K and len(set(I)) == K and all(0 <= v < n for v in I))
        clauses.add(tuple(sorted({V[(min(a, b), max(a, b))] for a, b in itertools.combinations(I, 2)})))
    top = nv
    for pi in cert["breakers"]:
        m = {}
        for p in pairs:
            x, y = V[p], V[img(pi, p)]
            need(m.setdefault(x, y) == y, "breaker does not normalize H")
        eq = None
        for x in range(1, nv + 1):
            y = m[x]
            if x == y:
                continue
            pre = [] if eq is None else [-eq]
            clauses.add(tuple(pre + [-x, y]))
            top += 1
            e = top
            # e <-> (eq and x == y)
            if eq is not None:
                clauses.add((-e, eq))
            clauses.add((-e, -x, y)); clauses.add((-e, x, -y))
            clauses.add(tuple(pre + [x, y, e])); clauses.add(tuple(pre + [-x, -y, e]))
            eq = e
    cnf = os.path.join(work, "check.cnf")
    with open(cnf, "w") as f:
        f.write(f"p cnf {top} {len(clauses)}\n")
        for cl in sorted(clauses):
            f.write(" ".join(map(str, cl)) + " 0\n")
    proof = os.path.join(work, "check.drat")
    r = subprocess.run([f"{BIN}/cadical", "-q", cnf, proof], capture_output=True, text=True)
    status = [l for l in r.stdout.split("\n") if l.startswith("s ")]
    print("vars", nv, "aux", top - nv, "clauses", len(clauses), "cadical:", status)
    if status != ["s UNSATISFIABLE"]:
        print("RESULT: NOT VERIFIED (CNF not UNSAT)")
        sys.exit(1)
    r = subprocess.run([f"{BIN}/drat-trim", cnf, proof, "-t", "100000"], capture_output=True, text=True)
    ok = "s VERIFIED" in r.stdout
    print("drat-trim:", [l for l in r.stdout.split("\n") if l.startswith("s ")])
    print("RESULT:", "VERIFIED" if ok else "NOT VERIFIED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
