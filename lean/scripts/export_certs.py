#!/usr/bin/env python3
"""Convert the Farkas certificates of agent `cases` (certs_<tag>.json, rows of
degseq.build_lp) into Lean `R310.LP.Cert` data (rows in M-variables, integer multipliers).

Untrusted helper: Lean re-checks every certificate (R310/LP/Cert.lean, `Cert.check`).
Here we also re-check each converted certificate with the same integer arithmetic as Lean.

Usage: tools/venv/bin/python lean/scripts/export_certs.py PIN_DIR TAG OUT_DIR [BATCH]
"""
import itertools
import json
import math
import os
import sys
from fractions import Fraction

PIN, TAG, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
BATCH = int(sys.argv[4]) if len(sys.argv) > 4 else 200
sys.path.insert(0, PIN)
import degseq as D  # noqa: E402  (pinned copy of cases/degseq.py)

DEGS = D.DEGS
PAIRS = [(i, j) for i in DEGS for j in DEGS if i <= j]


def rows_with_params(n, L, mtf):
    """Same order as degseq.build_lp; each row tagged with its Lean constructor and the
    factor  y_lean = factor * y_python."""
    present = [d for d, k in zip(DEGS, n) if k > 0]
    var = [(i, j) for a, i in enumerate(present) for j in present[a:]]
    out = []
    for i in present:
        out.append((("degLe", i), Fraction(1)))
        out.append((("degGe", i), Fraction(1)))
        out.append((("hyp", i), Fraction(1)))
        if mtf:
            out.append((("mtfZ", i), Fraction(1)))
    weights = []
    for r in range(1, len(present) + 1):
        for sub in itertools.combinations(present, r):
            weights.append({d: (1 if d in sub else 0) for d in present})
    weights.append({d: 9 - d for d in present})
    weights.append({d: 10 - d for d in present})
    weights.append({d: (9 - d) ** 2 for d in present})
    for xs in itertools.product(range(4), repeat=len(present)):
        if max(xs) >= 2:
            weights.append(dict(zip(present, xs)))
    for x in weights:
        if any(x[i] * x[j] for (i, j) in var):
            out.append((("mantel", tuple(x.get(d, 0) for d in DEGS)), Fraction(1, 2)))
    for (i, j) in var:
        out.append((("ub", i, j), Fraction(1) if i < j else Fraction(1, 2)))
    for (i, j) in var:
        if i + j <= 10:
            out.append((("forced", i, j), Fraction(1) if i < j else Fraction(1, 2)))
    return out


# ---- Lean semantics, re-implemented (M-variables) -------------------------------------
def nd(n, i):
    return n[i - 4] if 4 <= i <= 9 else 0


def lean_coef(row, p):
    a, b = p
    t = row[0]
    if t in ("degLe", "degGe"):
        v = 1 if (a == row[1] or b == row[1]) else 0
        return v if t == "degLe" else -v
    if t in ("hyp", "mtfZ"):
        i = row[1]
        v = b if a == i else (a if b == i else 0)
        return v if t == "hyp" else -v
    if t == "mantel":
        x = row[1]
        return x[a - 4] ** 2 if a == b else 2 * x[a - 4] * x[b - 4]
    if t == "ub":
        return 1 if p == (row[1], row[2]) else 0
    if t == "forced":
        return -1 if p == (row[1], row[2]) else 0
    raise ValueError(t)


def lean_ubv(n, p):
    a, b = p
    if a == b:
        return 2 * (nd(n, a) * nd(n, a) // 4)
    return min(nd(n, a) * min(a, nd(n, b)), nd(n, b) * min(b, nd(n, a)))


def lean_rhs(n, L, row):
    e = sum(i * nd(n, i) for i in DEGS) // 2
    t = row[0]
    if t == "degLe":
        return row[1] * nd(n, row[1])
    if t == "degGe":
        return -row[1] * nd(n, row[1])
    if t == "hyp":
        i = row[1]
        return nd(n, i) * e - nd(n, i) * L[i - 4]
    if t == "mtfZ":
        i = row[1]
        return 11 * i * nd(n, i) - nd(n, i) * (i * i + 78)
    if t == "mantel":
        x = row[1]
        s = sum(x[i - 4] * nd(n, i) for i in DEGS)
        return 2 * (s * s // 4)
    if t == "ub":
        return lean_ubv(n, (row[1], row[2]))
    if t == "forced":
        i, j = row[1], row[2]
        return -(nd(n, i) * (nd(n, j) - (1 if i == j else 0)))
    raise ValueError(t)


def lean_check(n, L, rows):
    col = {p: sum(y * lean_coef(r, p) for r, y in rows) for p in PAIRS}
    crhs = sum(y * lean_rhs(n, L, r) for r, y in rows)
    box = sum(min(0, col[p]) * lean_ubv(n, p) for p in PAIRS)
    return crhs < box


def lean_row(r):
    t = r[0]
    if t == "mantel":
        return "(.mantel [%s])" % ",".join(map(str, r[1]))
    return "(.%s %s)" % (t, " ".join(map(str, r[1:])))


def convert(c):
    n = tuple(c["n"])
    L = [c["L"][str(d)] for d in DEGS]
    Ld = {d: c["L"][str(d)] for d in DEGS}
    mtf = c["mtf"]
    # sanity: our row list matches build_lp exactly
    var, prow, ub = D.build_lp(n, Ld, mtf=mtf)
    tagged = rows_with_params(n, Ld, mtf)
    assert len(tagged) == len(prow), (n, len(tagged), len(prow))
    yl = []
    for k, t in c["y"].items():
        y = Fraction(t)
        if y == 0:
            continue
        row, fac = tagged[int(k)]
        yl.append((row, y * fac))
    den = 1
    for _, y in yl:
        den = den * y.denominator // math.gcd(den, y.denominator)
    rows = [(row, int(y * den)) for row, y in yl]
    assert all(y > 0 for _, y in rows)
    assert lean_check(n, L, rows), ("converted cert fails", n, L)
    return n, L, mtf, rows


def lean_cert(n, L, mtf, rows):
    rs = ", ".join("(%s, %d)" % (lean_row(r), y) for r, y in rows)
    return "⟨⟨[%s], [%s], %s⟩, [%s]⟩" % (",".join(map(str, n)), ",".join(map(str, L)),
                                       "true" if mtf else "false", rs)


def main():
    certs = json.load(open(os.path.join(PIN, f"certs_{TAG}.json")))
    conv = [convert(c) for c in certs]
    os.makedirs(OUT, exist_ok=True)
    nb = (len(conv) + BATCH - 1) // BATCH
    modname = "".join(w.capitalize() for w in TAG.split("_"))
    for b in range(nb):
        chunk = conv[b * BATCH:(b + 1) * BATCH]
        with open(os.path.join(OUT, f"{modname}{b:03d}.lean"), "w") as f:
            f.write("import R310.LP.Cert\n\n-- generated by lean/scripts/export_certs.py; "
                    f"source {PIN}/certs_{TAG}.json\n\nnamespace R310.LP.Data\n\n")
            f.write(f"def certs_{TAG}_{b:03d} : List Cert := [\n  ")
            f.write(",\n  ".join(lean_cert(*x) for x in chunk))
            f.write("]\n\n")
            f.write(f"theorem certs_{TAG}_{b:03d}_ok : certs_{TAG}_{b:03d}.all Cert.check = true := by\n"
                    "  decide +kernel\n\nend R310.LP.Data\n")
    print(f"{len(conv)} certificates converted and re-checked; {nb} files in {OUT}")


if __name__ == "__main__":
    main()
