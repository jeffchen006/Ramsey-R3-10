#!/usr/bin/env python3
"""Degree distributions and gluing cases for a hypothetical (3,10,40)-graph G.

Author: agent `cases` (R(3,10) team), 2026-10-24.  Proofs: notes/cases.md.
Run with:  tools/venv/bin/python cases/degseq.py [--self-e] [--out DIR]

G: 40 vertices, triangle-free, alpha(G) <= 9.  n_d = #vertices of degree d.
H_v = G - N[v];  Z(v) = sum_{u in N(v)} d(u);  e(H_v) = e(G) - Z(v).

A degree distribution is n = (n4, n5, n6, n7, n8, n9), sum 40 (Lemma L1: 4 <= d <= 9).
Every check below is a NECESSARY condition, proved in notes/cases.md (lemma name in
brackets).  A distribution that fails one check cannot occur.  The LP check
(check_class_lp) removes a distribution only when an exact rational Farkas
certificate was verified with fractions.Fraction; a float LP result alone never
removes anything.

Numbers from the literature (lit confirmed the reading, see notes/edge_tables.md):
  E9[m]   = e(3,9,m)    [GR] = Goedgebeur-Radziszowski, EJC 20(1) #P30, Tables 3,4, Thm 3.
  E8[m]   = e(3,8,m)    [GR] Table 3.
  E10_40  = 161 <= e(3,10,40)  [GR] Table 5 (lower bound; uses GR's gluing runs).
  COUNT9  = |R(3,9,m,e)| [GR] Table 14 and [Ang] = Angeltveit arXiv:2401.00392 Sec 3.3.
"""
import argparse
import itertools
import json
import os
import sys
from fractions import Fraction
from math import comb

import numpy as np
from scipy.optimize import linprog

N_VERT = 40
DEGS = (4, 5, 6, 7, 8, 9)
E9 = {30: 86, 31: 95, 32: 104, 33: 118, 34: 129, 35: 140}   # [GR] Tables 3,4; Thm 3
E8 = {22: 42, 23: 49, 24: 56, 25: 65, 26: 73, 27: 85}       # [GR] Table 3
E10_40_GR = 161                                               # [GR] Table 5
E10_40_SELF = 159                                             # Lemma L5 (from (4) only)

# Exact graph counts |R(3,9,m,e)| that are known COMPLETE ([GR] Table 14, [Ang] 3.3).
COUNT9 = {
    (30, 86): 1800, (30, 87): 147335,
    (31, 95): 560, (31, 96): 35154,
    (32, 104): 39, (32, 105): 952, (32, 106): 18598, (32, 107): 234681, (32, 108): 2104151,
    (33, 118): 5, (33, 119): 69,
    (34, 129): 1, (34, 130): 4,
    (35, 140): 1,
}
COUNT9_CUM = {(32, 112): 1554928360, (33, 121): 14395, (34, 130): 5, (35, 140): 1}  # [Ang]


def e9(d):
    """Lower bound e(3,9,39-d) on e(H_v) for d(v) = d (Lemma L3)."""
    return E9[39 - d]


def edges(n):
    s = sum(d * k for d, k in zip(DEGS, n))
    return s // 2


def deficiency(n):
    """N = sum_v (9 - d(v)) = 360 - 2 e(G)."""
    return sum((9 - d) * k for d, k in zip(DEGS, n))


# --------------------------------------------------------------------------------------
# Simple checks.  Each returns True if the distribution PASSES (is not excluded).
# --------------------------------------------------------------------------------------

def check_parity(n, ctx):
    """[L0] Handshake: sum_d d*n_d = 2 e(G) is even."""
    return sum(d * k for d, k in zip(DEGS, n)) % 2 == 0


def check_edge_bounds(n, ctx):
    """[L5] e_lb <= e(G) <= 180.  e_lb = 161 ([GR] Table 5) or 159 (Lemma L5, --self-e).
    Upper bound: Delta <= 9 (Lemma L1)."""
    e = edges(n)
    return ctx["e_lb"] <= e <= 180


def check_gr_sum(n, ctx):
    """[L4] GR inequality (4): sum_v e(H_v) = 40 e - sum d^2 = sum_d n_d d(20-d), and
    e(H_v) >= e(3,9,39-d).  So sum_d n_d (d(20-d) - e(3,9,39-d)) >= 0."""
    return sum(k * (d * (20 - d) - e9(d)) for d, k in zip(DEGS, n)) >= 0


def check_low_degree(n, ctx):
    """[L6] Pair lemma: non-adjacent u,v have |N(u) & N(v)| <= d(u)+d(v)-11.
    Hence u,v with d(u)+d(v) <= 10 are adjacent.  Consequences:
      (a) vertices of degree <= 5 are pairwise adjacent, so n4 + n5 <= 2;
      (b) a degree-4 vertex is adjacent to every other vertex of degree <= 6,
          so n4 >= 1 implies (n4 - 1) + n5 + n6 <= 4;
      (c) n4 = 2 implies n6 = 0 (a 6-vertex would be adjacent to both 4-vertices,
          which are adjacent: triangle)."""
    n4, n5, n6 = n[0], n[1], n[2]
    if n4 + n5 > 2:
        return False
    if n4 >= 1 and (n4 - 1) + n5 + n6 > 4:
        return False
    if n4 == 2 and n6 > 0:
        return False
    return True


def deg4_neighbour_multisets(ctx):
    """[L7] If d(u) = 4: H_u is the unique (3,9,35)-graph (8-regular, 140 edges, [GR] Thm 3).
    Let N(u) = {x1..x4}, d_i = d(x_i).  Every y in H_u has d(y) = 8 + |N(y) & N(u)| <= 9,
    so the sets S_i = N(x_i) - u are disjoint; then
      n9 = sum(d_i - 1) + #{i: d_i = 9},  n8 = 35 - sum(d_i - 1) + #{i: d_i = 8},
      n_d = [d = 4] + #{i: d_i = d}  for d <= 7,     e(G) = 140 + sum d_i.
    x_i, x_j are non-adjacent with exactly one common neighbour (u), so by the pair
    lemma d_i + d_j >= 12.  Returns the set of possible distributions."""
    out = {}
    for ds in itertools.combinations_with_replacement(DEGS, 4):
        if any(a + b < 12 for a, b in itertools.combinations(ds, 2)):
            continue
        if 140 + sum(ds) < ctx["e_lb"]:
            continue
        s1 = sum(d - 1 for d in ds)
        cnt = {d: ds.count(d) for d in DEGS}
        n = [0] * 6
        n[0] = 1 + cnt[4]
        n[1], n[2], n[3] = cnt[5], cnt[6], cnt[7]
        n[4] = 35 - s1 + cnt[8]
        n[5] = s1 + cnt[9]
        out.setdefault(tuple(n), []).append(ds)
    return out


def check_deg4_structure(n, ctx):
    """[L7] If n4 >= 1 the distribution must come from a neighbour multiset of a
    degree-4 vertex (see deg4_neighbour_multisets)."""
    if n[0] == 0:
        return True
    return tuple(n) in ctx["deg4_dists"]


def z_min_mtf(d):
    """[M2] MTF G: Z(v) >= d^2 - 11d + 78 for d(v) = d (proof in notes/cases.md)."""
    return d * d - 11 * d + 78


def check_mtf_min_degree(n, ctx):
    """[M1] MTF G (only with --mtf): delta >= 6, so n4 = n5 = 0."""
    if not ctx.get("mtf"):
        return True
    return n[0] == 0 and n[1] == 0


def check_min_Z(n, ctx):
    """[L3'] Per vertex: Z(v) <= e(G) - e(3,9,39-d(v)) (Lemmas L2, L3), and Z(v) is at
    least the sum of the d(v) smallest degrees among the OTHER 39 vertices.
    With --mtf also Z(v) >= d^2 - 11d + 78 [M2]."""
    e = edges(n)
    pool = [d for d, k in zip(DEGS, n) for _ in range(k)]   # sorted ascending
    for d, k in zip(DEGS, n):
        if k == 0:
            continue
        others = list(pool)
        others.remove(d)
        zmin = sum(others[:d])
        if ctx.get("mtf"):
            zmin = max(zmin, z_min_mtf(d))
        if zmin > e - e9(d):
            return False
    return True


# --------------------------------------------------------------------------------------
# Class-level LP with exact certificate  [L8]
# --------------------------------------------------------------------------------------
# Variables m_ij (i <= j, both degree classes present) = #edges between class i and j.
# M_ij = m_ij (i != j), M_ii = 2 m_ii   (ordered adjacent pairs, first end in class i).
# Valid constraints (all proved in notes/cases.md, Lemma L8):
#   deg_i     : sum_j M_ij = i n_i
#   hyp_i     : sum_j j M_ij <= n_i (e - L_i)        (every v in class i has e(H_v) >= L_i)
#   mantel_x  : sum_{i<=j} x_i x_j m_ij <= floor((sum_i x_i n_i)^2 / 4)   (Motzkin-Straus)
#   ub_ij     : m_ij <= n_i * min(i, n_j)  (i<j);  m_ii <= floor(n_i^2/4)
#   forced_ij : m_ij >= full count when i + j <= 10   (Lemma L6)

def build_lp(n, L, forced_max=10, mtf=False):
    """Return (vars, rows) with rows = list of (coef dict, rhs) meaning coef.x <= rhs."""
    present = [d for d, k in zip(DEGS, n) if k > 0]
    nd = dict(zip(DEGS, n))
    e = edges(n)
    var = [(i, j) for a, i in enumerate(present) for j in present[a:]]
    rows = []

    def M(i, j):  # coefficient dict for M_ij
        if i == j:
            return {(i, i): 2}
        return {(min(i, j), max(i, j)): 1}

    for i in present:
        c = {}
        for j in present:
            for k, v in M(i, j).items():
                c[k] = c.get(k, 0) + v
        rows.append((dict(c), i * nd[i], "deg_eq_le"))
        rows.append(({k: -v for k, v in c.items()}, -i * nd[i], "deg_eq_ge"))
        c = {}
        for j in present:
            for k, v in M(i, j).items():
                c[k] = c.get(k, 0) + j * v
        rows.append((c, nd[i] * (e - L[i]), f"hyp_{i}"))
        if mtf:
            rows.append(({k: -v for k, v in c.items()}, -nd[i] * z_min_mtf(i), f"mtfZ_{i}"))
    # Mantel / Motzkin-Straus families
    weights = []
    for r in range(1, len(present) + 1):
        for sub in itertools.combinations(present, r):
            weights.append({d: (1 if d in sub else 0) for d in present})
    weights.append({d: 9 - d for d in present})
    weights.append({d: 10 - d for d in present})
    weights.append({d: (9 - d) ** 2 for d in present})
    # all integer weights in {0..3} per class (critic K3); duplicates are harmless
    for xs in itertools.product(range(4), repeat=len(present)):
        if max(xs) >= 2:
            weights.append(dict(zip(present, xs)))
    for x in weights:
        tot = sum(x[d] * nd[d] for d in present)
        c = {}
        for (i, j) in var:
            w = x[i] * x[j]
            if w:
                c[(i, j)] = w
        if c:
            rows.append((c, tot * tot // 4, "mantel"))
    ub = {}
    for (i, j) in var:
        if i == j:
            ub[(i, j)] = nd[i] * nd[i] // 4
        else:
            ub[(i, j)] = min(nd[i] * min(i, nd[j]), nd[j] * min(j, nd[i]))
        rows.append(({(i, j): 1}, ub[(i, j)], "ub"))
    for (i, j) in var:
        if i + j <= forced_max:
            full = comb(nd[i], 2) if i == j else nd[i] * nd[j]
            rows.append(({(i, j): -1}, -full, "forced"))
    return var, rows, ub


CERTS = []   # verified Farkas certificates (written to out/certs_<tag>.json)


def lp_infeasible_certified(n, L, mtf=False):
    """True iff the class LP is infeasible AND an exact Farkas certificate verifies.
    Certificate: y >= 0 with  min_{0<=x<=ub} y^T A x  >  y^T b  (exact rationals)."""
    var, rows, ub = build_lp(n, L, mtf=mtf)
    idx = {v: k for k, v in enumerate(var)}
    A = np.zeros((len(rows), len(var)))
    b = np.zeros(len(rows))
    for r, (c, rhs, _) in enumerate(rows):
        for k, v in c.items():
            A[r, idx[k]] = v
        b[r] = rhs
    res = linprog(np.zeros(len(var)), A_ub=A, b_ub=b, bounds=[(0, None)] * len(var),
                  method="highs")
    if res.status == 0:
        return False
    # Farkas: min b.y  s.t. A^T y >= 0, 0 <= y <= 1
    far = linprog(b, A_ub=-A.T, b_ub=np.zeros(len(var)), bounds=[(0, 1)] * len(rows),
                  method="highs")
    if far.status != 0 or far.fun > -1e-9:
        return False
    y = [max(Fraction(0), Fraction(float(t)).limit_denominator(10 ** 6)) for t in far.x]
    ok = verify_farkas(var, rows, ub, y)
    if ok:
        CERTS.append({"n": list(n), "L": {str(k): v for k, v in L.items()}, "mtf": mtf,
                      "y": {str(r): str(t) for r, t in enumerate(y) if t}})
    return ok


def verify_farkas(var, rows, ub, y):
    """Exact check: for all x in box [0,ub], sum_r y_r (A_r x) >= min_box > y.b,
    contradicting A x <= b (which implies y^T A x <= y^T b since y >= 0)."""
    if any(t < 0 for t in y):
        return False
    yb = sum(yr * rhs for yr, (_, rhs, _) in zip(y, rows))
    col = {v: Fraction(0) for v in var}
    for yr, (c, _, _) in zip(y, rows):
        if yr:
            for k, v in c.items():
                col[k] += yr * v
    min_box = sum(min(Fraction(0), col[v]) * ub[v] for v in var)
    return min_box > yb


def base_L(n):
    return {d: e9(d) for d in DEGS}


def check_class_lp(n, ctx):
    """[L8] Class-level LP (see build_lp) with L_i = e(3,9,39-i) must be feasible."""
    return not lp_infeasible_certified(n, base_L(n), ctx.get("mtf", False))


CHECKS = [check_parity, check_edge_bounds, check_mtf_min_degree, check_gr_sum, check_low_degree,
          check_deg4_structure, check_min_Z, check_class_lp]


# --------------------------------------------------------------------------------------
# Gluing cases  [L9, L10]
# --------------------------------------------------------------------------------------
# Scenario U: for d <= 8, assume the gluing team has shown that no (3,10,40)-graph has a
# vertex v of degree d with H_v in R(3,9,39-d, e <= U[d]).  Then every d-vertex has
# e(H_v) >= U[d] + 1.  t9(n, U) = least T such that "every 9-vertex has e(H_v) >= T+1"
# is LP-infeasible; so some 9-vertex has H_v in R(3,9,30, e <= t9).  t9 = 85 means the
# distribution is killed by the gluing in U alone.

SCENARIOS = {
    "none": {},                                         # no gluing of D-vertices
    "U8": {8: 96},                                      # 35,714 graphs ([GR] T14)
    "known": {8: 96, 7: 108, 6: 119, 5: 130, 4: 140},   # all complete sets in [GR] T14
    "ang": {8: 96, 7: 112, 6: 121, 5: 130, 4: 140},     # + [Ang] censuses
}


def t9_star(n, U, mtf=False):
    L = {d: max(e9(d), U.get(d, -1) + 1) for d in DEGS}
    if n[5] == 0:
        return 85 if lp_infeasible_certified(n, L, mtf) else None
    for T in range(85, 100):
        L[9] = T + 1
        if lp_infeasible_certified(n, L, mtf):
            return T
    return None  # should not happen for non-regular n (Lemma L9)


def compositions(total, parts):
    """All tuples of `parts` non-negative integers with the given sum."""
    if parts == 1:
        yield (total,)
        return
    for a in range(total + 1):
        for rest in compositions(total - a, parts - 1):
            yield (a,) + rest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-e", action="store_true",
                    help="use e(G) >= 159 (self-proved) instead of 161 ([GR] Table 5)")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "out"))
    ap.add_argument("--no-cases", action="store_true")
    ap.add_argument("--mtf", action="store_true",
                    help="restrict to maximal triangle-free G (lossless for existence, Lemma M0)")
    args = ap.parse_args()
    ctx = {"e_lb": E10_40_SELF if args.self_e else E10_40_GR, "mtf": args.mtf}
    ctx["deg4_dists"] = deg4_neighbour_multisets(ctx)
    os.makedirs(args.out, exist_ok=True)

    killed = {c.__name__: 0 for c in CHECKS}
    survivors = []
    total = 0
    for n in compositions(N_VERT, 6):
        total += 1
        for c in CHECKS:
            if not c(n, ctx):
                killed[c.__name__] += 1
                break
        else:
            survivors.append(n)
    tag = ("self" if args.self_e else "gr") + ("_mtf" if args.mtf else "")
    print(f"e_lb = {ctx['e_lb']}; distributions with sum 40: {total}")
    for k, v in killed.items():
        print(f"  removed by {k:22s}: {v}")
    print(f"  survivors: {len(survivors)}")

    rows = []
    for n in survivors:
        r = {"n": list(n), "e": edges(n), "N": deficiency(n)}
        if not args.no_cases:
            for s, U in SCENARIOS.items():
                r["t9_" + s] = t9_star(n, U, args.mtf) if n != (0, 0, 0, 0, 0, 40) else 99
        rows.append(r)
    with open(os.path.join(args.out, f"certs_{tag}.json"), "w") as f:
        json.dump(CERTS, f)
    with open(os.path.join(args.out, f"degseq_{tag}.json"), "w") as f:
        json.dump({"e_lb": ctx["e_lb"], "removed": killed, "survivors": rows}, f, indent=0)
    if not args.no_cases:
        for s in SCENARIOS:
            hist = {}
            for r in rows:
                hist[r["t9_" + s]] = hist.get(r["t9_" + s], 0) + 1
            print(f"  scenario {s:6s}: t9 histogram {dict(sorted(hist.items(), key=str))}")


if __name__ == "__main__":
    main()
