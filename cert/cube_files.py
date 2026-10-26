#!/usr/bin/env python3
"""cert/cube_files.py - cert's own generator of the n = 40 cube formulas and comparison.

Written by agent `cert`. Spec: notes/cert_design.md sec. 3.9, cert/cases40.txt,
notes/cases.md Sec. 4a. Generates cube_{R,S8,N}.opb independently of Lean:
  TRI (gen.py), MTF full definitions (mtf.py, colex pair order, aux id 781 + 38 p + r),
  N(0) units, degree bounds per vertex, e(H_0) bound (R: both sides, = 99),
and compares each with another file (e.g. lean/out/cube_X.opb) as a MULTISET of
normalized constraints (terms sorted, literal form kept, rhs). Exit 0 iff all equal.
Usage: cube_files.py OUTDIR [OTHERDIR]
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mtf  # noqa: E402
import sb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
N_V = 40
CUBES = {  # d, degree lo..hi, e(H_0) <= t, e(H_0) >= tlo (or None)
    "R": (9, 9, 9, 99, 99),
    "S8": (8, 6, 9, 96, None),
    "N": (9, 6, 9, 98, None),
}


def lit(l):
    return ("~x%d" % -l) if l < 0 else ("x%d" % l)


def pb(terms, rhs):
    return " ".join("%d %s" % (c, lit(l)) for c, l in terms) + " >= %d" % rhs


def cube(name, tri, mtfc):
    d, lo, hi, t, tlo = CUBES[name]
    n = N_V
    out = [sb.opb_clause(c) for c in tri + mtfc]
    out += [sb.opb_clause([sb.var(0, u) if u <= d else -sb.var(0, u)]) for u in range(1, n)]
    for v in range(n):
        xs = [sb.var(u, v) for u in range(n) if u != v]
        out.append(pb([(1, x) for x in xs], lo))
        out.append(pb([(1, -x) for x in xs], len(xs) - hi))
    h = [sb.var(i, j) for i in range(d + 1, n) for j in range(i + 1, n)]
    out.append(pb([(1, -x) for x in h], len(h) - t))
    if tlo is not None:
        out.append(pb([(1, x) for x in h], tlo))
    return out


def norm(line):
    t = line.strip().rstrip(";").split()
    assert t[-2] == ">=", line
    terms = tuple(sorted(zip(t[0:-2:2], t[1:-2:2]), key=lambda p: (p[1].lstrip("~"), p[1], p[0])))
    return (terms, t[-1])


def ms(lines):
    d = {}
    for l in lines:
        k = norm(l)
        d[k] = d.get(k, 0) + 1
    return d


def main():
    outdir = sys.argv[1]
    other = sys.argv[2] if len(sys.argv) > 2 else None
    os.makedirs(outdir, exist_ok=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, "gen.py"), "tri", str(N_V), "10"], capture_output=True, text=True)
    tri = [[int(x) for x in l.split()[:-1]] for l in r.stdout.splitlines() if l and not l.startswith(("c", "p"))]
    M = mtf.MTF(N_V, "colex", 781)
    mtfc = M.clauses()
    ok = True
    for name in CUBES:
        cons = cube(name, tri, mtfc)
        path = os.path.join(outdir, "cube_%s.opb" % name)
        with open(path, "w") as f:
            f.write("* cert/cube_files.py cube_%s; constraints: %d\n" % (name, len(cons)))
            f.writelines(c + " ;\n" for c in cons)
        msg = "cube_%s: %d constraints" % (name, len(cons))
        if other:
            theirs = [l for l in open(os.path.join(other, "cube_%s.opb" % name)) if l.strip() and not l.startswith("*")]
            a, b = ms(cons), ms(theirs)
            same = a == b
            ok &= same
            msg += "; %s: %d constraints; multisets %s" % (other, len(theirs), "EQUAL" if same else "DIFFER")
            if not same:
                only_a = [k for k in a if a[k] != b.get(k, 0)][:3]
                only_b = [k for k in b if b[k] != a.get(k, 0)][:3]
                msg += "\n   cert-only/count: %s\n   other-only/count: %s" % (only_a, only_b)
        print(msg)
    print("RESULT:", "OK" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
