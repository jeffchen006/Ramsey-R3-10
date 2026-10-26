#!/usr/bin/env python3
"""cert/glue.py - trusted glue of the certificate chain (links b, c, d, f).

Written by agent `cert`. Short on purpose: this file is part of the trusted base.
cake_lpr exits 0 even when a check fails, so every verdict here is read from stdout.

Subcommands
  summary  --cnf F --summary S --ranges R
      Two-level mode. Runs `cake_lpr F S -check R`. Accepts only if stdout has the exact
      line "s VERIFIED INTERVALS COVER 0-<lines of S>" AND S contains the empty clause.
      (cake_lpr's COVER alone only means: F SAT => F + all lines of S SAT.)
      Verdict: "GLUE OK: F UNSAT".
  run-cube --cnf F --log L [--cadical BIN] [--cake BIN]
      Streams CaDiCaL's binary LRAT through a FIFO into cake_lpr (no proof stored).
      Writes L: "sha256 <hex>", then cake_lpr's stdout. (Part of the trusted runner.)
  percube  --n N --s S --manifest M [--allowed FILE]...
      Per-cube mode (for n = 40, lazy clauses differ per cube). Manifest lines:
          cube  <lit> ... 0  <F_j.cnf>  <log>
          cover <cover.cnf> <log>
      Checks: each F_j contains every unit of c_j, and every clause of F_j is TRI/IS
      (check_cnf), in an --allowed file (e.g. VeriPB output: MTF + SB + card CNF), or a
      unit of c_j; the cover file contains NOT c_j for every cube and otherwise only
      TRI/IS/allowed clauses; every log has "sha256 <hex>" equal to the file's sha256 now
      and the exact line "s VERIFIED UNSAT".
      Verdict: "GLUE OK: allowed + IS + TRI UNSAT" (with the VeriPB output step this
      gives F_def UNSAT; see notes/cert_design.md sec. 1).
"""
import argparse
import hashlib
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "..", "tools", "bin")


def clauses(path):
    out, cur = [], []
    for line in open(path):
        if line.startswith(("c", "p")):
            continue
        for t in line.split():
            l = int(t)
            if l == 0:
                out.append(tuple(cur))
                cur = []
            else:
                cur.append(l)
    return out


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def fail(msg):
    print("GLUE FAIL:", msg)
    sys.exit(1)


def cmd_summary(a):
    S = clauses(a.summary)
    r = subprocess.run([a.cake, a.cnf, a.summary, "-check", a.ranges], capture_output=True, text=True)
    want = "s VERIFIED INTERVALS COVER 0-%d" % len(S)
    print("cake_lpr -check:", r.stdout.strip()[:200])
    if want not in r.stdout.splitlines():
        fail("cake_lpr did not print '%s'" % want)
    if () not in S:
        fail("summary has no empty clause: COVER only means F SAT => F + summary SAT")
    print("GLUE OK: %s UNSAT (summary of %d lines with the empty clause, all ranges verified)" % (a.cnf, len(S)))


def cmd_run_cube(a):
    h = sha(a.cnf)
    with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.abspath(a.log))) as d:
        fifo = os.path.join(d, "proof.fifo")
        os.mkfifo(fifo)
        solver = subprocess.Popen([a.cadical, "-q", "--lrat", "--binary=true", a.cnf, fifo],
                                  stdout=subprocess.PIPE, text=True)
        chk = subprocess.run([a.cake, a.cnf, fifo], capture_output=True, text=True)
        solver.wait()
    with open(a.log, "w") as f:
        f.write("sha256 %s\n" % h)
        f.write(chk.stdout)
        f.write(chk.stderr)
    print(open(a.log).read().strip())


def check_cnf(n, s, path, extras):
    r = subprocess.run([sys.executable, os.path.join(HERE, "check_cnf.py"), "--n", str(n), "--s", str(s)]
                       + [x for e in extras for x in ("--extra", e)] + [path], capture_output=True, text=True)
    return "RESULT: OK (every clause is valid or listed as extra)" in r.stdout.splitlines()


def check_log(path, log):
    lines = open(log).read().splitlines()
    if not lines or lines[0] != "sha256 %s" % sha(path):
        fail("%s: sha256 in log does not match the file" % log)
    if "s VERIFIED UNSAT" not in lines:
        fail("%s: no 's VERIFIED UNSAT' line" % log)


def cmd_percube(a):
    cubes, cover = [], None
    for line in open(a.manifest):
        t = line.split()
        if not t or t[0].startswith("#"):
            continue
        if t[0] == "cube":
            z = t.index("0")
            cubes.append((tuple(int(x) for x in t[1:z]), t[z + 1], t[z + 2]))
        elif t[0] == "cover":
            cover = (t[1], t[2])
        else:
            fail("bad manifest line: " + line.strip())
    if cover is None or not cubes:
        fail("manifest needs cubes and one cover line")
    with tempfile.TemporaryDirectory() as d:
        for k, (cube, path, log) in enumerate(cubes):
            units = os.path.join(d, "units%d.cnf" % k)
            with open(units, "w") as f:
                f.write("p cnf %d %d\n" % (max(abs(l) for l in cube), len(cube)))
                f.writelines("%d 0\n" % l for l in cube)
            have = set(frozenset(c) for c in clauses(path))
            if any(frozenset([l]) not in have for l in cube):
                fail("%s does not contain all units of its cube" % path)
            if not check_cnf(a.n, a.s, path, a.allowed + [units]):
                fail("%s has a clause that is not TRI/IS/allowed/cube unit" % path)
            check_log(path, log)
        neg = os.path.join(d, "neg.cnf")
        with open(neg, "w") as f:
            f.write("p cnf %d %d\n" % (max(abs(l) for c, _, _ in cubes for l in c), len(cubes)))
            f.writelines(" ".join(str(-l) for l in c) + " 0\n" for c, _, _ in cubes)
        have = set(frozenset(c) for c in clauses(cover[0]))
        if any(frozenset(-l for l in c) not in have for c, _, _ in cubes):
            fail("cover file misses NOT c_j for some cube")
        if not check_cnf(a.n, a.s, cover[0], a.allowed + [neg]):
            fail("cover file has a clause that is not TRI/IS/allowed/NOT cube")
        check_log(cover[0], cover[1])
    print("GLUE OK: allowed + IS + TRI UNSAT (%d cubes each UNSAT, cover UNSAT, all logs match files)" % len(cubes))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("summary")
    p.add_argument("--cnf", required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--ranges", required=True)
    p.add_argument("--cake", default=os.path.join(BIN, "cake_lpr"))
    p = sub.add_parser("run-cube")
    p.add_argument("--cnf", required=True)
    p.add_argument("--log", required=True)
    p.add_argument("--cadical", default=os.path.join(BIN, "cadical"))
    p.add_argument("--cake", default=os.path.join(BIN, "cake_lpr"))
    p = sub.add_parser("percube")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--s", type=int, required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--allowed", action="append", default=[])
    a = ap.parse_args()
    {"summary": cmd_summary, "run-cube": cmd_run_cube, "percube": cmd_percube}[a.cmd](a)


if __name__ == "__main__":
    main()
