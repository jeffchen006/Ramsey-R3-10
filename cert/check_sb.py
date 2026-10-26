#!/usr/bin/env python3
"""cert/check_sb.py - independent re-check of lex symmetry-breaking clauses.

Written by agent `cert`. Shares no code with sb.py (positions and the edge
variable map are re-derived here).

Input file: one SB clause per line:  "<DIMACS literals> 0 | <pi(0)> ... <pi(n-1)>"
For each line, with alpha = the partial assignment that falsifies the clause,
check: pi is a permutation of 0..n-1, alpha is consistent, and for EVERY total
assignment x extending alpha, val(pi x) > val(x) (--better max, default) or
val(pi x) < val(x) (--better min, the SMS order), where
    val(x) = sum_k 2^(N-k) x_{p_k},  p_1..p_N = edges in row-major order
    (or colex order with --positions colex),
    (pi x)_{p} = x_{pi^-1(p)}.
Exact test: D(x) = val(x) - val(pi x) is linear in the free variables, so its
maximum over all completions is const + sum of positive coefficients
(big integers, no rounding).

Meta-lemma (hand proof, see notes/cert_design.md): if every SB clause passes,
the lex-largest relabelling of any graph satisfies all of them; the Ramsey
formula is closed under relabelling; so adding the clauses keeps satisfiability.
Usage: check_sb.py --n N --order colex|rowmajor FILE
"""
import argparse
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--order", default="colex")
    ap.add_argument("--better", default="max", choices=["max", "min"])
    ap.add_argument("--positions", default="rowmajor", choices=["rowmajor", "colex"],
                    help="order of the lex comparison (MathCheck CAS: colex)")
    ap.add_argument("--allow-empty", action="store_true", help="a file with no SB clause is OK")
    ap.add_argument("file")
    a = ap.parse_args()
    n = a.n
    sign = 1 if a.better == "max" else -1
    edges_rm = [(i, j) for i in range(n) for j in range(i + 1, n)]
    vid_list = list(edges_rm)
    if a.positions == "colex":
        edges_rm = [(i, j) for j in range(n) for i in range(j)]
    if a.order == "colex":
        vid = {(i, j): j * (j - 1) // 2 + i + 1 for (i, j) in edges_rm}
    else:
        vid = {e: k + 1 for k, e in enumerate(vid_list)}
    edge_of = {v: e for e, v in vid.items()}

    bad = 0
    total = 0
    for lineno, line in enumerate(open(a.file), 1):
        if not line.strip() or line.startswith("c"):
            continue  # blank or comment / header line ("c order ...")
        total += 1
        left, right = line.split("|")
        lits = [int(t) for t in left.split()]
        pi = [int(t) for t in right.split()]
        ok = lits and lits[-1] == 0 and sorted(pi) == list(range(n))
        alpha = {}
        if ok:
            for l in lits[:-1]:
                e = edge_of.get(abs(l))
                if e is None:
                    ok = False
                    break
                val = 0 if l > 0 else 1  # alpha falsifies the clause
                if alpha.get(e, val) != val:
                    ok = False
                    break
                alpha[e] = val
        if ok:
            # D(x) = val(x) - val(pi x) is linear in x. The clause is valid iff
            # max over completions of sign*D(x) < 0 (pi x strictly better).
            pinv = [0] * n
            for v, w in enumerate(pi):
                pinv[w] = v
            N = len(edges_rm)
            const = 0
            coef = {}
            for k, (i, j) in enumerate(edges_rm):
                u, w = pinv[i], pinv[j]
                q = (u, w) if u < w else (w, u)
                c = sign * (1 << (N - 1 - k))
                for e, sg in (((i, j), 1), (q, -1)):
                    if e in alpha:
                        const += sg * c * alpha[e]
                    else:
                        coef[e] = coef.get(e, 0) + sg * c
            ok = const + sum(c for c in coef.values() if c > 0) < 0
        if not ok:
            bad += 1
            if bad <= 10:
                print("BAD line %d: %s" % (lineno, line.strip()))
    print("checked %d SB clauses, n=%d order=%s better=%s: %d bad" % (total, n, a.order, a.better, bad))
    if bad or (total == 0 and not a.allow_empty):
        print("RESULT: FAIL")
        sys.exit(1)
    print("RESULT: OK")


if __name__ == "__main__":
    main()
