#!/usr/bin/env python3
"""cert/card_demo.py - certified degree bounds lo <= deg(v) <= hi (critic X5).

Written by agent `cert`. Proof 2 of the two-stage chain (notes/cert_design.md sec. 3.7):
input  = F (TRI [+ all IS]) + D_PB  (D_PB: for every v, sum_u x(u,v) >= lo and <= hi;
         implied constraints, justified by a Lean lemma, NOT by VeriPB)
proof  = card.derive per vertex (satcore's exact totalizer clauses and aux numbering)
output = input + totalizer CNF, EQUISATISFIABLE (VeriPB + CakePB)
then   F_cnf = TRI + IS + totalizer CNF: check_cnf (--extra = totalizer CNF),
       CaDiCaL LRAT + cake_lpr (UNSAT case) or a model (SAT case, positive control).
Usage: card_demo.py N S LO HI OUTDIR
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import card  # noqa: E402
import codish  # noqa: E402
import sb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "..", "tools", "bin")


def main():
    n, s, lo, hi, D = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    os.makedirs(D, exist_ok=True)
    sys.path.insert(0, HERE)
    from satcore_cert import implied
    if not implied(n, s, "all", "degree", lo, hi):
        print("RESULT: FAIL (bound %d..%d not implied by cert/implied_bounds.txt)" % (lo, hi))
        sys.exit(1)
    os.chdir(D)
    nedge = n * (n - 1) // 2
    gen = subprocess.run([sys.executable, os.path.join(HERE, "gen.py"), "full", str(n), str(s)],
                         capture_output=True, text=True).stdout
    F = [[int(t) for t in l.split()[:-1]] for l in gen.splitlines() if l and not l.startswith(("c", "p"))]
    maxvar = nedge
    P = codish.Proof("K")
    dpb, tot = [], []
    for v in range(n):
        lits = [sb.var(u, v) for u in range(n) if u != v]
        L = len(lits)
        dpb.append("@dlo%d %s >= %d" % (v, " ".join("1 x%d" % x for x in lits), lo))
        dpb.append("@dhi%d %s >= %d" % (v, " ".join("1 ~x%d" % x for x in lits), L - hi))
        root, cls, maxvar, lo2, hi2 = card.cardinality(lits, lo, hi, maxvar)
        keep = card.derive(P, root, lo2, hi2, "@dlo%d" % v, "@dhi%d" % v)
        assert len(keep) == len(cls)
        tot += cls
        kept = keep
        P.raw("core id %s ;" % " ".join(kept))
    inp = [sb.opb_clause(c) for c in F] + dpb
    with open("in.opb", "w") as f:
        f.write("* #variable= %d #constraint= %d\n" % (maxvar, len(inp)))
        f.writelines(c + " ;\n" for c in inp)
    with open("out.opb", "w") as f:
        out = inp + [sb.opb_clause(c) for c in tot]
        f.write("* #variable= %d #constraint= %d\n" % (maxvar, len(out)))
        f.writelines(c + " ;\n" for c in out)
    with open("card.pbp", "w") as f:
        f.write("pseudo-Boolean proof version 3.0\nf %d ;\n" % len(inp))
        f.write("\n".join(P.lines) + "\n")
        f.write("output EQUISATISFIABLE FILE ;\nconclusion NONE ;\nend pseudo-Boolean proof ;\n")
    ok = True
    r = subprocess.run([os.path.join(BIN, "veripb"), "-e", "card.elab.pbp", "in.opb", "card.pbp", "out.opb"],
                       capture_output=True, text=True)
    v = "s VERIFIED OUTPUT EQUISATISFIABLE" in r.stdout.splitlines()
    print("VeriPB:", v, [l for l in (r.stdout + r.stderr).splitlines() if "rror" in l or "Proofgoal" in l or "Caused" in l][:3])
    r = subprocess.run([os.path.join(BIN, "cake_pb"), "in.opb", "card.elab.pbp", "out.opb"], capture_output=True, text=True)
    c = "s VERIFIED OUTPUT EQUISATISFIABLE" in r.stdout.splitlines()
    print("CakePB:", c)
    ok &= v and c
    with open("tot.cnf", "w") as f:
        f.write("p cnf %d %d\n" % (maxvar, len(tot)))
        f.writelines(" ".join(map(str, cl)) + " 0\n" for cl in tot)
    with open("F_cnf.cnf", "w") as f:
        f.write("p cnf %d %d\n" % (maxvar, len(F) + len(tot)))
        f.writelines(" ".join(map(str, cl)) + " 0\n" for cl in F + tot)
    r = subprocess.run([sys.executable, os.path.join(HERE, "check_cnf.py"), "--n", str(n), "--s", str(s), "--extra",
                        "tot.cnf", "F_cnf.cnf"], capture_output=True, text=True)
    cc = "RESULT: OK (every clause is valid or listed as extra)" in r.stdout.splitlines()
    print("check_cnf:", cc)
    ok &= cc
    r = subprocess.run([os.path.join(BIN, "cadical"), "-q", "--lrat", "--binary=false", "F_cnf.cnf", "F_cnf.lrat"],
                       capture_output=True, text=True)
    if r.returncode == 20:
        r = subprocess.run([os.path.join(BIN, "cake_lpr"), "F_cnf.cnf", "F_cnf.lrat"], capture_output=True, text=True)
        u = "s VERIFIED UNSAT" in r.stdout.splitlines()
        print("CaDiCaL UNSAT; cake_lpr:", u)
        ok &= u
    elif r.returncode == 10:
        m = {int(t) for l in r.stdout.splitlines() if l.startswith("v") for t in l.split()[1:]}
        degs = [sum(1 for u in range(n) if u != w and sb.var(u, w) in m) for w in range(n)]
        print("CaDiCaL SAT (positive control): degrees %d..%d" % (min(degs), max(degs)))
        ok &= lo <= min(degs) and max(degs) <= hi
    print("RESULT:", "OK" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
