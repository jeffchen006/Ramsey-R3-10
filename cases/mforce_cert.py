"""Exact Farkas certificates for the profile-ILP kills of cases/mforce.py (notes/cases.md Sec 7).

Author: agent `cases`, 2026-10-25.
Run: tools/venv/bin/python cases/mforce_cert.py          (make + verify, writes cases/out/mforce_certs.json)
     tools/venv/bin/python cases/mforce_cert.py --check  (verify the stored certificates only)

The profile LP (relaxation of the ILP in mforce.build) is: rows lo <= A x <= hi, box 0 <= x <= u with
u = n_d for x[d,p] (at most n_d vertices of degree d) and u = min(i n_i, j n_j) for m_ij.
Rows are written as A x <= hi and -A x <= -lo.  Certificate: y >= 0 (rationals) with
    sum_k min(0, (y^T A')_k) * u_k  >  y^T b'.
Then no x in the box satisfies A' x <= b' (since y^T A' x >= the left side), so the distribution
cannot occur.  Verification uses only integers and fractions.Fraction.
"""
import argparse
import json
import os
import sys
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, os.path.dirname(__file__))
import degseq as D  # noqa: E402
import mforce as M  # noqa: E402

KILLS = [(0, 0, 0, 9, 4, 27), (0, 0, 4, 3, 0, 33), (0, 0, 5, 1, 1, 33), (0, 0, 5, 2, 1, 32),
         (0, 0, 6, 0, 0, 34), (0, 0, 6, 0, 2, 32), (0, 0, 6, 1, 0, 33)]
OUT = os.path.join(os.path.dirname(__file__), "out", "mforce_certs.json")


def system(n, L):
    cols, A, lo, hi = M.build(n, L)
    nd = dict(zip(D.DEGS, n))
    rows, b = [], []
    for r in range(len(A)):
        a = [int(round(t)) for t in A[r]]
        assert all(abs(t - s) < 1e-9 for t, s in zip(A[r], a))
        if np.isfinite(hi[r]):
            rows.append(a); b.append(int(hi[r]))
        if np.isfinite(lo[r]):
            rows.append([-t for t in a]); b.append(-int(lo[r]))
    u = [nd[c[1]] if c[0] == "x" else min(c[1] * nd[c[1]], c[2] * nd[c[2]]) for c in cols]
    return cols, rows, b, u


def verify(rows, b, u, y):
    if any(t < 0 for t in y):
        return False
    yb = sum(t * bi for t, bi in zip(y, b) if t)
    col = [Fraction(0)] * len(u)
    for t, r in zip(y, rows):
        if t:
            for k, v in enumerate(r):
                if v:
                    col[k] += t * v
    return sum(min(Fraction(0), c) * uk for c, uk in zip(col, u)) > yb


def make(n, L):
    cols, rows, b, u = system(n, L)
    A, bb = np.array(rows, float), np.array(b, float)
    far = linprog(bb, A_ub=-A.T, b_ub=np.zeros(len(u)), bounds=[(0, 1)] * len(rows), method="highs")
    if far.status != 0 or far.fun > -1e-9:
        return None
    for den in (10 ** 4, 10 ** 6, 10 ** 8):
        y = [max(Fraction(0), Fraction(float(t)).limit_denominator(den)) for t in far.x]
        if verify(rows, b, u, y):
            return y
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    L = M.SCEN["sel"]
    if a.check:
        data = json.load(open(OUT))
        ok = 0
        for c in data["certs"]:
            n = tuple(c["n"])
            _, rows, b, u = system(n, {int(k): v for k, v in c["L"].items()})
            y = [Fraction(0)] * len(rows)
            for k, v in c["y"].items():
                y[int(k)] = Fraction(v)
            good = verify(rows, b, u, y)
            ok += good
            print(n, "VERIFIED" if good else "FAILED")
        print(f"{ok}/{len(data['certs'])} verified")
        sys.exit(0 if ok == len(data["certs"]) else 1)
    certs = []
    for n in KILLS:
        y = make(n, L)
        print(n, "certificate VERIFIED" if y else "NO certificate", flush=True)
        if y:
            certs.append({"n": list(n), "L": {str(k): v for k, v in L.items()},
                          "y": {str(r): str(t) for r, t in enumerate(y) if t}})
    json.dump({"scenario": "sel", "L": L, "certs": certs}, open(OUT, "w"), indent=0)
    print(f"{len(certs)}/{len(KILLS)} certified, written {OUT}")


if __name__ == "__main__":
    main()
