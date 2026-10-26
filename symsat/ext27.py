#!/usr/bin/env python3
"""F10 extension check for the order-2 subcase a = 7 at n = 40 (notes/symsat.md F10).

For each (3,8,27)-graph H and each conjugacy class of involutions s of Aut(H) with exactly
f - 7 fixed points, decide by SAT + CEGAR if H extends to a (3,10,40)-graph G with an
involution sigma (sigma|H = s) and an independent orbit O = {x, x'} with N(x) = A + {b1, b2},
N(x') = A + {b1', b2'}, A = 7 fixed vertices, sigma: x<->x', b1<->b1', b2<->b2'.
H = G - N[O]. Unknown: edges (A + B) x H and the 4 pairs between {b1,b2} and {b1',b2'},
as sigma-orbit variables. Constraints: triangle-free, degree <= 9, alpha <= 9 (lazy).
Symmetry breaking (sound, commutes with sigma): rows of A in lex order; (b1,b1') <-> (b2,b2').
Usage: ext27.py FILE.g6.gz F [--start i --step k] [--maxaut N]   (F = target f; F = 34: s = id)
Output: one JSON line per (graph, class); final line SUMMARY.
"""
import gzip
import itertools
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "./tools")
from check_graph import parse_graph6, to_graph6  # noqa: E402
from autcycles import generators, group_elements, order  # noqa: E402
from orbsat import indep_with  # noqa: E402
from pysat.card import CardEnc, EncType  # noqa: E402
from pysat.formula import IDPool  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

N, K = 40, 10
X, XP = 27, 28
A = list(range(29, 36))
B1, B1P, B2, B2P = 36, 37, 38, 39


def compose(g, h):          # (g o h)(i) = g[h[i]]
    return tuple(g[i] for i in h)


def inverse(g):
    r = [0] * len(g)
    for i, j in enumerate(g):
        r[j] = i
    return tuple(r)


def inv_classes(els, nfix):
    """conjugacy-class representatives of involutions with nfix fixed points"""
    n = len(next(iter(els)))
    invs = [g for g in els if order(g) == 2 and sum(g[i] == i for i in range(n)) == nfix]
    seen, reps = set(), []
    for s in invs:
        if s in seen:
            continue
        reps.append(s)
        for g in els:
            seen.add(compose(compose(g, s), inverse(g)))
    return reps


def solve_ext(hadj, s, maxit=200000, cert=False):
    sig = list(s) + [XP, X] + A + [B1P, B1, B2P, B2]
    assert all(sig[sig[i]] == i for i in range(N))
    pool = IDPool()
    lit = {}            # pair -> True / False / var

    def pr(u, v):
        return (u, v) if u < v else (v, u)
    H = range(27)
    for u, v in itertools.combinations(H, 2):
        lit[(u, v)] = bool((hadj[u] >> v) & 1)
    for u in range(27, N):
        for v in range(N):
            if v != u:
                lit.setdefault(pr(u, v), False)
    for a in A:
        lit[pr(X, a)] = lit[pr(XP, a)] = True
    lit[pr(X, B1)] = lit[pr(X, B2)] = lit[pr(XP, B1P)] = lit[pr(XP, B2P)] = True
    free = [pr(u, h) for u in A + [B1, B1P, B2, B2P] for h in H]
    free += [pr(B1, B1P), pr(B2, B2P), pr(B1, B2P), pr(B2, B1P)]
    for e in free:
        o = min(e, pr(sig[e[0]], sig[e[1]]))
        lit[e] = pool.id(o)
    tri, cls = [], []
    for t in itertools.combinations(range(N), 3):
        ls = [lit[pr(t[0], t[1])], lit[pr(t[0], t[2])], lit[pr(t[1], t[2])]]
        if any(x is False for x in ls):
            continue
        c = [-x for x in ls if x is not True]
        assert c, "triangle in fixed part"
        tri.append(c)
    for v in range(N):
        vs = [lit[pr(u, v)] for u in range(N) if u != v]
        fixed = sum(1 for x in vs if x is True)
        vv = [x for x in vs if x is not True and x is not False]
        if fixed + len(vv) > 9:
            assert fixed <= 9
            cls += CardEnc.atmost(lits=vv, bound=9 - fixed, vpool=pool,
                                  encoding=EncType.seqcounter).clauses
    # lex: row(A[i]) <=lex row(A[i+1]) over h = 0..26 (equal-prefix encoding)
    def lex_le(xs, ys):
        out, eq_prev = [], None
        for x, y in zip(xs, ys):
            # if prefix equal then x <= y
            base = [] if eq_prev is None else [-eq_prev]
            out.append(base + [-x, y])
            e = pool.id(("eq", id(xs), x, y, len(out)))
            # e -> prefix equal and x == y
            if eq_prev is not None:
                out.append([-e, eq_prev])
            out.append([-e, -x, y]); out.append([-e, x, -y])
            # (prefix equal and x == y) -> e
            out.append(base + [x, y, e]); out.append(base + [-x, -y, e])
            eq_prev = e
        return out
    rows = [[lit[pr(a, h)] for h in H] for a in A]
    for i in range(len(A) - 1):
        cls += lex_le(rows[i], rows[i + 1])
    rb1 = [lit[pr(B1, h)] for h in H]
    rb2 = [lit[pr(B2, h)] for h in H]
    cls += lex_le(rb1, rb2)
    def cegar(sol, sets, it0=0):
        it = it0
        while True:
            it += 1
            if it > maxit:
                return "LIMIT", it
            if not sol.solve():
                return "UNSAT", it
            m = set(x for x in sol.get_model() if x > 0)
            adj = [0] * N
            for (u, v), x in lit.items():
                if x is True or (x is not False and x in m):
                    adj[u] |= 1 << v; adj[v] |= 1 << u
            found = 0
            for seed in range(1, 9):
                I = indep_with(adj, K, seed=seed)
                if I is None:
                    break
                vs = [v for v in range(N) if (I >> v) & 1]
                c = [lit[pr(u, v)] for u, v in itertools.combinations(vs, 2)]
                assert not any(x is True for x in c)
                c = sorted(set(x for x in c if x is not False))
                assert c
                sol.add_clause(c); found += 1; sets.append(vs)
            if not found:
                return ("SAT", adj), it
    sets = []
    with Solver(name="cadical153", bootstrap_with=tri + cls) as sol:
        r, it = cegar(sol, sets)
    if r != "UNSAT" or not cert:
        return r, it, len(sets)
    # phase 2 (certificate): triangle + 10-set clauses only, CEGAR again until UNSAT
    with Solver(name="cadical153", bootstrap_with=tri) as sol:
        for vs in sets:
            sol.add_clause(sorted(set(lit[pr(u, v)] for u, v in itertools.combinations(vs, 2)) - {False}))
        r2, it = cegar(sol, sets, it)
    if r2 != "UNSAT":       # a SAT here is a real graph (and would mean a breaker is unsound)
        return r2, it, len(sets)
    uniq = sorted(set(tuple(v) for v in sets))
    return "UNSAT", it, uniq


def main():
    path, f = sys.argv[1], int(sys.argv[2])
    start = int(sys.argv[sys.argv.index("--start") + 1]) if "--start" in sys.argv else 0
    step = int(sys.argv[sys.argv.index("--step") + 1]) if "--step" in sys.argv else 1
    nfix = f - 7
    cdir = sys.argv[sys.argv.index("--cert") + 1] if "--cert" in sys.argv else None
    if cdir:
        os.makedirs(cdir, exist_ok=True)
    cnt = {"graphs": 0, "classes": 0, "UNSAT": 0, "SAT": 0, "LIMIT": 0}
    t0 = time.time()
    with gzip.open(path, "rt") as fh:
        for idx, line in enumerate(fh):
            if idx % step != start:
                continue
            line = line.strip()
            hadj = parse_graph6(line)
            assert len(hadj) == 27
            cnt["graphs"] += 1
            if nfix == 27:
                reps = [tuple(range(27))]
            else:
                gens, size = generators(hadj)
                if not gens:
                    continue
                els = group_elements(gens, 27, 10 ** 6)
                assert els is not None and (size is None or abs(len(els) - size) < 0.5)
                reps = inv_classes(els, nfix)
            if "--count" in sys.argv:
                if reps:
                    cnt["classes"] += len(reps); print(json.dumps({"idx": idx, "nclass": len(reps)}), flush=True)
                continue
            for s in reps:
                cnt["classes"] += 1
                t1 = time.time()
                r, it, nadd = solve_ext(hadj, s, cert=bool(cdir))
                res = r if isinstance(r, str) else r[0]
                if cdir and res == "UNSAT":
                    k = cnt["classes"]
                    with open(f"{cdir}/f{f}_{idx}_{k}.json", "w") as out:
                        json.dump({"g6": line, "f": f, "s": list(s), "sets": nadd}, out)
                    nadd = len(nadd)
                cnt[res] += 1
                rec = {"idx": idx, "f": f, "s": s, "result": res, "iters": it, "cl": nadd,
                       "t": round(time.time() - t1, 2)}
                if res == "SAT":
                    rec["adj"] = r[1]
                    with open("./runs/symsat/found40_candidates.g6", "a") as out:
                        out.write(to_graph6(r[1]) + "\n")
                if res != "UNSAT" or nfix != 27:
                    print(json.dumps(rec), flush=True)
    cnt["time"] = round(time.time() - t0, 1)
    print("SUMMARY", f, start, step, json.dumps(cnt), flush=True)


if __name__ == "__main__":
    main()
