#!/usr/bin/env python3
"""t9 tables for custom gluing sets U (request of `gluing`), MTF or all-G distributions.
Reuses degseq.build_lp / lp_infeasible_certified unchanged (exact Farkas certificates).
t9(n, U) = least T in 85..99 such that "every 9-vertex has e(H_v) >= T+1 and every d-vertex
(d <= 8) has e(H_v) >= U[d]+1" is LP-infeasible with certificate.  Monotone in T, so binary
search.  9-regular n gets 99 (Theorem A).
Usage: tools/venv/bin/python cases/t9_scan.py [--all-g] OUT.json
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import degseq as D


def t9_bisect(n, U, mtf):
    if n == (0, 0, 0, 0, 0, 40):
        return 99
    L = {d: max(D.e9(d), U.get(d, -1) + 1) for d in D.DEGS}
    if n[5] == 0:
        return 85 if D.lp_infeasible_certified(n, L, mtf) else None
    lo, hi = 85, 99          # answer in [lo, hi]; hi = 99 always certifiable? check
    L[9] = 100
    if not D.lp_infeasible_certified(n, L, mtf):
        return None
    while lo < hi:
        mid = (lo + hi) // 2
        L[9] = mid + 1
        if D.lp_infeasible_certified(n, L, mtf):
            hi = mid
        else:
            lo = mid + 1
    return lo


def main():
    allg = "--all-g" in sys.argv
    out = [a for a in sys.argv[1:] if not a.startswith("--")][0]
    tag = "gr" if allg else "gr_mtf"
    rows = json.load(open(os.path.join(os.path.dirname(__file__), "out", f"degseq_{tag}.json")))
    dists = [tuple(r["n"]) for r in rows["survivors"]]
    mtf = not allg
    grid = []
    for u8, u7 in itertools.product((96, 97, 98, 99, 100), (103, 108, 110, 112)):
        grid.append({8: u8, 7: u7, 6: 121, 5: 130, 4: 140})
    res = {"tag": tag, "scenarios": []}
    for U in grid:
        t = {str(list(n)): t9_bisect(n, U, mtf) for n in dists}
        hist = {}
        for v in t.values():
            hist[str(v)] = hist.get(str(v), 0) + 1
        res["scenarios"].append({"U": {str(k): v for k, v in U.items()}, "t9": t, "hist": hist})
        print(f"U8<={U[8]} U7<={U[7]} U6<=121: {dict(sorted(hist.items()))}", flush=True)
        json.dump(res, open(out, "w"))
    D.CERTS and json.dump(D.CERTS, open(out.replace(".json", "_certs.json"), "w"))


if __name__ == "__main__":
    main()
