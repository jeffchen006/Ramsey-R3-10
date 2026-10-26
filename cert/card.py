#!/usr/bin/env python3
"""cert/card.py - VeriPB derivation of satcore's totalizer cardinality encoding.

Written by agent `cert` (critic finding X5). Design: notes/cert_design.md sec. 3.7.
The input (core) contains the bound as a PB constraint, e.g. sum x >= lo, sum x <= hi.
satcore (ramsey.hpp: cardinality/totalizer) builds a tree; node outputs
O[i] <-> (number of true leaves under the node >= i+1), i < m = min(|A|+|B|, cap).
Derivation per internal node (children first):
  red  (i+1) ~O_i + sum_S x >= i+1            : O_i -> 0     (O_i -> count >= i+1)
  red  (L-i) O_i + sum_S ~x >= L-i            : O_i -> 1     (count >= i+1 -> O_i)
then every satcore clause of the node by `pol` (sum of child/parent definitions and
literal axioms; the sum is ">= 1" over exactly the clause literals) and `rup` with
that hint; the units O[lo-1], ~O[hi] by `pol` with the input bound. Helpers are
deleted (`deld`). Leaf "outputs" are the input literals themselves (no aux).
"""
import sb


class Node:
    def __init__(self, leaves, outs, left=None, right=None):
        self.leaves, self.outs, self.left, self.right = leaves, outs, left, right


def build(lits, lo, hi, cap, nxt):
    """Replicates satcore's totalizer(lits, lo, hi, cap). nxt: [maxvar]. Returns (node, clauses)."""
    if hi - lo == 1:
        return Node([lits[lo]], [lits[lo]]), []
    mid = (lo + hi) // 2
    A, ca = build(lits, lo, mid, cap, nxt)
    B, cb = build(lits, mid, hi, cap, nxt)
    m = min(len(A.outs) + len(B.outs), cap)
    O = []
    for _ in range(m):
        nxt[0] += 1
        O.append(nxt[0])
    node = Node(A.leaves + B.leaves, O, A, B)
    cl = []
    na, nb = len(A.outs), len(B.outs)
    for a in range(na + 1):
        for b in range(nb + 1):
            if a + b >= 1:
                c = ([-A.outs[a - 1]] if a else []) + ([-B.outs[b - 1]] if b else []) + [O[min(a + b, m) - 1]]
                if a + b <= m:
                    cl.append(("up", a, b, c))
            if a + b < m:
                c = ([A.outs[a]] if a < na else []) + ([B.outs[b]] if b < nb else []) + [-O[a + b]]
                cl.append(("down", a, b, c))
    node.clauses = cl
    return node, ca + cb + [c for _, _, _, c in cl]


def cardinality(lits, lo, hi, maxvar):
    """Replicates satcore's cardinality(): returns (root, clauses in satcore order, maxvar, lo, hi)."""
    cap = max(hi + 1, lo)
    if cap > len(lits):
        cap = len(lits)
    if hi >= len(lits):
        hi = -1
    if lo <= 0 and hi < 0:
        return None, [], maxvar, lo, hi
    nxt = [maxvar]
    root, cls = build(lits, 0, len(lits), cap, nxt)
    if lo > 0:
        cls.append([root.outs[lo - 1]])
    if hi >= 0:
        cls.append([-root.outs[hi]])
    return root, cls, nxt[0], lo, hi


def lit(l):
    return ("~x%d" % -l) if l < 0 else ("x%d" % l)


def pb(terms, rhs):
    return " ".join("%d %s" % (c, lit(l)) for c, l in terms) + " >= %d" % rhs


def derive(P, root, lo, hi, lo_label=None, hi_label=None):
    """Append the derivation to P (codish.Proof). lo_label / hi_label: labels of
    the input PB constraints sum x >= lo, sum ~x >= L - hi. Returns labels of the
    kept clauses in satcore order."""
    keep = []
    up_def, down_def = {}, {}  # (node id, i) -> label

    def defs(node):
        if node.left is None:
            return
        defs(node.left)
        defs(node.right)
        L = len(node.leaves)
        for i, o in enumerate(node.outs):
            up_def[(id(node), i)] = P.add("red %s : x%d -> 0 ;" % (
                pb([(i + 1, -o)] + [(1, x) for x in node.leaves], i + 1), o))
            down_def[(id(node), i)] = P.add("red %s : x%d -> 1 ;" % (
                pb([(L - i, o)] + [(1, -x) for x in node.leaves], L - i), o))
        helpers = []
        for kind, a, b, c in node.clauses:
            parts = []
            m = len(node.outs)
            if kind == "up":
                # count_A >= a, count_B >= b  ->  O[k-1], k = min(a+b, m)
                k = min(a + b, m)
                for child, t in ((node.left, a), (node.right, b)):
                    if t and child.left is not None:
                        parts.append(up_def[(id(child), t - 1)])
                    elif not t:
                        parts.extend(lit(x) for x in child.leaves)  # literal axioms x >= 0
                parts.append(down_def[(id(node), k - 1)])
            else:
                # count_A <= a, count_B <= b  ->  not O[a+b]
                for child, t in ((node.left, a), (node.right, b)):
                    if t < len(child.outs) and child.left is not None:
                        parts.append(down_def[(id(child), t)])
                    elif t >= len(child.outs):
                        parts.extend(lit(-x) for x in child.leaves)
                parts.append(up_def[(id(node), a + b)])
            expr = parts[0] + "".join(" %s +" % p for p in parts[1:])
            h = P.add("pol %s ;" % expr)
            helpers.append(h)
            keep.append(P.add("rup %s : %s ;" % (pb([(1, l) for l in c], 1), h)))
        P.raw("deld %s ;" % " ".join(helpers))

    defs(root)
    L = len(root.leaves)
    if lo > 0:
        h = P.add("pol %s %s + ;" % (lo_label, down_def[(id(root), lo - 1)]))
        keep.append(P.add("rup 1 x%d >= 1 : %s ;" % (root.outs[lo - 1], h)))
        P.raw("deld %s ;" % h)
    if hi >= 0:
        h = P.add("pol %s %s + ;" % (hi_label, up_def[(id(root), hi)]))
        keep.append(P.add("rup 1 ~x%d >= 1 : %s ;" % (root.outs[hi], h)))
        P.raw("deld %s ;" % h)
    return keep


# ---------------------------------------------------------------------------------
# Sinz sequential counter (sms/gen_ramsey.py atmost): sum(lits) <= K.
# aux s[i][j], i = 0..m-2, j = 0..K-1, row-major ids after maxvar; meaning
# s[i][j] <-> (count of lits[0..i] >= j+1). Derivation per s (red, full definition):
#   (j+1) ~s + sum_{t<=i} l_t >= j+1          : s -> 0
#   (i+1-j) s + sum_{t<=i} ~l_t >= i+1-j     : s -> 1     (only if j <= i)
# then each sms clause by rup (some after one pol of two definitions or with the bound).
# ---------------------------------------------------------------------------------
def sinz(lits, K, maxvar):
    """Replicates sms atmost(lits, K): returns (clauses, s, maxvar)."""
    m = len(lits)
    if K >= m:
        return [], None, maxvar
    if K == 0:
        return [[-x] for x in lits], None, maxvar
    s = []
    for _ in range(m - 1):
        s.append(list(range(maxvar + 1, maxvar + K + 1)))
        maxvar += K
    C = [[-lits[0], s[0][0]]]
    C += [[-s[0][j]] for j in range(1, K)]
    for i in range(1, m - 1):
        C.append([-lits[i], s[i][0]])
        C.append([-s[i - 1][0], s[i][0]])
        for j in range(1, K):
            C.append([-lits[i], -s[i - 1][j - 1], s[i][j]])
            C.append([-s[i - 1][j], s[i][j]])
        C.append([-lits[i], -s[i - 1][K - 1]])
    C.append([-lits[m - 1], -s[m - 2][K - 1]])
    return C, s, maxvar


def sinz_derive(P, lits, K, s, bound_label):
    """bound_label: input PB constraint sum ~l >= m - K (i.e. sum l <= K).
    Returns labels of the sms clauses in sms order."""
    m = len(lits)
    if s is None:  # K == 0: units ~l from the bound
        return [P.add("rup 1 %s >= 1 : %s ;" % (lit(-l), bound_label)) for l in lits]
    up, down = {}, {}
    for i in range(m - 1):
        pre = lits[:i + 1]
        for j in range(K):
            v = s[i][j]
            up[(i, j)] = P.add("red %s : x%d -> 0 ;" % (pb([(j + 1, -v)] + [(1, l) for l in pre], j + 1), v))
            if j <= i:
                down[(i, j)] = P.add("red %s : x%d -> 1 ;" % (pb([(i + 1 - j, v)] + [(1, -l) for l in pre], i + 1 - j), v))
    keep, helpers = [], []

    def clause(c, *hints):
        keep.append(P.add("rup %s%s ;" % (pb([(1, l) for l in c], 1), (" : " + " ".join(hints)) if hints else "")))

    def polsum(a, b):
        h = P.add("pol %s %s + ;" % (a, b))
        helpers.append(h)
        return h

    clause([-lits[0], s[0][0]], down[(0, 0)])
    for j in range(1, K):
        clause([-s[0][j]], up[(0, j)])
    for i in range(1, m - 1):
        clause([-lits[i], s[i][0]], down[(i, 0)])
        clause([-s[i - 1][0], s[i][0]], down[(i, 0)], up[(i - 1, 0)])
        for j in range(1, K):
            if (i, j) in down:
                clause([-lits[i], -s[i - 1][j - 1], s[i][j]], polsum(down[(i, j)], up[(i - 1, j - 1)]))
                if (i - 1, j) in down:
                    clause([-s[i - 1][j], s[i][j]], polsum(down[(i, j)], up[(i - 1, j)]))
                else:  # s[i-1][j]: count of i items >= j+1 > i: false
                    clause([-s[i - 1][j], s[i][j]], up[(i - 1, j)])
            else:  # j > i: s[i][j] false; s[i-1][j-1] false too (j-1 >= i)
                clause([-lits[i], -s[i - 1][j - 1], s[i][j]], up[(i - 1, j - 1)])
                clause([-s[i - 1][j], s[i][j]], up[(i - 1, j)])
        clause([-lits[i], -s[i - 1][K - 1]], polsum(bound_label, up[(i - 1, K - 1)]))
    clause([-lits[m - 1], -s[m - 2][K - 1]], polsum(bound_label, up[(m - 2, K - 1)]))
    if helpers:
        P.raw("deld %s ;" % " ".join(helpers))
    return keep
