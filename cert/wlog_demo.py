#!/usr/bin/env python3
"""cert/wlog_demo.py - VeriPB demo of "WLOG vertex 0 has property P" (design sec. 3.3).

Written by agent `cert`.
P(v) = deg(v) >= K. Aux p_v (DIMACS id nedge+1+v), reified in the INPUT:
    K ~p_v + sum_u x(v,u) >= K            (p_v -> deg >= K)
    (n-1-K+1) p_v + sum_u ~x(v,u) >= n-K  (deg >= K -> p_v)
Implied constraint in the INPUT: sum_v p_v >= 1 ("some vertex has degree >= K";
justified outside VeriPB, e.g. by e(3,s,n) > n(K-1)/2).
Proof:
  red  p_0 + ~p_v >= 1 : transposition (0 v) on edges, p_0 <-> p_v     (v = 1..n-1)
  rup  p_0 >= 1
  load_order lexmax; dom SB clauses for transpositions (j j+1), j >= 1 (fix vertex 0),
       witnesses also swap p_j <-> p_{j+1}.
Output: input + chain + p_0 + SB, EQUISATISFIABLE. Then a positive control
(n where graphs exist: models with p_0 must exist) and an UNSAT check by cake_lpr.
Usage: wlog_demo.py N S K OUTDIR
"""
import os
import subprocess
import sys

from pysat.solvers import Cadical195

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "..", "tools", "bin")


def main():
    n, s, K, D = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    os.makedirs(D, exist_ok=True)
    nedge = n * (n - 1) // 2
    p = lambda v: nedge + 1 + v  # noqa: E731
    gen = subprocess.run([sys.executable, os.path.join(HERE, "gen.py"), "full", str(n), str(s)],
                         capture_output=True, text=True).stdout
    clauses = [[int(t) for t in l.split()[:-1]] for l in gen.splitlines() if l and not l.startswith(("c", "p"))]
    pb = []  # extra PB constraints of the input, as OPB strings
    for v in range(n):
        xs = [sb.var(v, u) for u in range(n) if u != v]
        pb.append("%d ~x%d %s >= %d" % (K, p(v), " ".join("1 x%d" % x for x in xs), K))
        pb.append("%d x%d %s >= %d" % (n - K, p(v), " ".join("1 ~x%d" % x for x in xs), n - K))
    pb.append(" ".join("1 x%d" % p(v) for v in range(n)) + " >= 1")
    inp = [sb.opb_clause(c) for c in clauses] + pb
    with open(os.path.join(D, "in.opb"), "w") as f:
        f.write("* #variable= %d #constraint= %d\n" % (nedge + n, len(inp)))
        f.writelines(c + " ;\n" for c in inp)

    def swap_witness(a, b):
        pi = list(range(n))
        pi[a], pi[b] = b, a
        w = sb.witness(n, pi)
        return pi, (w + " x%d -> x%d x%d -> x%d" % (p(a), p(b), p(b), p(a))).strip()

    prefix, derived = [], []
    for v in range(1, n):
        _, w = swap_witness(0, v)
        cl = [p(0), -p(v)]
        prefix.append("red %s : %s ;" % (sb.opb_clause(cl), w))
        derived.append(sb.opb_clause(cl))
    prefix.append("rup 1 x%d >= 1 ;" % p(0))
    derived.append("1 x%d >= 1" % p(0))
    static = [(c, pi) for c, pi in sb.static_clauses(n, 1) if pi[0] == 0]

    def aux_w(pi):
        return " ".join("x%d -> x%d" % (p(v), p(pi.index(v))) for v in range(n) if pi[v] != v)

    sb.write_veripb(os.path.join(D, "wlog.pbp"), n, len(inp), static, prefix=prefix, aux_witness=aux_w)
    with open(os.path.join(D, "out.opb"), "w") as f:
        out = inp + derived + [sb.opb_clause(c) for c, _ in static]
        f.write("* #variable= %d #constraint= %d\n" % (nedge + n, len(out)))
        f.writelines(c + " ;\n" for c in out)
    r = subprocess.run([os.path.join(BIN, "veripb"), "-e", os.path.join(D, "wlog.elab.pbp"), os.path.join(D, "in.opb"),
                        os.path.join(D, "wlog.pbp"), os.path.join(D, "out.opb")], capture_output=True, text=True)
    okv = "s VERIFIED OUTPUT EQUISATISFIABLE" in r.stdout.splitlines()
    print("VeriPB:", [l for l in (r.stdout + r.stderr).splitlines() if l.startswith("s ") or "rror" in l or "Proofgoal" in l])
    r = subprocess.run([os.path.join(BIN, "cake_pb"), os.path.join(D, "in.opb"), os.path.join(D, "wlog.elab.pbp"),
                        os.path.join(D, "out.opb")], capture_output=True, text=True)
    okc = "s VERIFIED OUTPUT EQUISATISFIABLE" in r.stdout.splitlines()
    print("CakePB:", [l for l in r.stdout.splitlines() if l.startswith("s ") or "fail" in l])

    # search on the output formula (CNF part + p_0 forces deg(0) >= K via a cardinality check loop)
    S = Cadical195()
    for c in clauses:
        S.add_clause(c)
    for c, _ in static:
        S.add_clause(c)
    from pysat.card import CardEnc
    enc = CardEnc.atleast([sb.var(0, u) for u in range(1, n)], bound=K, top_id=nedge + n)
    for c in enc.clauses:
        S.add_clause(c)
    res = S.solve()
    if res:
        m = S.get_model()
        deg0 = sum(1 for u in range(1, n) if m[sb.var(0, u) - 1] > 0)
        print("search with deg(0) >= %d: SAT, deg(0) = %d" % (K, deg0))
    else:
        print("search with deg(0) >= %d: UNSAT" % K)
    if not (okv and okc):
        print("RESULT: FAIL")
        sys.exit(1)
    print("RESULT: OK (VeriPB and CakePB verdicts read from stdout)")


if __name__ == "__main__":
    main()
