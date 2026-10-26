"""How many vertices with small e(H_v) are forced?  (Angeltveit-McKay style excess forcing.)

Author: agent `cases`, 2026-10-25.  Notes: notes/cases.md Sec 7.
Run: tools/venv/bin/python cases/mforce.py [--scen sel] [--emin 167]

For each MTF degree distribution n (cases/out/cases_gr_mtf.csv) we build a PROFILE ILP:
x[d,p] = number of d-vertices whose neighbour-degree multiset is p (p_j = #neighbours of
degree j).  Z(p) = sum_j j p_j, e(H_v) = e - Z(p).  Valid rows (notes/cases.md L8, M2):
  sum_p x[d,p] = n_d;   m_ij = sum_p x[i,p] p_j = sum_p x[j,p] p_i (i<j);  2 m_ii = sum_p x[i,p] p_i;
  profile allowed only if e - Z(p) >= L_d (scenario gluing bounds) and Z(p) >= d^2-11d+78 (M2);
  Mantel/Motzkin-Straus rows on m_ij (same weight family as degseq.build_lp).
Objective: minimise m_T = #9-vertices with e(H_v) <= T.  The ILP optimum is a valid lower
bound for every (3,10,40)-graph with distribution n (solver result, no exact certificate yet).
"""
import argparse
import csv
import itertools
import json
import os
import sys

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

sys.path.insert(0, os.path.dirname(__file__))
import degseq as D  # noqa: E402

SCEN = {
    "sel": {9: 91, 8: 100, 7: 113, 6: 122},    # T* = 90, U8 <= 99, U7 <= 112, U6 <= 121
    "U8": {9: 87, 8: 97, 7: 104, 6: 118},      # S8 + R(3,9,30,86) glued
}


def profiles(d, present, nd):
    out = []
    for c in itertools.product(*[range(min(d, nd[j] - (j == d)) + 1) for j in present]):
        if sum(c) == d:
            out.append(dict(zip(present, c)))
    return out


def build(n, L):
    nd = dict(zip(D.DEGS, n))
    present = [d for d in D.DEGS if nd[d] > 0]
    e = D.edges(n)
    cols = []          # ("x", d, p, ehv) or ("m", i, j)
    for d in present:
        for p in profiles(d, present, nd):
            Z = sum(j * k for j, k in p.items())
            ehv = e - Z
            if ehv < L.get(d, D.e9(d)) or ehv < D.e9(d) or Z < D.z_min_mtf(d):
                continue
            cols.append(("x", d, p, ehv))
    mvars = [(i, j) for a, i in enumerate(present) for j in present[a:]]
    cols += [("m", i, j) for (i, j) in mvars]
    idx = {("m", i, j): k for k, c in enumerate(cols) if c[0] == "m" for (i, j) in [(c[1], c[2])]}
    A, lo, hi = [], [], []

    def row(coef, l, h):
        r = np.zeros(len(cols))
        for k, v in coef.items():
            r[k] += v
        A.append(r); lo.append(l); hi.append(h)

    for d in present:
        row({k: 1 for k, c in enumerate(cols) if c[0] == "x" and c[1] == d}, nd[d], nd[d])
    for (i, j) in mvars:
        coef = {k: c[2][j] for k, c in enumerate(cols) if c[0] == "x" and c[1] == i}
        coef[idx[("m", i, j)]] = coef.get(idx[("m", i, j)], 0) - (2 if i == j else 1)
        row(coef, 0, 0)
        if i != j:
            coef = {k: c[2][i] for k, c in enumerate(cols) if c[0] == "x" and c[1] == j}
            coef[idx[("m", i, j)]] = -1
            row(coef, 0, 0)
    weights = []
    for r in range(1, len(present) + 1):
        for sub in itertools.combinations(present, r):
            weights.append({d: int(d in sub) for d in present})
    for xs in itertools.product(range(4), repeat=len(present)):
        if max(xs) >= 2:
            weights.append(dict(zip(present, xs)))
    for x in weights:
        tot = sum(x[d] * nd[d] for d in present)
        coef = {idx[("m", i, j)]: x[i] * x[j] for (i, j) in mvars if x[i] * x[j]}
        if coef:
            row(coef, -np.inf, tot * tot // 4)
    # alpha(G[D]) <= 9 for D = vertices of degree < 9: G[D] has >= |D| - e(G[D]) components,
    # one vertex from each is independent, so e(G[D]) >= |D| - 9  (Codex r4, duo)
    low = [d for d in present if d < 9]
    nD = sum(nd[d] for d in low)
    coef = {idx[("m", i, j)]: 1 for (i, j) in mvars if i in low and j in low}
    if coef and nD > 9:
        row(coef, nD - 9, np.inf)
    return cols, np.array(A), np.array(lo), np.array(hi)


def solve(n, L, T=None):
    """T None: feasibility (returns 0 / None).  Else min #9-vertices with e(H_v) <= T."""
    cols, A, lo, hi = build(n, L)
    if not cols or not any(c[0] == "x" for c in cols):
        return None
    cvec = np.zeros(len(cols))
    if T is not None:
        for k, c in enumerate(cols):
            if c[0] == "x" and c[1] == 9 and c[3] <= T:
                cvec[k] = 1
    res = milp(cvec, constraints=LinearConstraint(A, lo, hi), integrality=np.ones(len(cols)),
               bounds=Bounds(0, np.inf), options={"time_limit": 60})
    if res.status == 2:
        return None      # infeasible
    if res.status != 0:
        return "?"
    return int(round(res.fun))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scen", default="sel")
    ap.add_argument("--emin", type=int, default=167)
    ap.add_argument("--Ts", default="91,92,93,94,95,96,97,98")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "out", "mforce.json"))
    a = ap.parse_args()
    L = SCEN[a.scen]
    Ts = [int(t) for t in a.Ts.split(",")]
    rows = []
    with open(os.path.join(os.path.dirname(__file__), "out", "cases_gr_mtf.csv")) as f:
        for r in csv.DictReader(f):
            n = tuple(int(r[k]) for k in ["n4", "n5", "n6", "n7", "n8", "n9"])
            e = D.edges(n)
            if e < a.emin or n[5] == 40:
                continue
            feas = solve(n, L)
            rec = {"n": n, "e": e, "feasible": feas is not None}
            if feas is not None:
                rec["m"] = {T: solve(n, L, T) for T in Ts}
            rows.append(rec)
            print(n, e, rec.get("m", "INFEASIBLE"), flush=True)
    json.dump(rows, open(a.out, "w"), indent=0)
    alive = [r for r in rows if r["feasible"]]
    print(f"{len(rows)} distributions with e >= {a.emin}; profile-ILP feasible: {len(alive)}")
    for T in Ts:
        ms = [r["m"][T] for r in alive if isinstance(r["m"][T], int)]
        if ms:
            print(f"T={T}: min m_T over alive = {min(ms)}, histogram",
                  {k: ms.count(k) for k in sorted(set(ms))})


if __name__ == "__main__":
    main()
