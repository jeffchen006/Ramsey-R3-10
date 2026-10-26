#!/usr/bin/env python3
"""Re-verify the Farkas certificates written by degseq.py, in exact arithmetic.
Each certificate says: the class LP build_lp(n, L, mtf) has no solution, so no
(3,10,40)-graph has degree distribution n with every degree-i vertex v satisfying
e(H_v) >= L[i].  Usage: tools/venv/bin/python cases/verify_certs.py cases/out/certs_gr.json"""
import json, os, sys
from fractions import Fraction
sys.path.insert(0, os.path.dirname(__file__))
import degseq as D

certs = json.load(open(sys.argv[1]))
bad = 0
for c in certs:
    L = {int(k): v for k, v in c["L"].items()}
    var, rows, ub = D.build_lp(tuple(c["n"]), L, mtf=c["mtf"])
    y = [Fraction(0)] * len(rows)
    for r, t in c["y"].items():
        y[int(r)] = Fraction(t)
    if not D.verify_farkas(var, rows, ub, y):
        bad += 1
        print("FAILED", c["n"], c["L"])
print(f"{len(certs)} certificates, {bad} failed")
