#!/usr/bin/env python3
"""Check the external clauses of an SMS proof (written by lratlog2lrat.py).

Usage: check_ext.py --n N --k K EXT_FILE SYM_JSON [--partition a b c ...] [--blocked G6FILE]

Each external clause must be one of:
  IS   : the positive clause "some pair of S is an edge" for a k-set S (implied by the
         Ramsey formula: no independent k-set);
  SYM  : a symmetry-breaking clause C with a permutation witness pi from SYM_JSON such that
         every graph H that falsifies C satisfies pi(H) < H in ONE fixed total order on
         labelled graphs (checked by the indicator-pair criterion below);
  BLOCK: (with --blocked) the clause that excludes exactly one listed graph.
The fixed order: edge vector in SMS row-wise pair order (0,1),(0,2),...,(1,2),..., compared
lexicographically; a SYM clause forbids H when pi(H) is lex-SMALLER. We test both value orders
(0<1 and 1<0) and require ONE of them to work for ALL SYM clauses (SMS: 0<1, i.e. canonical =
lex-min row-wise edge vector; confirmed independently by cert with VeriPB). If --partition is given, every witness must preserve the vertex partition.

Soundness: the order-minimal graph of each isomorphism class (resp. partition-preserving class)
satisfies every SYM clause. So if the input formula is invariant under these permutations,
input + SYM clauses is equisatisfiable with the input.

Indicator-pair criterion for clause C, witness s (a permutation of vertices), value order <:
alpha = the partial graph falsifying C. For position q (pair p), a_q = H(p), b_q = H(s^-1(p)).
Need t with: alpha forces b_t < a_t, and for all q < t alpha forces b_q <= a_q
(b fixed min, or a fixed max, or same pair). Then s(H) < H for every completion H.
This file does not import any SMS code.
"""
import argparse
import json
from itertools import combinations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("ext")
    ap.add_argument("sym")
    ap.add_argument("--partition", type=int, nargs="*")
    ap.add_argument("--blocked")
    a = ap.parse_args()
    n, k = a.n, a.k
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    var = {p: v for v, p in enumerate(pairs, 1)}
    pair_of = {v: p for p, v in var.items()}
    nedge = len(pairs)

    part = None
    if a.partition:
        assert sum(a.partition) == n
        part = []
        for c, size in enumerate(a.partition):
            part += [c] * size

    # symmetry witnesses keyed by clause literal set
    wit = {}
    with open(a.sym) as f:
        for cl, perm in json.load(f)["sym_clauses"]:
            lits = frozenset((1 if s > 0 else -1) * var[(min(i, j), max(i, j))] for s, i, j in cl)
            wit.setdefault(lits, []).append(perm)

    blocked = set()
    if a.blocked:
        with open(a.blocked) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = [ord(c) - 63 for c in line]
                if d[0] == 63:
                    m, d = (d[1] << 12) | (d[2] << 6) | d[3], d[4:]
                else:
                    m, d = d[0], d[1:]
                assert m == n
                bits = [(x >> s) & 1 for x in d for s in range(5, -1, -1)]
                E = set()
                t = 0
                for j in range(1, n):
                    for i in range(j):
                        if bits[t]:
                            E.add((i, j))
                        t += 1
                blocked.add(frozenset(-var[p] if p in E else var[p] for p in pairs))

    def sym_ok(lits, s, maxval):
        # alpha: value of each pair forced by falsifying the clause
        alpha = {}
        for l in lits:
            alpha[pair_of[abs(l)]] = 0 if l > 0 else 1
        if part is not None and any(part[s[v]] != part[v] for v in range(n)):
            return False
        sinv = [0] * n
        for v in range(n):
            sinv[s[v]] = v
        minval = 1 - maxval
        for p in pairs:
            q = (sinv[p[0]], sinv[p[1]])
            q = (min(q), max(q))
            av, bv = alpha.get(p), alpha.get(q)
            if p == q:
                continue
            if bv == minval and av == maxval:
                return True  # strict at this position
            if bv == minval or av == maxval:
                continue  # b <= a forced
            return False
        return False

    with open(a.ext) as f:
        ext = [[int(x) for x in line.split()[1:-1]] for line in f if line.strip()]

    counts = {"IS": 0, "SYM": 0, "BLOCK": 0}
    syms = []
    bad = []
    for lits in ext:
        if all(l > 0 for l in lits) and len(lits) == k * (k - 1) // 2:
            vs = sorted({v for l in lits for v in pair_of[l]})
            if len(vs) == k and set(lits) == {var[p] for p in combinations(vs, 2)}:
                counts["IS"] += 1
                continue
        fs = frozenset(lits)
        if fs in blocked:
            counts["BLOCK"] += 1
            continue
        if fs in wit:
            syms.append(fs)
            continue
        bad.append(lits)

    good_order = None
    for maxval in (1, 0):
        if all(any(sym_ok(fs, s, maxval) or sym_ok(fs, [s.index(v) for v in range(n)], maxval)
                   for s in wit[fs]) for fs in syms):
            good_order = maxval
            break
    counts["SYM"] = len(syms)
    print(f"external={len(ext)} IS={counts['IS']} SYM={counts['SYM']} BLOCK={counts['BLOCK']} "
          f"unjustified={len(bad)} sym_order={'lex-min, 0<1' if good_order == 1 else 'lex-min, 1<0' if good_order == 0 else 'NONE'}")
    if bad or (syms and good_order is None):
        if bad:
            print("first unjustified clause:", bad[0])
        raise SystemExit(1)
    print("OK")


if __name__ == "__main__":
    main()
