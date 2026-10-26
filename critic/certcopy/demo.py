#!/usr/bin/env python3
"""cert/demo.py - end-to-end certified non-existence demo for (3,s,n).

Written by agent `cert`. Run under: taskset -c 68-71 nice -n 5 venv/bin/python demo.py N S [DEPTH]

Chain produced in demo/r3_<s>_<n>/:
  F_full.cnf  all triangle + all s-set clauses (cert/gen.py)       link (a)
  cubes: c_d = "N(0) = {1..d}" first switch in row 0; d = 0..n-1   link (b)
  sb_all.cnf  static + dynamic lex SB clauses; sb_all.wit (clause | pi)
     VeriPB  : F_full  -> F_full + SB  EQUISATISFIABLE (dominance)  link (e)
     CakePB  : same, elaborated proof, verified checker
     VeriPB  : F_tri   -> F_tri + SB   (n=40 style; meta-lemma for IS part)
     check_sb: independent re-check of every SB clause with its pi
  F_cert.cnf  triangles + SB + lazily generated s-set clauses       link (f)
     check_cnf: every clause is TRI, IS or listed in sb_all.cnf
  summary.txt lines: NOT c_1, ..., NOT c_m, empty clause
     line j < m : LRAT from F_cert + lines<j (per-cube proof)         link (d)
     line m     : LRAT from F_cert + all NOT c_j (cube cover proof)  link (c)
     cake_lpr F_cert summary j-(j+1) proof_j ; cake_lpr ... -check -> s VERIFIED INTERVALS COVER 0-(m+1)
     glue: summary.txt ends with the empty clause => F_cert UNSAT
"""
import hashlib
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mtf  # noqa: E402
import sb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = "./tools/bin"
PY = sys.executable


def sh(cmd, out=None, check=True):
    t = time.time()
    with open(out, "w") if out else open(os.devnull, "w") as f:
        r = subprocess.run(cmd, stdout=f if out else subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    dt = time.time() - t
    if check and r.returncode != 0:
        raise SystemExit("command failed (%d): %s" % (r.returncode, " ".join(cmd)))
    return r, dt


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def read_cnf(path):
    cls, cur = [], []
    for line in open(path):
        if line.startswith(("c", "p")):
            continue
        for t in line.split():
            l = int(t)
            if l == 0:
                cls.append(cur)
                cur = []
            else:
                cur.append(l)
    return cls


def write_cnf(path, nv, cls, comment=""):
    with open(path, "w") as f:
        if comment:
            f.write("c %s\n" % comment)
        f.write("p cnf %d %d\n" % (nv, len(cls)))
        for c in cls:
            f.write(" ".join(map(str, c)) + " 0\n")


def cube_lits(n, d):
    if d == 0:
        return [-sb.var(0, 1)]
    if d == n - 1:
        return [sb.var(0, n - 1)]
    return [sb.var(0, d), -sb.var(0, d + 1)]


def transform_lrat(src, dst, neg_cube, unit_ids, norig):
    """LRAT refutation of (F + cube units) -> LRAT derivation of clause NOT cube
    from F: add NOT cube to every lemma, drop hints/deletions of the cube-unit
    clauses (their literals are now assigned by the negated lemma). A valid
    hint chain never uses a clause that contains a cube literal positively
    (other than the unit itself), so the new chains stay valid; cake_lpr
    re-checks everything anyway. A lemma that contains a cube literal
    positively becomes a tautology: it is dropped, and so are references to it
    (its cube literal is already true in the new context).
    Deletions of input clauses (ids <= norig) are dropped: cake_lpr's range
    check wants every clause of F + summary lines to survive the proof."""
    cube = {-l for l in neg_cube}
    unit_ids = set(unit_ids)
    extra = [str(l) for l in neg_cube]
    with open(src) as f, open(dst, "w") as g:
        for line in f:
            t = line.split()
            if not t:
                continue
            if t[1] == "d":
                ids = [x for x in t[2:-1] if int(x) not in unit_ids and int(x) > norig]
                if ids:
                    g.write(" ".join([t[0], "d"] + ids + ["0"]) + "\n")
                continue
            z = t.index("0", 1)
            lits = [int(x) for x in t[1:z]]
            if any(l in cube for l in lits):
                unit_ids.add(int(t[0]))
                continue
            hints = [x for x in t[z + 1:-1] if int(x) not in unit_ids]
            g.write(" ".join([t[0]] + [str(l) for l in lits if -l not in cube] + extra + ["0"] + hints + ["0"]) + "\n")


def main():
    n, s = int(sys.argv[1]), int(sys.argv[2])
    depth = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    variants = ("full", "tri") if "--skip-full" not in sys.argv else ("tri",)
    use_mtf = "--mtf" in sys.argv
    D = os.path.join(HERE, "demo", "r3_%d_%d%s" % (s, n, "_mtf" if use_mtf else ""))
    os.makedirs(D, exist_ok=True)
    os.chdir(D)
    M = mtf.MTF(n)
    nv = M.nvars if use_mtf else n * (n - 1) // 2
    mtfc = M.clauses() if use_mtf else []
    log = open("RESULT.txt", "w")

    def say(msg):
        print(msg)
        log.write(msg + "\n")
        log.flush()

    say("# certified demo: no (3,%d,%d)-graph   (cert/demo.py, %s)" % (s, n, time.strftime("%Y-%m-%d %H:%M")))

    # (a) base formulas
    sh([PY, os.path.join(HERE, "gen.py"), "full", str(n), str(s)], "F_full.cnf")
    sh([PY, os.path.join(HERE, "gen.py"), "tri", str(n), str(s)], "F_tri.cnf")
    r, _ = sh([PY, os.path.join(HERE, "check_cnf.py"), "--n", str(n), "--s", str(s), "F_full.cnf"], "check_F_full.log")
    say("(a) F_full.cnf sha256 %s : check_cnf OK (only TRI/IS clauses)" % sha("F_full.cnf"))

    # (b) cubes + lazy solving per cube
    cubes = [cube_lits(n, d) for d in range(n)]
    with open("cubes.txt", "w") as f:
        for c in cubes:
            f.write("a %s 0\n" % " ".join(map(str, c)))
    os.makedirs("lazy", exist_ok=True)
    static = sb.static_clauses(n, depth)
    sbw = {}
    for cl, pi in static:
        sbw.setdefault(tuple(sorted(cl)), pi)
    lazy_is = {}
    t0 = time.time()
    for d, c in enumerate(cubes):
        r, _ = sh([PY, os.path.join(HERE, "lazy.py"), str(n), str(s), str(depth), " ".join(map(str, c)), "lazy/c%d" % d]
                  + (["20", "--mtf"] if use_mtf else []),
                  "lazy/c%d.log" % d, check=False)
        if r.returncode != 0:
            raise SystemExit("cube %d not UNSAT, see lazy/c%d.log" % (d, d))
        for line in open("lazy/c%d.sbdyn" % d):
            left, right = line.split("|")
            cl = tuple(sorted(int(x) for x in left.split()[:-1]))
            sbw.setdefault(cl, [int(x) for x in right.split()])
        sec = None
        for line in open("lazy/c%d.cnf" % d):
            if line.startswith("c section"):
                sec = line.split()[2]
                continue
            if sec == "lazy-is" and not line.startswith("c"):
                cl = tuple(sorted(int(x) for x in line.split()[:-1]))
                lazy_is[cl] = 1
    say("(b) %d cubes c_d (d = deg(0) under SB); lazy solving %.1f s; %d SB clauses, %d lazy IS clauses"
        % (len(cubes), time.time() - t0, len(sbw), len(lazy_is)))

    # (e) symmetry breaking: VeriPB, CakePB, independent check
    sbl = sorted(sbw.items())
    write_cnf("sb_all.cnf", nv, [list(c) for c, _ in sbl], "SB clauses (lex-max, row-major)")
    with open("sb_all.wit", "w") as f:
        for c, pi in sbl:
            f.write("%s 0 | %s\n" % (" ".join(map(str, c)), " ".join(map(str, pi))))
    write_cnf("mtf.cnf", nv, mtfc, "MTF clauses (cert/mtf.py)")
    r, _ = sh([PY, os.path.join(HERE, "check_sb.py"), "--n", str(n), "sb_all.wit"], "check_sb.log")
    say("(e) check_sb: %s" % open("check_sb.log").read().strip().splitlines()[-1])
    for tag in variants:
        base = "F_%s.cnf" % tag
        base_cls = read_cnf(base)
        write_cnf("in_%s.cnf" % tag, nv, base_cls)
        ncl = sb.cnf_to_opb("in_%s.cnf" % tag, "in_%s.opb" % tag)
        write_cnf("out_%s.cnf" % tag, nv, base_cls + mtfc + [list(c) for c, _ in sbl])
        sb.cnf_to_opb("out_%s.cnf" % tag, "out_%s.opb" % tag)
        sb.write_veripb("sb_%s.pbp" % tag, n, ncl, [(list(c), pi) for c, pi in sbl],
                        prefix=M.proof_lines() if use_mtf else (),
                        aux_witness=M.aux_witness if use_mtf else None)
        r, dt = sh([os.path.join(BIN, "veripb"), "-e", "sb_%s.elab.pbp" % tag,
                    "in_%s.opb" % tag, "sb_%s.pbp" % tag, "out_%s.opb" % tag], "veripb_%s.log" % tag)
        ok = "s VERIFIED OUTPUT EQUISATISFIABLE" in open("veripb_%s.log" % tag).read()
        r, dt2 = sh([os.path.join(BIN, "cake_pb"), "in_%s.opb" % tag, "sb_%s.elab.pbp" % tag,
                     "out_%s.opb" % tag], "cakepb_%s.log" % tag, check=False)
        ok2 = "s VERIFIED OUTPUT EQUISATISFIABLE" in open("cakepb_%s.log" % tag).read()
        say("(e) %s: VeriPB %s (%.1f s), CakePB %s (%.1f s): F_%s SAT => F_%s + %sSB SAT"
            % (tag, "OK" if ok else "FAIL", dt, "OK" if ok2 else "FAIL", dt2, tag, tag, "MTF + " if use_mtf else ""))
        if not (ok and ok2):
            raise SystemExit("SB proof failed")

    # (f) certificate formula
    tri = read_cnf("F_tri.cnf")
    fcert = tri + mtfc + [list(c) for c, _ in sbl] + [list(c) for c in sorted(lazy_is)]
    write_cnf("F_cert.cnf", nv, fcert, "F_tri + MTF + SB + lazy IS clauses")
    sh([PY, os.path.join(HERE, "check_cnf.py"), "--n", str(n), "--s", str(s), "--extra", "sb_all.cnf",
        "--extra", "mtf.cnf", "F_cert.cnf"], "check_F_cert.log")
    say("(f) F_cert.cnf sha256 %s : %d clauses, check_cnf OK" % (sha("F_cert.cnf"), len(fcert)))

    # (c),(d) compositional proof checked by cake_lpr
    os.makedirs("proofs", exist_ok=True)
    summary = [[-l for l in c] for c in cubes] + [[]]
    with open("summary.txt", "w") as f:
        for c in summary:
            f.write(" ".join(map(str, c + [0])) + "\n")
    outs = []
    tsolve = tcheck = 0.0
    lrat_bytes = 0
    for j, line in enumerate(summary):
        prev = fcert + summary[:j]
        write_cnf("proofs/F%d.cnf" % j, nv, prev)
        cube = cubes[j] if j < len(cubes) else []
        write_cnf("proofs/Q%d.cnf" % j, nv, prev + [[u] for u in cube])
        _, dt = sh([os.path.join(BIN, "cadical"), "-q", "--lrat", "--binary=false", "proofs/Q%d.cnf" % j,
                    "proofs/Q%d.lrat" % j], check=False)
        units = set(range(len(prev) + 1, len(prev) + len(cube) + 1))
        transform_lrat("proofs/Q%d.lrat" % j, "proofs/P%d.lrat" % j, line, units, len(prev) + len(cube))
        tsolve += dt
        lrat_bytes += os.path.getsize("proofs/P%d.lrat" % j)
        _, dt = sh([os.path.join(BIN, "cake_lpr"), "F_cert.cnf", "summary.txt", "%d-%d" % (j, j + 1),
                    "proofs/P%d.lrat" % j], "proofs/P%d.cake.log" % j, check=False)
        tcheck += dt
        outs.append(open("proofs/P%d.cake.log" % j).read())
        for p in ("proofs/F%d.cnf" % j, "proofs/Q%d.cnf" % j, "proofs/Q%d.lrat" % j):
            if os.path.exists(p):
                os.remove(p)
    with open("cake_ranges.txt", "w") as f:
        f.write("".join(outs))
    nver = sum(o.count("s VERIFIED RANGE") for o in outs)
    sh([os.path.join(BIN, "cake_lpr"), "F_cert.cnf", "summary.txt", "-check", "cake_ranges.txt"],
       "cake_check.log", check=False)
    final = open("cake_check.log").read().strip()
    say("(c,d) %d summary lines (%d cubes + cover); %d ranges VERIFIED; solve %.1f s, check %.1f s, LRAT %.1f MB"
        % (len(summary), len(cubes), nver, tsolve, tcheck, lrat_bytes / 1e6))
    say("(c,d) cake_lpr -check: %s" % final)
    # cake_lpr -check only says: F_cert SAT => F_cert + all summary lines SAT.
    # UNSAT needs the empty clause among the summary lines (checked here, glue).
    empty_last = open("summary.txt").read().splitlines()[-1].split() == ["0"]
    say("(c,d) summary.txt md5 %s, last line is the empty clause: %s"
        % (hashlib.md5(open("summary.txt", "rb").read()).hexdigest(), empty_last))
    if final != "s VERIFIED INTERVALS COVER 0-%d" % len(summary) or not empty_last:
        raise SystemExit("compositional check failed")
    say("CONCLUSION: F_cert UNSAT (cake_lpr) and F_cert <= F_full + %sSB (check_cnf) and "
        "F_full SAT => F_full + %sSB SAT (VeriPB, CakePB) => F_full UNSAT => no (3,%d,%d)-graph "
        "(given gen.py encodes the definition; link (a))." % (("MTF + " if use_mtf else ""), ("MTF + " if use_mtf else ""), s, n))


if __name__ == "__main__":
    main()
