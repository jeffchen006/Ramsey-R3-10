#!/usr/bin/env python3
"""cert/sms_card_cert.py - certify an sms run with degree / edge counters (Sinz), e.g. the
edge-minimum instances "no (3,s,n)-graph with <= E edges" (plan sec. 5.1 #2).

Written by agent `cert`. Claim certified: F_def + (sum of all edges <= EMAX) is UNSAT.
Inputs from sms: OUT.cnf (input + external clauses, solver order), OUT.lrat, SYM.json;
the input part was made by `sms/gen_ramsey.py -n N -k S --dmin A --dmax B --emin C --emax E`.
Steps:
  1. Regenerate the input part (TRI, per-vertex degree counters, edge counter; sms clause
     order and aux numbering) with cert's code; compare clause lists exactly.
  2. Degree bounds must be implied (implied_bounds.txt or deg <= S-1); EMIN must be 0;
     EMAX is the claim, stated on the command line.
  3. SYM clauses: check_sb (lex-min, row-major); VeriPB proof 1 (input TRI): one `dom` each;
     CakePB; check_pbp --perm-only. Valid for F_def + claim: IS_all and the claim constraint
     are closed under vertex permutations, and no witness adds an edge (M-IS with condition P,
     critic Review 18 Q1). The input CNF must have no MTF section (MTF adds edges).
  4. VeriPB proof 2: input TRI + SYM + degree bounds + claim (PB) -> all counter clauses
     (card.sinz_derive), output EQUISATISFIABLE; CakePB; check_pbp.
  5. check_cnf on OUT.cnf (TRI / IS / SYM / counter clauses); cake_lpr OUT.cnf OUT.lrat.
  --fix-nbhd D: split case of the claim (hand lemma: relabel a maximum-degree vertex as 0 and
     its neighbours as 1..D): N(0) = {1..D} as units (sms puts them last in the input) and
     DMAX must equal D (every degree <= D is part of the case, not an implied bound). The
     units are in the core of proof 1, so VeriPB checks that every SYM witness keeps 0, N(0)
     and the rest as blocks; the degree and edge constraints are closed under all vertex
     permutations (M-IS with condition P).
  --sb lean: SYM clauses checked by the Lean-verified sbcheck (all) + check_sb.py (all);
     VeriPB/CakePB proof 1 only on a random sample of 500. Valid by R310.Gen.lexleader_gen;
     for the F1 claim (DMAX >= S-1, no split) R310.Gen.edgeLowerBound_of_unsat gives Lean's
     F1 hypothesis directly. Default (--sb veripb): VeriPB + CakePB on all SYM clauses.
Usage: sms_card_cert.py N S DMIN DMAX EMIN EMAX OUT.cnf OUT.lrat SYM.json WORKDIR [--fix-nbhd D] [--sb lean]
"""
import json
import os
import subprocess
import sys
import time
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import card  # noqa: E402
import codish  # noqa: E402
import sb  # noqa: E402
from satcore_cert import implied  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "..", "tools", "bin")


def read_cnf(path):
    out, cur = [], []
    for line in open(path):
        if line.startswith(("c", "p")):
            continue
        for t in line.split():
            l = int(t)
            if l == 0:
                out.append(cur)
                cur = []
            else:
                cur.append(l)
    return out


def write(path, nv, cons):
    with open(path, "w") as f:
        f.write("* #variable= %d #constraint= %d\n" % (nv, len(cons)))
        f.writelines(c + " ;\n" for c in cons)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout + r.stderr


SBCHECK = os.path.join(HERE, "..", "lean", ".lake", "build", "bin", "sbcheck")
SAMPLE = 500


def main():
    sb_mode = "veripb"
    if "--sb" in sys.argv:
        i = sys.argv.index("--sb")
        sb_mode = sys.argv[i + 1]
        del sys.argv[i:i + 2]
    fixd = None
    if "--fix-nbhd" in sys.argv:
        i = sys.argv.index("--fix-nbhd")
        fixd = int(sys.argv[i + 1])
        del sys.argv[i:i + 2]
    n, s, dmin, dmax, emin, emax = [int(x) for x in sys.argv[1:7]]
    out_cnf, lrat, symf, W = [os.path.abspath(x) for x in sys.argv[7:11]]
    os.makedirs(W, exist_ok=True)
    os.chdir(W)
    sb.VARORDER, sb.NVERT = "rowmajor", n
    nedge = n * (n - 1) // 2
    fails = []

    tlast = [time.time()]

    def need(name, ok):
        now = time.time()
        print("%-34s %s  (%.1f s)" % (name, "OK" if ok else "FAIL", now - tlast[0]))
        tlast[0] = now
        if not ok:
            fails.append(name)

    # 1. regenerate the input part
    tri = [[-sb.var(i, j), -sb.var(i, l), -sb.var(j, l)] for i, j, l in combinations(range(n), 3)]
    maxv = nedge
    counters = []  # (lits, K, s, clauses, bound PB text)
    def counter(lits, lo, hi):
        nonlocal maxv
        for ls, K in ((lits, hi), ([-x for x in lits], len(lits) - lo) if lo > 0 else (None, None)):
            if ls is None:
                continue
            cls, svars, maxv = card.sinz(ls, K, maxv)
            if cls:
                counters.append((ls, K, svars, cls))
    if dmin > 0 or dmax < n - 1:
        for v in range(n):
            counter([sb.var(v, u) for u in range(n) if u != v], dmin, dmax)
    if emin > 0 or emax < nedge:
        counter(list(range(1, nedge + 1)), emin, emax)
    units = [] if fixd is None else [[sb.var(0, u)] if u <= fixd else [-sb.var(0, u)] for u in range(1, n)]
    base = tri + [c for *_, cls in counters for c in cls] + units
    F = read_cnf(out_cnf)
    need("input part regenerated (exact)", F[:len(base)] == base)
    if fixd is None:
        need("degree bounds implied", implied(n, s, "all", "degree", dmin, dmax))
    else:
        need("split case: dmin = 0, dmax = D <= s-1", dmin == 0 and dmax == fixd <= s - 1)
    need("no edge lower bound", emin == 0)

    # 3. SYM clauses, proof 1
    data = json.load(open(symf))["sym_clauses"]
    sym = {}
    for lits, perm in data:
        cl = tuple(sorted(sg * sb.var(i, j) for sg, i, j in lits))
        pi = [0] * n
        for v, w in enumerate(perm):
            pi[w] = v
        sym.setdefault(cl, pi)
    sym = sorted(sym.items())
    with open("sym.wit", "w") as f:
        f.writelines("%s 0 | %s\n" % (" ".join(map(str, c)), " ".join(map(str, pi))) for c, pi in sym)
    need("check_sb (lex-min, row-major)", "RESULT: OK" in run([sys.executable, os.path.join(HERE, "check_sb.py"),
         "--n", str(n), "--order", "rowmajor", "--better", "min", "--allow-empty", "sym.wit"]).splitlines())
    in1 = [sb.opb_clause(c) for c in tri + units]
    out1 = in1 + [sb.opb_clause(list(c)) for c, _ in sym]
    proof1_sym = sym
    if sb_mode == "lean":
        # Lean route (R310.Gen.lexleader_gen / edgeLowerBound_of_unsat): the Lean-verified
        # per-clause checker on ALL SYM clauses; VeriPB/CakePB only on a random sample.
        with open("sym_lean.wit", "w") as f:
            f.write("c order positions=rowmajor better=min vars=rowmajor d=%d n=%d s=%d\n" % (fixd or 0, n, s))
            f.writelines("%s 0 | %s\n" % (" ".join(map(str, c)), " ".join(map(str, pi))) for c, pi in sym)
        o = run([SBCHECK, "sym_lean.wit"])
        need("Lean sbcheck (all %d SYM)" % len(sym), "s VERIFIED %d clauses" % len(sym) in o.splitlines()
             or (len(sym) == 0))
        import random
        random.seed(1)
        proof1_sym = sorted(random.sample(sym, min(SAMPLE, len(sym))))
    out1s = in1 + [sb.opb_clause(list(c)) for c, _ in proof1_sym]
    write("in1.opb", maxv, in1)
    write("out1.opb", maxv, out1s)
    sb.write_veripb("p1.pbp", n, len(in1), [(list(c), pi) for c, pi in proof1_sym], better="min")
    o = run([os.path.join(BIN, "veripb"), "-e", "p1.elab.pbp", "in1.opb", "p1.pbp", "out1.opb"])
    tag1 = "" if sb_mode != "lean" else " sample %d" % len(proof1_sym)
    need("VeriPB proof 1 (SYM%s)" % tag1, "s VERIFIED OUTPUT EQUISATISFIABLE" in o.splitlines())
    o = run([os.path.join(BIN, "cake_pb"), "in1.opb", "p1.elab.pbp", "out1.opb"])
    need("CakePB proof 1%s" % tag1, "s VERIFIED OUTPUT EQUISATISFIABLE" in o.splitlines())
    # critic Q1: the claim "edges <= E" is closed only under pure vertex permutations
    need("check_pbp --perm-only proof 1", "RESULT: OK (M-IS conditions W, D, I, R, P hold)" in run([
        sys.executable, os.path.join(HERE, "check_pbp.py"), "--n", str(n), "--order", "rowmajor", "--perm-only",
        "--input-constraints", str(len(in1)), "p1.pbp"]).splitlines())
    with open("units.cnf", "w") as f:
        f.write("p cnf %d %d\n" % (nedge, len(units)))
        f.writelines("%d 0\n" % c[0] for c in units)
    need("proof 1 input = all TRI (+ N(0) units)", "RESULT: OK (every clause is valid or listed as extra)" in run([
        sys.executable, os.path.join(HERE, "check_cnf.py"), "--n", str(n), "--s", str(s), "--order", "rowmajor",
        "--opb", "--require-all-tri", "--extra", "units.cnf", "in1.opb"]).splitlines())

    # 4. proof 2: counters
    P = codish.Proof("Z")
    bounds, keep = [], []
    for t, (ls, K, svars, cls) in enumerate(counters):
        bounds.append("@b%d %s" % (t, card.pb([(1, -l) for l in ls], len(ls) - K)))
        kp = card.sinz_derive(P, ls, K, svars, "@b%d" % t)
        assert len(kp) == len(cls)
        keep += kp
    in2 = out1 + bounds
    out2 = in2 + [sb.opb_clause(c) for *_, cls in counters for c in cls]
    write("in2.opb", maxv, in2)
    write("out2.opb", maxv, out2)
    with open("p2.pbp", "w") as f:
        f.write("pseudo-Boolean proof version 3.0\nf %d ;\n" % len(in2))
        f.write("\n".join(P.lines) + "\n")
        if keep:
            f.write("core id %s ;\n" % " ".join(keep))
        f.write("output EQUISATISFIABLE FILE ;\nconclusion NONE ;\nend pseudo-Boolean proof ;\n")
    o = run([os.path.join(BIN, "veripb"), "-e", "p2.elab.pbp", "in2.opb", "p2.pbp", "out2.opb"])
    need("VeriPB proof 2 (counters)", "s VERIFIED OUTPUT EQUISATISFIABLE" in o.splitlines())
    o = run([os.path.join(BIN, "cake_pb"), "in2.opb", "p2.elab.pbp", "out2.opb"])
    need("CakePB proof 2", "s VERIFIED OUTPUT EQUISATISFIABLE" in o.splitlines())
    need("check_pbp proof 2", "RESULT: OK (M-IS conditions W, D, I, R hold)" in run([sys.executable, os.path.join(
        HERE, "check_pbp.py"), "--n", str(n), "--order", "rowmajor", "--input-constraints", str(len(in2)), "p2.pbp"]).splitlines())

    # 5. clause check + LRAT
    with open("extra.cnf", "w") as f:
        ex = [list(c) for c, _ in sym] + [c for *_, cls in counters for c in cls] + units
        f.write("p cnf %d %d\n" % (maxv, len(ex)))
        f.writelines(" ".join(map(str, c)) + " 0\n" for c in ex)
    o = run([sys.executable, os.path.join(HERE, "check_cnf.py"), "--n", str(n), "--s", str(s), "--order", "rowmajor",
             "--extra", "extra.cnf", out_cnf])
    need("check_cnf OUT.cnf", "RESULT: OK (every clause is valid or listed as extra)" in o.splitlines())
    print("  " + " | ".join(l.strip() for l in o.splitlines()[2:-1]))
    o = run([os.path.join(BIN, "cake_lpr"), "--CML_HEAP_SIZE=10000", "--CML_STACK_SIZE=2000", out_cnf, lrat])
    need("cake_lpr OUT.cnf OUT.lrat", "s VERIFIED UNSAT" in o.splitlines())
    if fails:
        print("RESULT: FAIL", fails)
        sys.exit(1)
    if fixd is None:
        print("RESULT: OK: no (3,%d,%d)-graph with at most %d edges (deg %d..%d implied); certified" % (s, n, emax, dmin, dmax))
    else:
        print("RESULT: OK: case D=%d: no (3,%d,%d)-graph with at most %d edges, max degree %d at vertex 0, "
              "N(0)={1..%d}; certified" % (fixd, s, n, emax, fixd, fixd))


if __name__ == "__main__":
    main()
