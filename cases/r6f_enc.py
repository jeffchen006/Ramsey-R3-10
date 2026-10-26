"""Batched selector CNFs for sub-case R(6, f* <= 5) of the 9-regular case (notes/cases_local.md Lemma F).

Author: agent `cases`, 2026-10-25.  Batching idea W1 (Wesley, arXiv:2606.17021 Sec 4.4).
Run: tools/venv/bin/python cases/r6f_enc.py --g6 FILE [--batch 1000] [--out DIR] [--first i --last j]

Labelling (Lemma Mc + Lemma F): G 9-regular (3,10,40), every non-adjacent pair has codegree <= 6,
vertex 0 and 10 non-adjacent with codegree 6:
  N(0) = {1..9}, N(10) = {1..6} + {11,12,13};  C = {1..6}, A = {7,8,9}, B = {11,12,13};
  X = V - N[0] - N[10] = {14..39} (26 vertices, alpha <= 7, e(X) = 72 + f, f = e(A,B)).
Base CNF = sms/gen_ramsey.py (triangle-free, degrees = 9, codeg <= 6, N(0) = {1..9}, N(10) & N(0) = {1..6})
plus units for N(10).  Independent 10-sets: lazily by smsg --forbid-independent-set 10, with --no-SMS
(the X block is a fixed labelled graph, so SMS minimality pruning is NOT valid here).
Per batch: one selector s_H per input graph H (on X = 14..39 in graph6 vertex order):
  (-s_H v x_e) for e in E(H), (-s_H v -x_e) for non-edges of H, and (OR_H s_H).
UNSAT of a batch CNF = no G with G[X] isomorphic to any H of the batch (in this labelling).
Implied rows added (all consequences of the base + selectors, added to help CDCL with counting):
  (I1) Hall / Lemma F2: for A' in A, B' in B with |A'| + |B'| = 4, C + A' + B' is a 10-set, so some A'-B' edge.
  (I2) Lemma F1: f = e(A,B) = e(H) - 72 exactly (unary totalizer over the 9 A-B variables; s_H -> count = f).
"""
from itertools import combinations
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N, XOFF, XN = 40, 14, 26


def g6decode(s):
    s = s.strip()
    b = [ord(c) - 63 for c in s]
    n = b[0]
    assert n < 63
    bits = []
    for v in b[1:]:
        for k in range(5, -1, -1):
            bits.append((v >> k) & 1)
    E, t = set(), 0
    for j in range(1, n):
        for i in range(j):
            if bits[t]:
                E.add((i, j))
            t += 1
    return n, E


def check_input(n, E, amax=7):
    """Sanity: n = 26, triangle-free, alpha <= amax (cheap exact check by branching)."""
    adj = [set() for _ in range(n)]
    for i, j in E:
        adj[i].add(j); adj[j].add(i)
    for i, j in E:
        if adj[i] & adj[j]:
            return False

    def alpha(cand):
        if not cand:
            return 0
        v = max(cand, key=lambda u: len(adj[u] & cand))
        if not adj[v] & cand:
            return len(cand)
        return max(1 + alpha(cand - adj[v] - {v}), alpha(cand - {v}))
    return n == XN and alpha(set(range(n))) <= amax


def var(i, j):
    i, j = min(i, j), max(i, j)
    return i * N - i * (i + 1) // 2 + (j - i)    # sms numbering: row-wise upper triangle from 1


def base_cnf(path, k=10):
    edges = "10-11,10-12,10-13"
    nonedges = ",".join(f"10-{j}" for j in range(XOFF, N))
    cmd = [sys.executable, os.path.join(ROOT, "sms", "gen_ramsey.py"), "-n", "40", "-k", str(k),
           "--dmin", "9", "--dmax", "9", "--fix-nbhd", "9", "--codeg-max", "6", "--codeg-pair", "6",
           "--edges", edges, "--nonedges", nonedges, "-o", path]
    subprocess.run(cmd, check=True)
    with open(path) as f:
        hdr = f.readline().split()
        body = f.read()
    return int(hdr[2]), int(hdr[3]), body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g6", required=True)
    ap.add_argument("--batch", type=int, default=1000)
    ap.add_argument("--out", default=os.path.join(ROOT, "runs", "cases", "r6f"))
    ap.add_argument("--first", type=int, default=1, help="first input line (1-based)")
    ap.add_argument("--last", type=int, default=None)
    ap.add_argument("--k", type=int, default=10,
                    help="forbidden independent-set size; k = 11 only for the positive control (no Hall rows)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    nv, nc, body = base_cnf(os.path.join(a.out, "base.cnf"), a.k)
    assert var(0, 1) == 1 and var(38, 39) == N * (N - 1) // 2
    lines = [l for l in open(a.g6) if l.strip() and not l.startswith(">")]
    last = a.last or len(lines)
    lines = lines[a.first - 1:last]
    # (I1) Hall clauses and (I2) unary counter o[1..9] for e(A,B)
    A, B, C = [7, 8, 9], [11, 12, 13], list(range(1, 7))
    hall = []
    for ka in range(1, 4):
        for Ap in combinations(A, ka):
            for Bp in combinations(B, 4 - ka):
                if a.k == 10:
                    hall.append(" ".join(str(var(x, y)) for x in Ap for y in Bp) + " 0")
    ab = [var(x, y) for x in A for y in B]
    # sequential counter: r[i][k] <-> at least k of ab[0..i] are true (full equivalence)
    v0 = nv
    r = {}
    cnt = []
    for i, x in enumerate(ab):
        for k in range(1, i + 2):
            v0 += 1
            r[(i, k)] = v0
            # r(i,k) <-> r(i-1,k) or (r(i-1,k-1) and x)
            prev_k = r.get((i - 1, k))
            prev_k1 = r.get((i - 1, k - 1)) if k > 1 else None
            if prev_k:
                cnt.append(f"{-prev_k} {v0} 0")
            if k == 1:
                cnt.append(f"{-x} {v0} 0")
                cnt.append(f"{-v0} {x}" + (f" {prev_k}" if prev_k else "") + " 0")
            else:
                if prev_k1:
                    cnt.append(f"{-prev_k1} {-x} {v0} 0")
                    cnt.append(f"{-v0} {prev_k1}" + (f" {prev_k}" if prev_k else "") + " 0")
                    cnt.append(f"{-v0} {x}" + (f" {prev_k}" if prev_k else "") + " 0")
                else:
                    cnt.append(f"{-v0} 0")
    o = {k: r[(len(ab) - 1, k)] for k in range(1, len(ab) + 1)}
    extra = hall + cnt
    nv, nc = v0, nc + len(extra)
    body = body + "\n".join(extra) + "\n"
    nb = 0
    for b0 in range(0, len(lines), a.batch):
        chunk = lines[b0:b0 + a.batch]
        cl, sel, v = [], [], nv
        for s in chunk:
            n, E = g6decode(s)
            if not check_input(n, E, a.k - 3):
                sys.exit(f"bad input graph: {s.strip()}")
            v += 1
            sel.append(v)
            f = len(E) - 72
            if f < 0 or f > 9:
                cl.append(f"{-v} 0")
            else:
                if f >= 1:
                    cl.append(f"{-v} {o[f]} 0")
                if f + 1 <= 9:
                    cl.append(f"{-v} {-o[f + 1]} 0")
            for j in range(1, n):
                for i in range(j):
                    lit = var(XOFF + i, XOFF + j)
                    cl.append(f"{-v} {lit if (i, j) in E else -lit} 0")
        cl.append(" ".join(map(str, sel)) + " 0")
        i0 = a.first + b0
        name = os.path.join(a.out, f"b_{i0:07d}_{i0 + len(chunk) - 1:07d}.cnf")
        with open(name, "w") as f:
            f.write(f"p cnf {v} {nc + len(cl)}\n{body}")
            f.write("\n".join(cl) + "\n")
        nb += 1
        print(name, len(chunk), flush=True)
    print(f"{nb} batch CNFs in {a.out}")


if __name__ == "__main__":
    main()
