#!/usr/bin/env python3
"""Certificate tool for UNSAT results of satcore runs on orbit variables. No code shared with
orbsat.py / cyclic.py.

  verify_sc.py lex   SPEC.json OUT.cnf        write lex-leader clauses (own encoding) for satcore --extra
  verify_sc.py check SPEC.json MAP PREFIX N K P F
                                             check a satcore --proof PREFIX run for the case
                                             "n = N, alpha < K, automorphism of prime order P
                                             with exactly F fixed points"

SPEC.json: {"n", "K", "generators": [perm...], "breakers": [perm...]}.
check:
  1. orbit variables: own union-find over vertex pairs under the generators, numbered by least
     pair; MAP (lines "i j v") must agree pair by pair;
  2. every clause of PREFIX.full.cnf must be one of
       (a) a triangle clause {-v(ab), -v(ac), -v(bc)} for a vertex triple a<b<c,
       (b) a clause of the own lex-leader encoding for the breakers (each breaker checked to map
           pair-orbits onto pair-orbits, i.e. to normalize H),
       (c) an all-positive clause C with an explicit K-set S (from PREFIX.ext.sets, or found by
           search) such that every pair of S has its variable in C ("S is not independent");
     so every clause is valid for all (3,K)-graphs invariant under H, or is a lex-leader clause;
  3. drat-trim PREFIX.full.cnf PREFIX.drat must print "s VERIFIED".
If all pass: no (3,K,n)-graph G with H <= Aut(G).
"""
import itertools
import json
import subprocess
import sys

DRAT = "./tools/bin/drat-trim"


def need(cond, msg="check failed"):
    """Explicit check (not assert: must also run under python3 -O)."""
    if not cond:
        print("RESULT: NOT VERIFIED (" + msg + ")")
        sys.exit(1)


def orbit_vars(n, gens):
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
        need(sorted(g) == list(range(n)))
        for p in pairs:
            ra, rb = find(p), find(img(g, p))
            if ra != rb:
                parent[max(ra, rb)] = min(ra, rb)
    roots = sorted({find(p) for p in pairs})
    var = {r: i + 1 for i, r in enumerate(roots)}
    return {p: var[find(p)] for p in pairs}, len(roots), img


def lex_clauses(n, V, nv, img, breakers):
    clauses = []
    top = nv
    for pi in breakers:
        need(sorted(pi) == list(range(n)))
        m = {}
        for p, x in V.items():
            y = V[img(pi, p)]
            need(m.setdefault(x, y) == y, "breaker does not normalize H")
        eq = None
        for x in range(1, nv + 1):
            y = m[x]
            if x == y:
                continue
            pre = [] if eq is None else [-eq]
            clauses.append(tuple(pre + [-x, y]))
            top += 1
            e = top
            if eq is not None:
                clauses.append((-e, eq))
            clauses.append((-e, -x, y))
            clauses.append((-e, x, -y))
            clauses.append(tuple(pre + [x, y, e]))
            clauses.append(tuple(pre + [-x, -y, e]))
            eq = e
    return clauses, top


def subcase_clauses(n, V, spec, top):
    """Own encoding of the 'amax' subcase (see notes/symsat.md F9): orbit 0 = vertices 0..p-1 is
    independent, its fixed neighbours are exactly A, every other orbit has <= amax fixed
    neighbours (sequential counter, written here independently of cyclic.py)."""
    p, amax, A, B = spec["p"], spec["amax"], spec["A"], spec["B"]
    k = (n - spec["f"]) // p
    need(sorted(A + B) == list(range(k * p, n)) and len(A) == amax, "A, B not a split of F")
    cls = []
    W = lambda i, j: V[(min(i, j), max(i, j))]
    for j in range(1, p):
        cls.append((-W(0, j),))
    for t in A:
        cls.append((W(0, t),))
    for t in B:
        cls.append((-W(0, t),))
    for i in range(1, k):
        xs = [W(i * p, t) for t in A + B]
        # s[j][c] <-> "at least c+1 of xs[0..j] true", c < amax; forbid amax+1
        s_ = [[0] * amax for _ in xs]
        for j in range(len(xs)):
            for c in range(amax):
                top += 1
                s_[j][c] = top
        for j, x in enumerate(xs):
            cls.append((-x, s_[j][0]))
            if j > 0:
                for c in range(amax):
                    cls.append((-s_[j - 1][c], s_[j][c]))
                for c in range(1, amax):
                    cls.append((-x, -s_[j - 1][c - 1], s_[j][c]))
                cls.append((-x, -s_[j - 1][amax - 1]))
    return cls, top


def check_breakers_keep_subcase(n, spec):
    p, A, B = spec["p"], set(spec["A"]), set(spec["B"])
    O0 = set(range(p))
    for pi in spec["breakers"]:
        need({pi[v] for v in O0} == O0, "breaker moves orbit 0")
        need({pi[v] for v in A} == A and {pi[v] for v in B} == B, "breaker does not keep A, B")


def has_kset_inside(n, K, V, C):
    """Search a K-set all of whose pairs have variables in C (clique search)."""
    adj = [0] * n
    for (a, b), v in V.items():
        if v in C:
            adj[a] |= 1 << b
            adj[b] |= 1 << a

    def rec(P, c):
        if c >= K:
            return True
        if c + bin(P).count("1") < K:
            return False
        while P:
            v = P.bit_length() - 1
            P &= ~(1 << v)
            if rec(P & adj[v], c + 1):
                return True
            if c + bin(P).count("1") < K:
                return False
        return False

    return rec((1 << n) - 1, 0)


def main():
    cmd = sys.argv[1]
    spec = json.load(open(sys.argv[2]))
    n, K = spec["n"], spec["K"]
    V, nv, img = orbit_vars(n, spec["generators"])
    lex, top = lex_clauses(n, V, nv, img, spec["breakers"])
    if spec.get("amax") is not None:
        check_breakers_keep_subcase(n, spec)
        sub, top = subcase_clauses(n, V, spec, top)
        lex = lex + sub
    if cmd == "lex":
        with open(sys.argv[3], "w") as f:
            f.write(f"p cnf {top} {len(lex)}\n")
            for cl in lex:
                f.write(" ".join(map(str, cl)) + " 0\n")
        return
    need(cmd == "check")
    mapf, prefix = sys.argv[3], sys.argv[4]
    # the case being certified must be given explicitly and must match the generator
    cn, cK, cp, cf = map(int, sys.argv[5:9])
    need(n == cn and K == cK, "n or K differ from the claimed case")
    gens = spec["generators"]
    need(len(gens) == 1, "expected exactly one generator")
    g = gens[0]
    need(sorted(g) == list(range(n)), "generator is not a permutation")
    for v in range(n):  # every cycle has length 1 or cp
        L, w = 1, g[v]
        while w != v:
            w = g[w]; L += 1
        need(L in (1, cp), f"cycle of length {L} through vertex {v}")
    need(sum(g[v] == v for v in range(n)) == cf, "wrong number of fixed points")
    need(cp > 1 and all(cp % d for d in range(2, cp)), "p not prime")
    need(any(g[v] != v for v in range(n)), "identity generator")
    print(f"case: n={n} K={K} generator of order {cp} with {cf} fixed points"
          + (f", subcase amax={spec['amax']}" if spec.get("amax") is not None else ""))
    seen = 0
    for line in open(mapf):
        i, j, v = map(int, line.split())
        need(V[(min(i, j), max(i, j))] == v, f"map mismatch at pair {i},{j}")
        seen += 1
    need(seen == n * (n - 1) // 2)
    tri = set()
    for a, b, c in itertools.combinations(range(n), 3):
        tri.add(frozenset((-V[(a, b)], -V[(a, c)], -V[(b, c)])))
    lexset = set(frozenset(cl) for cl in lex)
    sets = []
    try:
        for line in open(prefix + ".ext.sets"):
            sets.append(list(map(int, line.split())))
    except FileNotFoundError:
        pass
    hinted = 0
    counts = dict(tri=0, lex=0, pos=0)
    hint_by_clause = {}
    for S in sets:
        if len(S) == K and len(set(S)) == K:
            hint_by_clause.setdefault(frozenset(V[(min(a, b), max(a, b))] for a, b in itertools.combinations(S, 2)), S)
    with open(prefix + ".full.cnf") as f:
        for line in f:
            if line.startswith("c") or line.startswith("p") or not line.strip():
                continue
            lits = list(map(int, line.split()))
            need(lits[-1] == 0)
            C = frozenset(lits[:-1])
            if C in tri:
                counts["tri"] += 1
            elif C in lexset:
                counts["lex"] += 1
            elif all(l > 0 and l <= nv for l in C):
                # a logged K-set whose pair-variables are exactly C, else search one inside C
                if C in hint_by_clause:
                    hinted += 1
                    ok = True
                else:
                    ok = has_kset_inside(n, K, V, C)
                need(ok, f"positive clause without a K-set: {sorted(C)}")
                counts["pos"] += 1
            else:
                raise AssertionError(f"unexplained clause: {lits}")
    print("clauses:", counts, "positive clauses matched to a logged set:", hinted)
    r = subprocess.run([DRAT, prefix + ".full.cnf", prefix + ".drat", "-t", "100000"], capture_output=True, text=True)
    ok = "s VERIFIED" in r.stdout
    print("drat-trim:", [l for l in r.stdout.split("\n") if l.startswith("s ")])
    print("RESULT:", "VERIFIED" if ok else "NOT VERIFIED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
