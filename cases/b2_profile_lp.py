#!/usr/bin/env python3
"""B2 test: LP over the independent-set profile of a 9-regular (3,10,40)-graph (case R).

Variables: I_s = number of independent s-sets (s = 1..10); p[s][m] = number of independent
s-sets S with |X_S| = m, X_S = V - S - N(S).  Valid constraints (proofs in notes/cases.md Sec 6):
 (a) sum_m p[s][m] = I_s
 (b) sum_m m p[s][m] = (s+1) I_{s+1}          (each independent (s+1)-set counted s+1 times)
 (c) sum_m p[s][m] lo(s,m) <= C(s+2,2) I_{s+2} <= sum_m p[s][m] hi(s,m)
     with lo/hi = bounds on I_2(X_S) = C(m,2) - e(X_S):
     e(X_S) >= e(3,10-s,m)            ([GR] Table 3/4 via cases/etables.py)
     e(X_S) = 9m + 9s - 180 + f_S      (9-regular identity), 0 <= f_S <= fmax(40-s-m)
     e(X_S) <= min(m^2/4, m(9-s)/2)    (Mantel; max degree <= alpha(X_S) <= 9-s)
     fmax(n) = min(n^2/4, 4n)          (G[N(S)] triangle-free; each vertex of N(S) has a
                                        neighbour in S, so at most 8 neighbours inside N(S))
     p[s][m] = 0 if the e(X_S) interval is empty or m >= R(3,10-s).
 (d) I_1 = 40, I_2 = 600, I_3 = 4480 (9-regular, triangle-free), I_10 = 0, I_9 >= 40, p[1][30] = 40.
Prints whether the LP is feasible, and the min/max of I_s.
"""
import os
import sys
from math import comb

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, os.path.dirname(__file__))
from etables import e3

R = {3: 6, 4: 9, 5: 14, 6: 18, 7: 23, 8: 28, 9: 36, 10: 41}


def ebounds(s, m):
    k = 10 - s
    if s == 9:
        return (0, 0) if m == 0 else None
    if s == 8:                       # alpha(X) <= 1 and triangle-free: X empty, K1 or K2
        if m > 2:
            return None
        e = comb(m, 2)
        n = 40 - s - m
        return (e, e) if 9 * m + 9 * s - 180 <= e <= 9 * m + 9 * s - 180 + min(n * n // 4, 4 * n) else None
    if m >= R[k]:
        return None
    lb = e3(k, m)
    if lb is None:
        return None
    lo = max(lb, 9 * m + 9 * s - 180)
    n = 40 - s - m
    if n < 0:
        return None
    fmax = min(n * n // 4, 4 * n)
    hi = min(m * m // 4, m * (9 - s) // 2, 9 * m + 9 * s - 180 + fmax)
    if s == 1:
        lo = hi = 9 * m + 9 - 180          # N(v) independent: f = 0
    return (lo, hi) if lo <= hi else None


def main():
    # optional caps: --cap s:m  forbids independent s-sets with |X_S| >= m
    caps = {}
    for a in sys.argv[1:]:
        if a.startswith("--cap"):
            continue
        if ":" in a:
            ss, mm = a.split(":"); caps[int(ss)] = int(mm)
    idx = {}
    def var(key):
        if key not in idx:
            idx[key] = len(idx)
        return idx[key]
    for s in range(1, 11):
        var(("I", s))
    allowed = {}
    for s in range(1, 10):
        allowed[s] = {}
        for m in range(0, 41):
            b = ebounds(s, m)
            if s in caps and m >= caps[s]:
                b = None
            if b is not None:
                allowed[s][m] = b
                var(("p", s, m))
    A_eq, b_eq, A_ub, b_ub = [], [], [], []
    def row():
        return np.zeros(len(idx))
    for s in range(1, 10):
        r = row()
        for m in allowed[s]:
            r[idx[("p", s, m)]] = 1
        r[idx[("I", s)]] = -1
        A_eq.append(r); b_eq.append(0)
        r = row()
        for m in allowed[s]:
            r[idx[("p", s, m)]] = m
        r[idx[("I", s + 1)]] = -(s + 1)
        A_eq.append(r); b_eq.append(0)
        if s + 2 <= 10:
            lo = row(); hi = row()
            for m, (elo, ehi) in allowed[s].items():
                lo[idx[("p", s, m)]] = comb(m, 2) - ehi     # I_2(X) >= C(m,2) - e_max
                hi[idx[("p", s, m)]] = comb(m, 2) - elo
            lo[idx[("I", s + 2)]] = -comb(s + 2, 2)
            hi[idx[("I", s + 2)]] = -comb(s + 2, 2)
            A_ub.append(lo); b_ub.append(0)                 # sum lo*p - C I <= 0
            A_ub.append(-hi); b_ub.append(0)                # C I - sum hi*p <= 0
    for s, val in ((1, 40), (2, 600), (3, 4480), (10, 0)):
        r = row(); r[idx[("I", s)]] = 1
        A_eq.append(r); b_eq.append(val)
    r = row(); r[idx[("I", 9)]] = -1
    A_ub.append(r); b_ub.append(-40)
    if ("p", 1, 30) in idx:
        r = row(); r[idx[("p", 1, 30)]] = 1
        A_eq.append(r); b_eq.append(40)
    for s in range(1, 10):
        print(f"s={s}: allowed m = {sorted(allowed[s])}")
    for s in range(4, 10):
        for sense in (1, -1):
            c = row(); c[idx[("I", s)]] = sense
            res = linprog(c, A_ub=np.array(A_ub), b_ub=b_ub, A_eq=np.array(A_eq), b_eq=b_eq,
                          bounds=[(0, None)] * len(idx), method="highs")
            if res.status != 0:
                print("LP status", res.status, res.message, "caps", caps)
                return
            print(f"I_{s} {'min' if sense == 1 else 'max'} = {sense * res.fun:.1f}")


if __name__ == "__main__":
    main()
