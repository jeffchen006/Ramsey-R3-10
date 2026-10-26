#!/usr/bin/env python3
"""cert/base40_cert.py - certify an sms n = 40 cube BASE CNF against Lean's cube file.

Written by agent `cert`. Claim: every assignment that satisfies Lean's cube file
(lean/out/cube_X.opb: TRI + MTF full definitions + N(0) units + degree PB bounds + e(H_0) PB)
extends to one that satisfies the sms base CNF (sms/gen_ramsey.py: TRI + Sinz degree counters
+ one-direction MTF + [Sinz e(H_0) counter] + N(0) units), up to renaming of variables.
Steps:
  1. Regenerate the sms base with cert's code (gen_ramsey's clause order and aux allocation)
     and compare with the sms file: exact list equality.
  2. VeriPB proof, input = Lean's cube file (degree / e(H_0) lines get labels; constraints
     unchanged): sms MTF aux c' by `red` (full definition), bridge (-c c') by `rup`, sms MTF
     clause by `rup`; Sinz counters by card.sinz_derive from Lean's PB bounds. Output = input +
     all derived clauses, EQUISATISFIABLE. VeriPB + CakePB + check_pbp.
  3. Glue: the sms base, renamed (sms row-major edge id -> Lean colex id; sms aux a -> 30420 +
     a - 780), is a subset of the VeriPB output (clause sets).
Usage: base40_cert.py LEAN_CUBE.opb SMS_BASE.cnf WORKDIR --dmin A --dmax B --mtf --fix-nbhd D [--h-emax T]
"""
import argparse
import os
import subprocess
import sys
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import card  # noqa: E402
import codish  # noqa: E402
import sb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "..", "tools", "bin")
N = 40
LEAN_AUX_MAX = 781 + 780 * 38 - 1  # 30420


def rm(i, j):  # sms row-major edge id
    if i > j:
        i, j = j, i
    return i * N - i * (i + 1) // 2 + (j - i)


def cx(i, j):  # Lean / cert colex edge id
    if i > j:
        i, j = j, i
    return j * (j - 1) // 2 + i + 1


def lean_c(i, j, l):
    if i > j:
        i, j = j, i
    return 781 + (j * (j - 1) // 2 + i) * 38 + (l - (l > i) - (l > j))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lean")
    ap.add_argument("sms")
    ap.add_argument("work")
    ap.add_argument("--dmin", type=int, default=0)
    ap.add_argument("--dmax", type=int, default=N - 1)
    ap.add_argument("--mtf", action="store_true")
    ap.add_argument("--fix-nbhd", type=int, required=True)
    ap.add_argument("--h-emax", type=int, default=None)
    # case constraints of cases' Lemma Mc / Lemma R7 (notes/cases_local.md); NOT in Lean's cube
    # file: they enter as an extra input part (case.opb), justified by those lemmas
    ap.add_argument("--codeg-max", type=int, default=None)
    ap.add_argument("--edges", default="")
    ap.add_argument("--block-from", type=int, default=None)
    ap.add_argument("--block-e", type=int, default=None)
    ap.add_argument("--codeg-pair", type=int, default=None)
    a = ap.parse_args()
    lean, smsf = os.path.abspath(a.lean), os.path.abspath(a.sms)
    os.makedirs(a.work, exist_ok=True)
    os.chdir(a.work)
    fails = []

    def need(name, ok):
        print("%-44s %s" % (name, "OK" if ok else "FAIL"))
        if not ok:
            fails.append(name)

    # 1. regenerate sms base in sms ids, and the same structure in Lean ids
    V = range(N)
    gen_s, gen_l = [], []           # clauses in sms ids / in Lean ids
    nxt = [780]                     # sms aux counter (gen_ramsey E.new)

    def add(cs, cl):
        gen_s.append(cs)
        gen_l.append(cl)

    rm2cx = {rm(i, j): cx(i, j) for i, j in combinations(V, 2)}

    def lmap(l):  # sms literal -> Lean literal
        v = abs(l)
        w = rm2cx[v] if v <= 780 else LEAN_AUX_MAX + v - 780
        return w if l > 0 else -w

    for i, j, l in combinations(V, 3):
        add([-rm(i, j), -rm(i, l), -rm(j, l)], None)
    counters = []  # (lean lits, K, lean s, kind, v)

    def atmost(lits_s, K, kind, v):
        cls_s, s_s, top = card.sinz(lits_s, K, nxt[0])
        cls_l, s_l, _ = card.sinz([lmap(x) for x in lits_s], K, LEAN_AUX_MAX + nxt[0] - 780)
        nxt[0] = top
        for cs, cl in zip(cls_s, cls_l):
            add(cs, cl)
        counters.append(([lmap(x) for x in lits_s], K, s_l, kind, v))

    def counter(lits_s, lo, hi, tag, v):
        atmost(lits_s, hi, tag + "hi", v)
        if lo > 0:
            atmost([-x for x in lits_s], len(lits_s) - lo, tag + "lo", v)

    if a.dmin > 0 or a.dmax < N - 1:
        for v in V:
            counter([rm(v, u) for u in V if u != v], a.dmin, a.dmax, "deg", v)
    mtf = []  # (i, j, [(l, sms aux)])
    if a.mtf:
        for i, j in combinations(V, 2):
            cl = [rm(i, j)]
            row = []
            for l in V:
                if l in (i, j):
                    continue
                nxt[0] += 1
                c = nxt[0]
                add([-c, rm(i, l)], None)
                add([-c, rm(j, l)], None)
                cl.append(c)
                row.append((l, c))
            add(cl, None)
            mtf.append((i, j, row))
    if a.h_emax is not None:
        d = a.fix_nbhd
        counter([rm(i, j) for i in range(d + 1, N) for j in range(i + 1, N)], 0, a.h_emax, "h", None)
    codeg = []  # (u, v, [(w, sms c)])
    if a.codeg_max is not None:
        for u, v in combinations(V, 2):
            row = []
            for w in V:
                if w in (u, v):
                    continue
                nxt[0] += 1
                add([-rm(u, w), -rm(v, w), nxt[0]], None)
                row.append((w, nxt[0]))
            atmost([c for _, c in row], a.codeg_max, "codeg", (u, v))
            codeg.append((u, v, row))
    d = a.fix_nbhd
    for u in range(1, N):
        add([rm(0, u)] if u <= d else [-rm(0, u)], None)
    case_units = []
    for t in filter(None, a.edges.split(",")):
        i, j = map(int, t.split("-"))
        add([rm(i, j)], None)
        case_units.append([cx(i, j)])
    if a.block_e is not None:
        b = a.block_from
        counter([rm(i, j) for i in range(b, N) for j in range(i + 1, N)], a.block_e, a.block_e, "blk", None)
    if a.codeg_pair is not None:
        w0 = d + 1
        for i in range(1, d + 1):
            add([rm(w0, i)] if i <= a.codeg_pair else [-rm(w0, i)], None)
            case_units.append([cx(w0, i)] if i <= a.codeg_pair else [-cx(w0, i)])
    sms_cls = []
    for line in open(smsf):
        if line.startswith(("c", "p")):
            continue
        sms_cls.append([int(t) for t in line.split()[:-1]])
    need("sms base regenerated (exact, %d clauses)" % len(gen_s), sms_cls == gen_s)

    # 2. VeriPB: input = Lean file with labels on degree / e(H_0) lines
    lines = [l.strip() for l in open(lean) if l.strip() and not l.startswith("*")]
    star = {v: frozenset(cx(u, v) for u in V if u != v) for v in V}
    hset = frozenset(cx(i, j) for i in range(d + 1, N) for j in range(i + 1, N))
    labeled, labels = [], {}
    for ln in lines:
        t = ln.rstrip(";").split()
        lits = t[1:-2:2]
        vs = frozenset(int(x.lstrip("~x")) for x in lits)
        neg = all(x.startswith("~") for x in lits)
        pos = all(not x.startswith("~") for x in lits)
        lab = None
        for v in V:
            if vs == star[v]:
                lab = "@deg%s%d" % ("hi" if neg else "lo", v)
        if vs == hset:
            lab = "@h%s" % ("hi" if neg else "lo")
        if lab and (neg or pos):
            labels[lab] = int(t[-1])
            labeled.append(lab + " " + ln)
        else:
            labeled.append(ln)
    # case input part (Lemma Mc / R7): units, codegree definitions + bounds, block bounds
    DBASE = LEAN_AUX_MAX + nxt[0] - 780
    dvar = {}
    case = [sb.opb_clause(c) for c in case_units]
    for u, v, row in codeg:
        ds = []
        for w, _ in row:
            dvar[(u, v, w)] = DBASE + len(dvar) + 1
            dd = dvar[(u, v, w)]
            ds.append(dd)
            xu, xv = cx(u, w), cx(v, w)
            case += [sb.opb_clause([-dd, xu]), sb.opb_clause([-dd, xv]), sb.opb_clause([dd, -xu, -xv])]
        lab = "@cg_%d_%d" % (u, v)
        labels[lab] = len(ds) - a.codeg_max
        case.append(lab + " " + card.pb([(1, -x) for x in ds], len(ds) - a.codeg_max))
    if a.block_e is not None:
        bl = [cx(i, j) for i in range(a.block_from, N) for j in range(i + 1, N)]
        labels["@blkhi"], labels["@blklo"] = len(bl) - a.block_e, a.block_e
        case.append("@blkhi " + card.pb([(1, -x) for x in bl], len(bl) - a.block_e))
        case.append("@blklo " + card.pb([(1, x) for x in bl], a.block_e))
    labeled += [c + " ;" if not c.endswith(";") else c for c in case]
    with open("case.opb", "w") as f:
        f.write("* case constraints (Lemma Mc / R7), cert/base40_cert.py; %d constraints\n" % len(case))
        f.writelines((c.split(" ", 1)[1] if c.startswith("@") else c) + " ;\n" for c in case)
    P = codish.Proof("B")
    keep = []
    cgbound = {}
    for u, v, row in codeg:
        bridges = []
        for w, c in row:
            cl = lmap(c)
            xu, xv = cx(u, w), cx(v, w)
            keep.append(P.add("red %s : x%d -> 0 ;" % (sb.opb_clause([-cl, xu]), cl)))
            keep.append(P.add("red %s : x%d -> 0 ;" % (sb.opb_clause([-cl, xv]), cl)))
            keep.append(P.add("red %s : x%d -> 1 ;" % (sb.opb_clause([cl, -xu, -xv]), cl)))
            bridges.append(P.add("rup %s ;" % sb.opb_clause([-cl, dvar[(u, v, w)]])))
        keep += bridges
        cgbound[(u, v)] = P.add("pol @cg_%d_%d %s ;" % (u, v, " ".join("%s +" % b for b in bridges)))
    for i, j, row in mtf:
        bridge = []
        for l, c in row:
            cl = lmap(c)
            xi, xj = cx(i, l), cx(j, l)
            keep.append(P.add("red %s : x%d -> 0 ;" % (sb.opb_clause([-cl, xi]), cl)))
            keep.append(P.add("red %s : x%d -> 0 ;" % (sb.opb_clause([-cl, xj]), cl)))
            keep.append(P.add("red %s : x%d -> 1 ;" % (sb.opb_clause([cl, -xi, -xj]), cl)))
            keep.append(P.add("rup %s ;" % sb.opb_clause([-lean_c(i, j, l), cl])))
        keep.append(P.add("rup %s ;" % sb.opb_clause([cx(i, j)] + [lmap(c) for _, c in row])))
    for lits, K, s_l, kind, v in counters:
        if kind == "codeg":
            keep += card.sinz_derive(P, lits, K, s_l, cgbound[v])
            continue
        lab = {"deghi": "@deghi%d" % v if v is not None else None, "deglo": "@deglo%d" % v if v is not None else None,
               "hhi": "@hhi", "hlo": "@hlo", "blkhi": "@blkhi", "blklo": "@blklo"}[kind]
        # Sinz atmost(lits, K) needs the bound sum ~l >= m - K; check that the Lean line says exactly that
        m = len(lits)
        if labels.get(lab) != m - K:
            need("Lean bound %s equals the sms bound (%s vs %d)" % (lab, labels.get(lab), m - K), False)
            continue
        keep += card.sinz_derive(P, lits, K, s_l, lab)
    nv = DBASE + len(dvar)
    with open("in.opb", "w") as f:
        f.write("* #variable= %d #constraint= %d\n" % (nv, len(labeled)))
        f.writelines(l + "\n" for l in labeled)
    kept = set(keep)
    derived_kept = []
    for l in P.lines:
        if not l.startswith("@"):
            continue
        lab, rule, rest = l.split(" ", 2)
        if lab in kept and rule in ("red", "rup"):
            derived_kept.append(rest.split(":")[0].strip().rstrip(";").strip())
    with open("out.opb", "w") as f:
        allc = [l.split(" ", 1)[1] if l.startswith("@") else l for l in labeled] + [c + " ;" for c in derived_kept]
        f.write("* #variable= %d #constraint= %d\n" % (nv, len(allc)))
        f.writelines(c + "\n" for c in allc)
    with open("base.pbp", "w") as f:
        f.write("pseudo-Boolean proof version 3.0\nf %d ;\n" % len(labeled))
        f.write("\n".join(P.lines) + "\n")
        f.write("core id %s ;\n" % " ".join(keep))
        f.write("output EQUISATISFIABLE FILE ;\nconclusion NONE ;\nend pseudo-Boolean proof ;\n")
    r = subprocess.run([os.path.join(BIN, "veripb"), "-e", "base.elab.pbp", "in.opb", "base.pbp", "out.opb"],
                       capture_output=True, text=True)
    need("VeriPB (Lean cube -> + sms encodings)", "s VERIFIED OUTPUT EQUISATISFIABLE" in r.stdout.splitlines())
    if "s VERIFIED OUTPUT EQUISATISFIABLE" not in r.stdout.splitlines():
        print((r.stdout + r.stderr)[-500:])
    r = subprocess.run([os.path.join(BIN, "cake_pb"), "--CML_HEAP_SIZE=12000", "in.opb", "base.elab.pbp", "out.opb"],
                       capture_output=True, text=True)
    need("CakePB", "s VERIFIED OUTPUT EQUISATISFIABLE" in r.stdout.splitlines())

    # 3. glue: renamed sms base is a subset of the VeriPB output
    def norm(c):
        return frozenset(c)
    outset = set()
    for ln in open("out.opb"):
        if ln.startswith("*"):
            continue
        t = ln.strip().rstrip(";").split()
        if t[-2] == ">=" and t[-1] == "1" and all(x == "1" for x in t[0:-2:2]):
            outset.add(frozenset((-int(x[2:]) if x.startswith("~") else int(x[1:])) for x in t[1:-2:2]))
    missing = [c for c in gen_s if norm(lmap(x) for x in c) not in outset]
    need("renamed sms base is a subset of the output (%d missing)" % len(missing), not missing)
    print("RESULT:", "OK" if not fails else "FAIL %s" % fails)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
