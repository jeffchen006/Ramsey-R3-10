#!/usr/bin/env python3
"""cert/sms2veripb.py - certify an SMS run (sms agent's patched smsg) end to end.

Written by agent `cert`.
Inputs (from sms): OUT.cnf (input + external clauses, solver order), OUT.lrat,
SYM.json ({"sym_clauses": [[[[sign,i,j],...], perm], ...]}, rowmajor vars,
perm[v] = old vertex placed at new position v, so pi = perm^-1).
SMS order: canonical = lex-MIN of the row-wise edge vector (0 < 1), found
empirically on r3_5_14 (46/46 clauses valid; lex-max: 0/46).
Steps:
  1. SB list = JSON clauses with pi = perm^-1; check_sb.py (independent).
  2. VeriPB + CakePB: F_tri (rowmajor) -> F_tri + SB, and F_full -> F_full + SB.
  3. check_cnf.py --order rowmajor --extra sb.cnf OUT.cnf  (TRI / IS / SYM only).
  4. cake_lpr OUT.cnf OUT.lrat -> s VERIFIED UNSAT.
Usage: sms2veripb.py N S OUT.cnf OUT.lrat SYM.json WORKDIR
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "..", "tools", "bin")


def run(cmd, log):
    with open(log, "w") as f:
        subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    return open(log).read()


def main():
    n, s = int(sys.argv[1]), int(sys.argv[2])
    cnf, lrat, symf, W = [os.path.abspath(x) for x in sys.argv[3:7]]
    os.makedirs(W, exist_ok=True)
    os.chdir(W)
    sb.VARORDER, sb.NVERT = "rowmajor", n
    nv = n * (n - 1) // 2
    data = json.load(open(symf))["sym_clauses"]
    sbl = {}
    for lits, perm in data:
        cl = tuple(sorted(sg * sb.var(i, j) for sg, i, j in lits))
        pi = [0] * n
        for v, w in enumerate(perm):
            pi[w] = v
        sbl.setdefault(cl, pi)
    sbl = sorted(sbl.items())
    with open("sb.wit", "w") as f:
        for c, pi in sbl:
            f.write("%s 0 | %s\n" % (" ".join(map(str, c)), " ".join(map(str, pi))))
    with open("sb.cnf", "w") as f:
        f.write("p cnf %d %d\n" % (nv, len(sbl)))
        for c, _ in sbl:
            f.write(" ".join(map(str, c)) + " 0\n")
    fails = []

    def need(name, text, line):
        """cake_lpr / cake_pb exit 0 on failure: decide only by the stdout line."""
        if line not in text.splitlines():
            fails.append(name)

    out = run([sys.executable, os.path.join(HERE, "check_sb.py"), "--n", str(n), "--order", "rowmajor", "--better", "min", "--allow-empty", "sb.wit"], "check_sb.log")
    need("check_sb", out, "RESULT: OK")
    print("check_sb:", out.strip().splitlines()[-2:])
    for tag in ("tri", "full"):
        r = subprocess.run([sys.executable, os.path.join(HERE, "gen.py"), tag, str(n), str(s), "--rowmajor"],
                           capture_output=True, text=True).stdout
        open("F_%s.cnf" % tag, "w").write(r)
        base = [l for l in r.splitlines() if l and not l.startswith(("c", "p"))]
        ncl = sb.cnf_to_opb("F_%s.cnf" % tag, "in_%s.opb" % tag)
        with open("out_%s.cnf" % tag, "w") as f:
            f.write("p cnf %d %d\n" % (nv, len(base) + len(sbl)))
            f.write("\n".join(base) + "\n")
            for c, _ in sbl:
                f.write(" ".join(map(str, c)) + " 0\n")
        sb.cnf_to_opb("out_%s.cnf" % tag, "out_%s.opb" % tag)
        sb.write_veripb("sb_%s.pbp" % tag, n, ncl, [(list(c), pi) for c, pi in sbl], better="min")
        a = run([os.path.join(BIN, "veripb"), "-e", "sb_%s.elab.pbp" % tag, "in_%s.opb" % tag,
                 "sb_%s.pbp" % tag, "out_%s.opb" % tag], "veripb_%s.log" % tag)
        b = run([os.path.join(BIN, "cake_pb"), "in_%s.opb" % tag, "sb_%s.elab.pbp" % tag, "out_%s.opb" % tag],
                "cakepb_%s.log" % tag)
        need("veripb_" + tag, a, "s VERIFIED OUTPUT EQUISATISFIABLE")
        need("check_pbp_" + tag, run([sys.executable, os.path.join(HERE, "check_pbp.py"), "--n", str(n), "--order",
                                      "rowmajor", "--input-constraints", str(ncl), "sb_%s.pbp" % tag],
                                     "check_pbp_%s.log" % tag), "RESULT: OK (M-IS conditions W, D, I, R hold)")
        need("check_in_" + tag, run([sys.executable, os.path.join(HERE, "check_cnf.py"), "--n", str(n), "--s", str(s),
                                     "--order", "rowmajor", "--opb", "--require-all-tri", "in_%s.opb" % tag],
                                    "check_in_%s.log" % tag), "RESULT: OK (every clause is valid or listed as extra)")
        need("cakepb_" + tag, b, "s VERIFIED OUTPUT EQUISATISFIABLE")
        print("%s: VeriPB %s, CakePB %s" % (tag, "OUTPUT EQUISATISFIABLE" in a and "s VERIFIED" in a,
                                            "s VERIFIED OUTPUT EQUISATISFIABLE" in b))
    out = run([sys.executable, os.path.join(HERE, "check_cnf.py"), "--n", str(n), "--s", str(s), "--order",
               "rowmajor", "--extra", "sb.cnf", cnf], "check_cnf.log")
    need("check_cnf", out, "RESULT: OK (every clause is valid or listed as extra)")
    print("check_cnf:", " | ".join(out.strip().splitlines()[2:]))
    out = run([os.path.join(BIN, "cake_lpr"), "--CML_HEAP_SIZE=10000", "--CML_STACK_SIZE=2000", cnf, lrat], "cake_lpr.log")
    need("cake_lpr", out, "s VERIFIED UNSAT")
    print("cake_lpr:", out.strip())
    if fails:
        print("RESULT: FAIL", fails)
        sys.exit(1)
    print("RESULT: OK (all checks passed; verdicts read from stdout, not exit codes)")


if __name__ == "__main__":
    main()
