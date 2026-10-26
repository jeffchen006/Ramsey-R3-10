#!/usr/bin/env python3
"""cert/mc_cert.py - certify a MathCheckRamsey (Li-Duggan-Bright-Ganesh, IJCAI 2025) run.

Written by agent `cert`. MathCheck's DRAT proofs contain trusted "t" clauses (CAS
orderly-generation blocking clauses) that its drat-trim fork skips; here they become
VeriPB dominance steps, so no clause is trusted.
Input: the MathCheck CNF (generate.py with lower=upper=0, no MPCF: p-clique clauses,
q-set clauses, `cubic` lex constraints), the DRAT proof with "t" lines, the .perm file.
Steps:
  1. Regenerate the CNF with cert's own code (TRI, IS, MathCheck's lex clause shapes and
     aux numbering) and compare clause multisets.
  2. Every "t" clause: check_sb (exact; order = lex-MIN of the colex edge vector).
  3. VeriPB + CakePB, input TRI: the `cubic` clauses (one PB lex constraint per pair i<j
     by `dom`, aux definitions by `red`, clauses by `pol`/`rup`) and the "t" clauses
     (one `dom` each), all under ONE order (lex-min, colex positions); output TRI + both.
     check_pbp (M-IS) and check_cnf --require-all-tri on the input.
  4. F' = CNF + "t" clauses; proof = DRAT without "t" lines; drat-trim -> LRAT; cake_lpr.
     check_cnf on F' (TRI / IS / VeriPB output).
Usage: mc_cert.py N P Q CNF DRAT PERM WORKDIR    (P = 3: triangles; Q = s)
"""
import os
import subprocess
import sys
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import codish  # noqa: E402
import sb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "..", "tools", "bin")


def read_cnf(path):
    nv, out, cur = 0, [], []
    for line in open(path):
        if line.startswith("p"):
            nv = int(line.split()[2])
        if line.startswith(("c", "p")):
            continue
        for t in line.split():
            l = int(t)
            if l == 0:
                out.append(cur)
                cur = []
            else:
                cur.append(l)
    return nv, out


def ms(cls):
    d = {}
    for c in cls:
        k = frozenset(c)
        d[k] = d.get(k, 0) + 1
    return d


def write_opb(path, nv, cons):
    with open(path, "w") as f:
        f.write("* #variable= %d #constraint= %d\n" % (nv, len(cons)))
        f.writelines(c + " ;\n" for c in cons)


def main():
    n, p, q = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    cnf, drat, perm, W = [os.path.abspath(x) for x in sys.argv[4:8]]
    assert p == 3
    os.makedirs(W, exist_ok=True)
    os.chdir(W)
    sb.POSITIONS = "colex"
    nedge = n * (n - 1) // 2
    nv, F = read_cnf(cnf)
    fails = []

    def need(name, ok):
        print("%-28s %s" % (name, "OK" if ok else "FAIL"))
        if not ok:
            fails.append(name)

    # 1. regenerate (MathCheck order: p-clique clauses, q-set clauses, cubic)
    tri = [[-sb.var(a, b) for a, b in combinations(T, 2)] for T in combinations(range(n), 3)]
    iss = [[sb.var(a, b) for a, b in combinations(S, 2)] for S in combinations(range(n), q)]
    B = lambda i, j: sb.var(i, j)  # noqa: E731
    cubic, struct, count = [], [], nedge
    for j in range(n):
        for i in range(j):
            cols = [c for c in range(n) if c not in (i, j)]
            X = [B(i, c) for c in cols]
            Y = [B(j, c) for c in cols]
            L = len(X)
            t = [None] + [count + k for k in range(1, L)]
            cubic += [[-X[0], Y[0]], [-X[0], t[1]], [Y[0], t[1]]]
            for k in range(1, L - 1):
                cubic += [[-t[k], -X[k], Y[k]], [-t[k], -X[k], t[k + 1]], [-t[k], Y[k], t[k + 1]]]
            cubic.append([-t[L - 1], -X[L - 1], Y[L - 1]])
            count += L - 1
            struct.append((i, j, X, Y, t))
    need("CNF regenerated", ms(F) == ms(tri + iss + cubic) and nv == count)

    # 2. t clauses
    subprocess.run([sys.executable, os.path.join(HERE, "mc2wit.py"), str(n), drat, perm, "t.wit"],
                   capture_output=True, text=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, "check_sb.py"), "--n", str(n), "--order", "colex",
                        "--positions", "colex", "--better", "min", "t.wit"], capture_output=True, text=True)
    need("check_sb t clauses", "RESULT: OK" in r.stdout.splitlines())
    tw = {}
    for line in open("t.wit"):
        left, right = line.split("|")
        cl = tuple(sorted(int(x) for x in left.split()[:-1]))
        tw.setdefault(cl, [int(x) for x in right.split()])

    # 3. VeriPB
    pos = sb.positions(n)
    cm = {sb.var(*pp): 2 ** (nedge - 1 - k) for k, pp in enumerate(pos)}
    P = codish.Proof("M")
    keep = []
    for i, j, X, Y, t in struct:
        pi = list(range(n))
        pi[i], pi[j] = j, i
        w = sb.witness(n, pi)
        pairs = list(zip(Y, X))                       # constraint: Y >=lex X, i.e. row_i <= row_j
        d = [cm[x] - cm[y] for x, y in zip(X, Y)]     # X sits at the earlier colex position
        labs = codish.derive_one(P, w, pairs, d, t)   # A_1, c1_1, c2_1, A_2, ...
        L = len(X)
        dead = []
        for k in range(L):
            keep.append(labs[3 * k])                  # A_{k+1} = (-t_k) -X_k Y_k
            if k < L - 1:
                pre = [-t[k]] if t[k] else []
                keep.append(P.add("rup %s ;" % sb.opb_clause(pre + [-X[k], t[k + 1]])))
                keep.append(P.add("rup %s ;" % sb.opb_clause(pre + [Y[k], t[k + 1]])))
                dead += labs[3 * k + 1:3 * k + 3]
        P.raw("deld %s ;" % " ".join(dead))
    for cl, pi in sorted(tw.items()):
        keep.append(P.add("dom %s : %s ;" % (sb.opb_clause(list(cl)), sb.witness(n, pi))))
    inp = [sb.opb_clause(c) for c in tri]
    tcl = [list(c) for c in sorted(tw)]
    write_opb("in.opb", count, inp)
    write_opb("out.opb", count, inp + [sb.opb_clause(c) for c in cubic + tcl])
    sb.write_veripb("hdr.pbp", n, len(inp), [], better="min")
    hdr = open("hdr.pbp").read().splitlines()
    k = [x for x, l in enumerate(hdr) if l.startswith("load_order lexmax")][0]
    with open("mc.pbp", "w") as f:
        f.write("\n".join(hdr[:k + 1] + P.lines) + "\n")
        f.write("load_order ;\ncore id %s ;\n" % " ".join(keep))
        f.write("output EQUISATISFIABLE FILE ;\nconclusion NONE ;\nend pseudo-Boolean proof ;\n")
    r = subprocess.run([os.path.join(BIN, "veripb"), "-e", "mc.elab.pbp", "in.opb", "mc.pbp", "out.opb"],
                       capture_output=True, text=True)
    need("VeriPB", "s VERIFIED OUTPUT EQUISATISFIABLE" in r.stdout.splitlines())
    if "s VERIFIED OUTPUT EQUISATISFIABLE" not in r.stdout.splitlines():
        print((r.stdout + r.stderr)[-600:])
    r = subprocess.run([os.path.join(BIN, "cake_pb"), "in.opb", "mc.elab.pbp", "out.opb"],
                       capture_output=True, text=True)
    need("CakePB", "s VERIFIED OUTPUT EQUISATISFIABLE" in r.stdout.splitlines())
    r = subprocess.run([sys.executable, os.path.join(HERE, "check_pbp.py"), "--n", str(n), "--input-constraints",
                        str(len(inp)), "mc.pbp"], capture_output=True, text=True)
    need("check_pbp (M-IS)", "RESULT: OK (M-IS conditions W, D, I, R hold)" in r.stdout.splitlines())
    r = subprocess.run([sys.executable, os.path.join(HERE, "check_cnf.py"), "--n", str(n), "--s", str(q), "--opb",
                        "--require-all-tri", "in.opb"], capture_output=True, text=True)
    need("VeriPB input = all TRI", "RESULT: OK (every clause is valid or listed as extra)" in r.stdout.splitlines())

    # 4. DRAT -> LRAT -> cake_lpr on F' = CNF + t clauses
    tlines = [l for l in open(drat) if l.startswith("t ")]
    with open("Fp.cnf", "w") as f:
        f.write("p cnf %d %d\n" % (count, len(F) + len(tlines)))
        f.writelines(" ".join(map(str, c)) + " 0\n" for c in F)
        f.writelines(l[2:] for l in tlines)
    with open("p.drat", "w") as f:
        f.writelines(l for l in open(drat) if not l.startswith("t "))
    with open("extra.cnf", "w") as f:
        f.write("p cnf %d %d\n" % (count, len(cubic) + len(tcl)))
        f.writelines(" ".join(map(str, c)) + " 0\n" for c in cubic + tcl)
    r = subprocess.run([sys.executable, os.path.join(HERE, "check_cnf.py"), "--n", str(n), "--s", str(q),
                        "--extra", "extra.cnf", "Fp.cnf"], capture_output=True, text=True)
    need("check_cnf F'", "RESULT: OK (every clause is valid or listed as extra)" in r.stdout.splitlines())
    r = subprocess.run([os.path.join(BIN, "drat-trim"), "Fp.cnf", "p.drat", "-L", "p.lrat"],
                       capture_output=True, text=True)
    print("drat-trim:", [l for l in r.stdout.splitlines() if l.startswith("s ")])
    r = subprocess.run([os.path.join(BIN, "cake_lpr"), "--CML_HEAP_SIZE=10000", "--CML_STACK_SIZE=2000", "Fp.cnf", "p.lrat"], capture_output=True, text=True)
    need("cake_lpr F'", "s VERIFIED UNSAT" in r.stdout.splitlines())
    print("RESULT:", "OK" if not fails else "FAIL %s" % fails)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
