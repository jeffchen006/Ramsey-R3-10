#!/usr/bin/env python3
"""cert/satcore_cert.py - certify a satcore run (--lex --mtf, lazy IS clauses).

Written by agent `cert`. Inputs from satcore (runs/satcore/proofs/):
  BASE = base.cnf (sections "c BEGIN <tag>" .. "c END"), FULL = base + ext, LRAT.
Steps:
  1. Regenerate every base section independently (gen.py / codish.py / mtf.py) and
     compare as clause multisets: triangles, "lex rows i >= i+1 aux=a..b", "mtf aux=a..b".
  2. VeriPB + CakePB: input TRI (and TRI + all IS for small n)
       -> MTF by `red` (full definitions), load lex-max order,
       -> satcore's lex clauses by codish.derive (dom + red + pol + rup),
     output TRI (+IS) + MTF + lex clauses, EQUISATISFIABLE.
  3. check_cnf on FULL with --extra (MTF + lex clauses of the VeriPB output).
  4. cake_lpr FULL LRAT -> s VERIFIED UNSAT.
  Card sections ("card degree vertex=v ...", "card edges ..."): second VeriPB proof,
  input = output of proof 1 + the bounds as PB constraints (implied constraints D,
  justified by Lean lemmas, sec. 1.1), output = + satcore's exact totalizer clauses.
  --resolve: if satcore's LRAT fails, re-solve FULL with plain CaDiCaL --lrat (the
  certificate is about the formula, any solver may produce the proof).
  --claim-edges-max E: the "card edges" section must be exactly hi = E (the claim);
  LRAT may be a .drat file (converted by drat-trim; cake_lpr checks the result).
Usage: satcore_cert.py N S BASE FULL LRAT|DRAT WORKDIR [--resolve] [--claim-edges-max E]
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import card  # noqa: E402
import codish  # noqa: E402
import mtf  # noqa: E402
import sb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "..", "tools", "bin")


def read_sections(path):
    secs, cur, tag, nv = [], [], None, None
    for line in open(path):
        if line.startswith("p cnf"):
            nv = int(line.split()[2])
        elif line.startswith("c BEGIN "):
            tag, cur = line[8:].strip(), []
        elif line.startswith("c END"):
            secs.append((tag, cur))
            tag = None
        elif not line.startswith("c") and line.strip():
            assert tag is not None, "clause outside a section"
            cur.append([int(t) for t in line.split()[:-1]])
    return nv, secs


def implied(n, s, mode, kind, lo, hi):
    """critic P2: a D bound from a solver tag is used as a proof-2 input only if the fixed
    table cert/implied_bounds.txt (bounds with a Lean / hand justification) implies it."""
    if kind == "degree" and lo <= 0 and (hi < 0 or hi >= s - 1):
        return True  # deg <= s-1: N(v) is independent (hand lemma, every n)
    for line in open(os.path.join(HERE, "implied_bounds.txt")):
        t = line.split()
        if not t or t[0].startswith("#"):
            continue
        if (int(t[0]), int(t[1]), t[2], t[3]) == (n, s, mode, kind):
            tlo, thi = int(t[4]), int(t[5])
            return (lo <= 0 or lo <= tlo) and (hi < 0 or hi >= thi)
    return lo <= 0 and hi < 0


def ms(cls):
    out = {}
    for c in cls:
        k = frozenset(c)
        out[k] = out.get(k, 0) + 1
    return out


def write_opb(path, nv, cls):
    with open(path, "w") as f:
        f.write("* #variable= %d #constraint= %d\n" % (nv, len(cls)))
        for c in cls:
            f.write(sb.opb_clause(c) + " ;\n")


def write_cnf(path, nv, cls):
    with open(path, "w") as f:
        f.write("p cnf %d %d\n" % (nv, len(cls)))
        for c in cls:
            f.write(" ".join(map(str, c)) + " 0\n")


def main():
    resolve = "--resolve" in sys.argv
    sys.argv = [a for a in sys.argv if a != "--resolve"]
    claim_emax = None  # --claim-edges-max E: the run proves "no graph with <= E edges"
    if "--claim-edges-max" in sys.argv:
        i = sys.argv.index("--claim-edges-max")
        claim_emax = int(sys.argv[i + 1])
        del sys.argv[i:i + 2]
    n, s = int(sys.argv[1]), int(sys.argv[2])
    base, full, lrat, W = [os.path.abspath(x) for x in sys.argv[3:7]]
    os.makedirs(W, exist_ok=True)
    os.chdir(W)
    nv, secs = read_sections(base)

    # 1. regenerate sections
    gen = lambda mode: [[int(t) for t in l.split()[:-1]] for l in subprocess.run(  # noqa: E731
        [sys.executable, os.path.join(HERE, "gen.py"), mode, str(n), str(s)], capture_output=True,
        text=True).stdout.splitlines() if l and not l.startswith(("c", "p"))]
    tri = gen("tri")
    lex_rows, M, lex_first = [], None, None
    cards = []  # (lits, lo, hi, first_aux, regenerated clauses)
    ok = True
    for tag, cls in secs:
        if tag == "triangles":
            good = ms(cls) == ms(tri)
        elif tag.startswith("lex rows"):
            m = re.match(r"lex rows (\d+) >= (\d+) aux=(\d+)\.\.(\d+)", tag)
            i, a = int(m.group(1)), int(m.group(3))
            lex_first = a if lex_first is None else lex_first
            mine, _, _ = codish.lex_rows(n, [(i, i + 2)], a - 1)
            good = ms(cls) == ms(mine)
            lex_rows.append(i)
        elif tag.startswith("mtf"):
            m = re.match(r"mtf aux=(\d+)\.\.(\d+) order: pairs colex, m ascending", tag)
            M = mtf.MTF(n, "colex", int(m.group(1)))
            good = ms(cls) == ms(M.satcore_clauses()) and M.nvars == int(m.group(2))
        elif tag.startswith("card "):
            m = re.match(r"card (degree vertex=(\d+)|edges) lo=(-?\d+) hi=(-?\d+) "
                         r"encoding=totalizer\(cap=(\d+)\) aux=(\d+)\.\.(\d+)$", tag)
            good = False
            if m:
                if m.group(2) is not None:
                    v = int(m.group(2))
                    lits = [sb.var(u, v) for u in range(n) if u != v]
                else:
                    lits = list(range(1, n * (n - 1) // 2 + 1))
                lo, hi, a = int(m.group(3)), int(m.group(4)), int(m.group(6))
                root, mine, last, lo2, hi2 = card.cardinality(lits, lo, hi, a - 1)
                good = ms(cls) == ms(mine) and last == int(m.group(7))
                kind = "degree" if m.group(2) is not None else "edges"
                if kind == "edges" and claim_emax is not None:
                    ok_d = lo <= 0 and hi == claim_emax  # the claim itself, not an implied bound
                else:
                    ok_d = implied(n, s, "mtf" if any(t.startswith("mtf") for t, _ in secs) else "all", kind, lo, hi)
                if not ok_d:
                    print("  bound %s lo=%d hi=%d is NOT implied by cert/implied_bounds.txt" % (kind, lo, hi))
                good = good and ok_d
                cards.append((lits, lo2, hi2, root, mine))
        else:
            good = False
        print("section %-40s %6d clauses: %s" % (tag[:40], len(cls), "regenerated OK" if good else "MISMATCH"))
        ok &= good
    if not ok:
        raise SystemExit("base.cnf does not match the independent regeneration")
    if claim_emax is not None and M is not None:
        # critic Q1: MTF adds edges, so "edges <= E" is not preserved; the run would prove
        # only "no MTF graph with <= E edges".
        raise SystemExit("--claim-edges-max with an MTF section: refused (claim not preserved by MTF)")

    # blocks of consecutive rows -> codish structure with satcore's aux numbering
    blocks, start = [], None
    for i in sorted(lex_rows):
        if start is None or i != prev + 1:
            if start is not None:
                blocks.append((start, prev + 2))
            start = i
        prev = i
    if start is not None:
        blocks.append((start, prev + 2))
    lexc, maxv, struct = codish.lex_rows(n, blocks, (lex_first or 1) - 1)

    fails = []

    def need(name, text, line):
        """cake_lpr / cake_pb exit 0 on failure: decide only by the stdout line."""
        if line not in text.splitlines():
            fails.append(name)

    # 2. VeriPB / CakePB
    mtf_full = M.clauses() if M else []
    variants = ["tri"] + (["full"] if n <= 18 else [])
    for tag in variants:
        inp = tri if tag == "tri" else tri + gen("full")[len(tri):]
        write_opb("in_%s.opb" % tag, nv, inp)
        write_opb("out_%s.opb" % tag, nv, inp + mtf_full + lexc)
        sb.write_veripb("hdr.pbp", n, len(inp), [], prefix=M.proof_lines() if M else ())
        hdr = open("hdr.pbp").read().splitlines()
        k = [t for t, l in enumerate(hdr) if l.startswith("load_order lexmax")][0]
        P = codish.Proof()
        keep = codish.derive(P, n, struct, aux_witness=M.aux_witness if M else None)
        assert len(keep) == len(lexc)
        with open("cert_%s.pbp" % tag, "w") as f:
            f.write("\n".join(hdr[:k + 1] + P.lines) + "\n")
            f.write("load_order ;\n")
            if keep:
                f.write("core id %s ;\n" % " ".join(keep))
            f.write("output EQUISATISFIABLE FILE ;\nconclusion NONE ;\nend pseudo-Boolean proof ;\n")
        r = subprocess.run([os.path.join(BIN, "veripb"), "-e", "cert_%s.elab.pbp" % tag, "in_%s.opb" % tag,
                            "cert_%s.pbp" % tag, "out_%s.opb" % tag], capture_output=True, text=True)
        need("veripb_" + tag, r.stdout, "s VERIFIED OUTPUT EQUISATISFIABLE")
        r2 = subprocess.run([sys.executable, os.path.join(HERE, "check_pbp.py"), "--n", str(n), "--input-constraints",
                             str(len(inp)), "cert_%s.pbp" % tag] + (["--perm-only"] if claim_emax is not None else []),
                            capture_output=True, text=True)
        need("check_pbp_" + tag, r2.stdout, "RESULT: OK (M-IS conditions W, D, I, R%s hold)"
             % (", P" if claim_emax is not None else ""))
        r2 = subprocess.run([sys.executable, os.path.join(HERE, "check_cnf.py"), "--n", str(n), "--s", str(s), "--opb",
                             "--require-all-tri", "in_%s.opb" % tag], capture_output=True, text=True)
        need("check_in_" + tag, r2.stdout, "RESULT: OK (every clause is valid or listed as extra)")
        v = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith("s ") or "rror" in l or "Proofgoal" in l]
        r = subprocess.run([os.path.join(BIN, "cake_pb"), "in_%s.opb" % tag, "cert_%s.elab.pbp" % tag,
                            "out_%s.opb" % tag], capture_output=True, text=True)
        need("cakepb_" + tag, r.stdout, "s VERIFIED OUTPUT EQUISATISFIABLE")
        c = [l for l in r.stdout.splitlines() if l.startswith("s ") or "fail" in l]
        print("VeriPB %s: %s | CakePB: %s" % (tag, v, c))

    # 2b. second VeriPB proof for cardinality sections
    cardc = [c for _, _, _, _, cls in cards for c in cls]
    if cards:
        base1 = tri + mtf_full + lexc  # output of proof 1 (tri variant)
        P = codish.Proof("K")
        dpb, keepall = [], []
        for t, (lits, lo, hi, root, cls) in enumerate(cards):
            L = len(lits)
            if lo > 0:
                dpb.append("@dlo%d %s >= %d" % (t, " ".join("1 x%d" % x for x in lits), lo))
            if hi >= 0:
                dpb.append("@dhi%d %s >= %d" % (t, " ".join("1 ~x%d" % x for x in lits), L - hi))
            keep = card.derive(P, root, lo, hi, "@dlo%d" % t, "@dhi%d" % t)
            assert len(keep) == len(cls)
            keepall += keep
        inp2 = [sb.opb_clause(c) for c in base1] + dpb
        for name, cons in (("in_card.opb", inp2), ("out_card.opb", inp2 + [sb.opb_clause(c) for c in cardc])):
            with open(name, "w") as f:
                f.write("* #variable= %d #constraint= %d\n" % (nv, len(cons)))
                f.writelines(c + " ;\n" for c in cons)
        with open("card.pbp", "w") as f:
            f.write("pseudo-Boolean proof version 3.0\nf %d ;\n" % len(inp2))
            f.write("\n".join(P.lines) + "\n")
            f.write("core id %s ;\n" % " ".join(keepall))
            f.write("output EQUISATISFIABLE FILE ;\nconclusion NONE ;\nend pseudo-Boolean proof ;\n")
        r = subprocess.run([os.path.join(BIN, "veripb"), "-e", "card.elab.pbp", "in_card.opb", "card.pbp",
                            "out_card.opb"], capture_output=True, text=True)
        need("veripb_card", r.stdout, "s VERIFIED OUTPUT EQUISATISFIABLE")
        r2 = subprocess.run([os.path.join(BIN, "cake_pb"), "in_card.opb", "card.elab.pbp", "out_card.opb"],
                            capture_output=True, text=True)
        need("cakepb_card", r2.stdout, "s VERIFIED OUTPUT EQUISATISFIABLE")
        r3 = subprocess.run([sys.executable, os.path.join(HERE, "check_pbp.py"), "--n", str(n), "--input-constraints",
                             str(len(inp2)), "card.pbp"], capture_output=True, text=True)
        need("check_pbp_card", r3.stdout, "RESULT: OK (M-IS conditions W, D, I, R hold)")
        print("card proof (%d sections, %d clauses): VeriPB %s, CakePB %s, check_pbp %s" % (
            len(cards), len(cardc), "VERIFIED" in r.stdout, "s VERIFIED OUTPUT EQUISATISFIABLE" in r2.stdout,
            "RESULT: OK" in r3.stdout))

    # 3. clause check of FULL
    write_cnf("extra_mtf_lex.cnf", nv, mtf_full + lexc + cardc)
    r = subprocess.run([sys.executable, os.path.join(HERE, "check_cnf.py"), "--n", str(n), "--s", str(s),
                        "--extra", "extra_mtf_lex.cnf", full], capture_output=True, text=True)
    need("check_cnf", r.stdout, "RESULT: OK (every clause is valid or listed as extra)")
    print("check_cnf:", " | ".join(r.stdout.strip().splitlines()[2:]))
    # 4. cake_lpr
    if lrat.endswith(".drat"):  # satcore DRAT route: drat-trim makes the LRAT, cake_lpr checks it
        subprocess.run([os.path.join(BIN, "drat-trim"), full, lrat, "-L", "dt.lrat"], capture_output=True, text=True)
        lrat = "dt.lrat"
    r = subprocess.run([os.path.join(BIN, "cake_lpr"), "--CML_HEAP_SIZE=10000", "--CML_STACK_SIZE=2000", full, lrat], capture_output=True, text=True)
    print("cake_lpr (satcore LRAT):", (r.stdout + r.stderr).strip()[:200])
    if "s VERIFIED UNSAT" not in r.stdout.splitlines() and resolve:
        subprocess.run([os.path.join(BIN, "cadical"), "-q", "--lrat", "--binary=false", full, "resolve.lrat"],
                       capture_output=True, text=True)
        r = subprocess.run([os.path.join(BIN, "cake_lpr"), "--CML_HEAP_SIZE=10000", "--CML_STACK_SIZE=2000", full, "resolve.lrat"], capture_output=True, text=True)
        print("cake_lpr (re-solved with CaDiCaL):", (r.stdout + r.stderr).strip()[:200])
    need("cake_lpr", r.stdout, "s VERIFIED UNSAT")
    if fails:
        print("RESULT: FAIL", fails)
        sys.exit(1)
    claim = "no (3,%d,%d)-graph%s" % (s, n, "" if claim_emax is None else " with at most %d edges" % claim_emax)
    print("RESULT: OK (all checks passed; verdicts read from stdout, not exit codes): %s" % claim)


if __name__ == "__main__":
    main()
