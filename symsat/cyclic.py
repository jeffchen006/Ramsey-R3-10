#!/usr/bin/env python3
"""Search (3,K,n)-graphs with an automorphism sigma of prime order p with k orbits of size p
and f = n - k*p fixed points (orbit SAT + CEGAR, see orbsat.py).

Vertex labels: orbit i (0 <= i < k), position j: v = i*p + j; fixed points k*p .. n-1.
sigma: i*p + j -> i*p + (j+1 mod p); fixed points fixed.
Symmetry breaking (lex-leader, one constraint per generator of a subgroup of the
normalizer of <sigma>): rotate one orbit; swap adjacent orbits; multiplier j -> g*j
(g a primitive root mod p); swap adjacent fixed points.

Usage: cyclic.py p f [--K 10] [--n 40] [--dmin 4] [--nosb] [--cnf FILE] [--tl SEC]
Prints one JSON result line. A SAT graph is written as graph6 to --out (default stdout).
dmin default 4: a vertex of degree d <= 3 leaves 39-d >= 36 non-neighbours, a triangle-free
graph with alpha <= 8, impossible since R(3,9) = 36 (Grinstead-Roberts 1982). Only used for
propagation (it is implied by alpha <= 9).
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, "./tools")
from check_graph import to_graph6  # noqa: E402
from orbsat import Problem, alpha  # noqa: E402


def primroot(p):
    for g in range(2, p):
        if len({pow(g, e, p) for e in range(1, p)}) == p - 1:
            return g
    return 1


def build(p, f, n, full=False):
    assert (n - f) % p == 0
    k = (n - f) // p
    ident = list(range(n))
    sigma = ident[:]
    for i in range(k):
        for j in range(p):
            sigma[i * p + j] = i * p + (j + 1) % p
    breakers = []
    for i in range(k):  # rotate orbit i only
        r = ident[:]
        for j in range(p):
            r[i * p + j] = i * p + (j + 1) % p
        if p > 1 and k > 1:
            breakers.append(r)
    opairs = [(i, i2) for i in range(k) for i2 in range(i + 1, k)] if full else [(i, i + 1) for i in range(k - 1)]
    for i, i2 in opairs:  # swap orbits i, i2
        s = ident[:]
        for j in range(p):
            s[i * p + j], s[i2 * p + j] = i2 * p + j, i * p + j
        breakers.append(s)
    if p > 2:
        g = primroot(p)
        m = ident[:]
        for i in range(k):
            for j in range(p):
                m[i * p + j] = i * p + (g * j) % p
        breakers.append(m)
    fpairs = [(t, t2) for t in range(k * p, n) for t2 in range(t + 1, n)] if full else [(t, t + 1) for t in range(k * p, n - 1)]
    for t, t2 in fpairs:  # swap fixed points
        s = ident[:]
        s[t], s[t2] = t2, t
        breakers.append(s)
    return k, sigma, breakers


def build_amax(p, f, n, amax, full=True):
    """Case split by a = max |A_O| over orbits O (A_O = fixed neighbours of O; for f > 0, F3 and
    F6 give a >= 1 and every orbit with A_O nonempty is independent). WLOG (relabel orbits and fixed
    points, which commutes with sigma): O = orbit 0, A_O = first amax fixed points.
    Breakers keep orbit 0, A and F - A setwise: rotations of every orbit, the multiplier (p odd),
    transpositions of orbits 1..k-1, transpositions inside A and inside F - A."""
    k = (n - f) // p
    ident = list(range(n))
    sigma = ident[:]
    for i in range(k):
        for j in range(p):
            sigma[i * p + j] = i * p + (j + 1) % p
    breakers = []
    for i in range(k):
        r = ident[:]
        for j in range(p):
            r[i * p + j] = i * p + (j + 1) % p
        breakers.append(r)
    if p > 2:
        g = primroot(p)
        m = ident[:]
        for i in range(k):
            for j in range(p):
                m[i * p + j] = i * p + (g * j) % p
        breakers.append(m)
    for i in range(1, k):
        for i2 in (range(i + 1, k) if full else ([i + 1] if i + 1 < k else [])):
            s = ident[:]
            for j in range(p):
                s[i * p + j], s[i2 * p + j] = i2 * p + j, i * p + j
            breakers.append(s)
    A = list(range(k * p, k * p + amax))
    B = list(range(k * p + amax, n))
    for part in (A, B):
        for x in range(len(part)):
            for y in (range(x + 1, len(part)) if full else ([x + 1] if x + 1 < len(part) else [])):
                s = ident[:]
                s[part[x]], s[part[y]] = part[y], part[x]
                breakers.append(s)
    return k, sigma, breakers, A, B


def amax_clauses(V, p, k, A, B, amax, pool):
    """Clauses of the subcase (V(i,j) = orbit variable of pair {i,j})."""
    from pysat.card import CardEnc, EncType
    cls = []
    for j in range(1, p):                 # orbit 0 independent
        cls.append([-V(0, j)])
    for t in A:                            # A = N(orbit 0) cap F
        cls.append([V(0, t)])
    for t in B:
        cls.append([-V(0, t)])
    for i in range(1, k):                  # maximality: every other orbit has <= amax fixed neighbours
        enc = CardEnc.atmost(lits=[V(i * p, t) for t in A + B], bound=amax, vpool=pool,
                             encoding=EncType.seqcounter)
        cls.extend(enc.clauses)
    return cls


def run_orbsolve(P, a):
    import subprocess
    tag = f"{a.work}/n{a.n}K{a.K}p{a.p}f{a.f}s{a.seed}{'nosb' if a.nosb else 'sbfull' if a.sbfull else ''}{os.getpid()}"
    with open(tag + ".prob", "w") as fh:
        fh.write(f"{P.n} {P.K} {P.nv}\n")
        for i in range(P.n):
            fh.write(" ".join(str(0 if i == j else P.var[(min(i, j), max(i, j))]) for j in range(P.n)) + "\n")
        reps = [orb[0] for orb in P.vorbits]
        fh.write(f"{len(reps)} " + " ".join(map(str, reps)) + "\n")
    P.write_cnf(tag + ".cnf")
    cmd = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "orbsolve"), tag + ".prob", tag + ".cnf",
           "--sets", tag + ".sets", "--seed", str(a.seed + 1)] + a.osargs.split()
    if a.tl:
        cmd += ["--tl", str(a.tl)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    P.indep_sets = []
    for line in open(tag + ".sets"):
        m = 0
        for v in line.split():
            m |= 1 << int(v)
        P.indep_sets.append(m)
    P.n_indep = len(P.indep_sets)
    stats = [l for l in out.split("\n") if l.startswith("c time")]
    it = int(stats[0].split()[4]) if stats else -1
    if "s SATISFIABLE" in out:
        adj = [0] * P.n
        for e in out.split("\nv ")[1].split("\n")[0].split():
            i, j = map(int, e.split("-"))
            adj[i] |= 1 << j
            adj[j] |= 1 << i
        assert alpha(adj) < P.K
        return "SAT", adj, it
    if "s UNSATISFIABLE" in out:
        return "UNSAT", None, it
    return "TIMEOUT", None, it


def run_satcore(P, a, breakers):
    import subprocess
    tag = f"{a.work}/sc_n{a.n}K{a.K}p{a.p}f{a.f}c{a.cube}a{a.amax}s{a.seed}{os.getpid()}"
    with open(tag + ".map", "w") as fh:
        for (i, j), v in sorted(P.var.items()):
            fh.write(f"{i} {j} {v}\n")
    extra = []
    if a.cert:
        # certificate mode: extra CNF = lex-leader clauses from the independent checker only
        spec = dict(n=a.n, K=a.K, p=a.p, f=a.f, generators=P.gens, breakers=breakers)
        if a.amax is not None:
            spec.update(amax=a.amax, A=A_glob, B=B_glob)
        json.dump(spec, open(a.cert + ".spec.json", "w"))
        here = os.path.dirname(os.path.abspath(__file__))
        subprocess.run([sys.executable, os.path.join(here, "verify_sc.py"), "lex", a.cert + ".spec.json", tag + ".cnf"], check=True)
        extra = ["--proof", a.cert]
        import shutil
        shutil.copy(tag + ".map", a.cert + ".map")
    else:
        P.write_cnf(tag + ".cnf")
    cmd = ["./satcore/bin/satcore", "-n", str(a.n), "-k", str(a.K), "--pairmap", tag + ".map",
           "--extra", tag + ".cnf", "--out", tag + ".g6", "--seed", str(a.seed), "-q"] + extra + a.osargs.split()
    if a.tl:
        cmd += ["--time", str(int(a.tl))]
    if os.path.exists(tag + ".g6"):
        os.remove(tag + ".g6")
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = r.stdout + r.stderr
    P.satcore_out = out[-2000:]
    if os.path.exists(tag + ".g6") and open(tag + ".g6").read().strip():
        from check_graph import parse_graph6
        adj = parse_graph6(open(tag + ".g6").read().split()[0])
        assert alpha(adj) < P.K
        return "SAT", adj, -1
    if "UNSAT" in out:
        return "UNSAT", None, -1
    return "TIMEOUT", None, -1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("p", type=int)
    ap.add_argument("f", type=int)
    ap.add_argument("--K", type=int, default=10)
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--dmin", type=int, default=4)
    ap.add_argument("--nosb", action="store_true")
    ap.add_argument("--amax", type=int, help="subcase a = max |A_O| over orbits (see build_amax)")
    ap.add_argument("--cube", type=int, help="cube: exactly this many orbit variables true")
    ap.add_argument("--pair2", action="store_true", help="add non-adjacent pair neighbourhood bounds")
    ap.add_argument("--sbfull", action="store_true", help="lex-leader for all orbit / fixed-point transpositions")
    ap.add_argument("--cnf")
    ap.add_argument("--tl", type=float)
    ap.add_argument("--out")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--solver", default="cadical195")
    ap.add_argument("--engine", default="pysat", choices=["pysat", "orbsolve", "satcore"])
    ap.add_argument("--osargs", default="", help="extra orbsolve / satcore options")
    ap.add_argument("--work", default="/tmp", help="dir for orbsolve files")
    ap.add_argument("--cert", help="write certificate JSON (no cardinality clauses used)")
    a = ap.parse_args()
    if a.amax is not None:
        assert 1 <= a.amax <= a.f, "need 1 <= a <= f"
        k, sigma, breakers, A_, B_ = build_amax(a.p, a.f, a.n, a.amax, full=a.sbfull)
        global A_glob, B_glob
        A_glob, B_glob = A_, B_
    else:
        k, sigma, breakers = build(a.p, a.f, a.n, full=a.sbfull)
    if a.nosb:
        breakers = []
    t0 = time.time()
    P = Problem(a.n, a.K, [sigma], breakers=breakers, dmin=a.dmin, solver=a.solver, seed=a.seed, card=not a.cert, pair2=a.pair2, cube_nvars=a.cube,
                log=lambda s: print(s, file=sys.stderr, flush=True))
    if a.amax is not None:
        V = lambda i, j: P.var[(min(i, j), max(i, j))]
        for cl in amax_clauses(V, a.p, k, A_, B_, a.amax, P.pool):
            P.add(cl)
    if a.engine == "pysat":
        res, adj, it = P.solve(time_limit=a.tl)
    elif a.engine == "satcore":
        res, adj, it = run_satcore(P, a, breakers)
    else:
        res, adj, it = run_orbsolve(P, a)
    dt = time.time() - t0
    out = dict(n=a.n, K=a.K, p=a.p, k=k, f=a.f, dmin=a.dmin, sb=('none' if a.nosb else 'full' if a.sbfull else 'gens'), solver=a.solver if a.engine == 'pysat' else a.engine + ' ' + a.osargs,
               pair2=a.pair2, cube=a.cube, amax=a.amax, vars=P.nv, triangle_clauses=P.n_tri, sb_steps=P.n_sb, iters=it,
               indep_clauses=P.n_indep, result=res, time_s=round(dt, 2))
    if res == "SAT":
        g6 = to_graph6(adj)
        out["alpha"] = alpha(adj)
        out["graph6"] = g6
        if a.out:
            with open(a.out, "a") as fh:
                fh.write(g6 + "\n")
    if a.cert and res == "UNSAT" and a.engine != "satcore":
        with open(a.cert, "w") as fh:
            json.dump(dict(n=a.n, K=a.K, p=a.p, f=a.f, generators=[sigma], breakers=breakers,
                           indep_sets=[[i for i in range(a.n) if (m >> i) & 1] for m in P.indep_sets]), fh)
        out["cert"] = a.cert
    if a.cnf:
        P.write_cnf(a.cnf)
        out["cnf"] = a.cnf
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
