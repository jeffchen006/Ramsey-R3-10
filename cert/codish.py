#!/usr/bin/env python3
"""cert/codish.py - VeriPB derivation of satcore's aux-encoded lex clauses.

Written by agent `cert`. Design: notes/cert_design.md sec. 3.6.
satcore (satcore/src/ramsey.hpp, lex_rows): for rows i, i+1 in one block, pairs
(a_k, b_k) = (x(i,j_k), x(i+1,j_k)), j_k = columns 0..n-1 without i, i+1, ascending:
    A_k : (-e_{k-1}) a_k -b_k              (e_0 = true: literal omitted)
    c1_k: (-e_{k-1}) -a_k -b_k e_k          (k < m)
    c2_k: (-e_{k-1})  a_k  b_k e_k          (k < m)
This is "row_i >=lex row_{i+1}", i.e. val(x) >= val(sigma x) for sigma = (i i+1)
under the lex-MAX order of the row-major edge vector (sb.py).
VeriPB steps per transposition (order lexmax loaded):
  L    dom  sum_k d_k (a_k - b_k) >= 0 : sigma        (d_k = coef(a_k) - coef(b_k))
  defs red  -e_k e_{k-1} ; -e_k a_k -b_k ; -e_k -a_k b_k   : e_k -> 0   (fresh e_k)
       red  c1_k ; c2_k                                    : e_k -> 1
  G_1 = L; G_k = G_{k-1} + S_{k-1} (-e_{k-1} e_{k-2}) + d_{k-1} (-e_{k-1} -a_{k-1} b_{k-1})
       = sum_{j>=k} d_j (a_j - b_j) + S_k (1 - e_{k-1}) >= 0,  S_k = d_1 + ... + d_{k-1}
  A_k  rup (from G_k: e_{k-1}, -a_k, b_k leave max LHS < 0)
  deld L, G_k, the "->" definitions.  Kept: A_k, c1_k, c2_k (exactly satcore's clauses).
"""
import sb


class Proof:
    """Writes VeriPB lines; every derived constraint gets a label @<prefix><k>
    (subproofs consume constraint IDs, so numeric IDs are not tracked)."""

    def __init__(self, prefix="L"):
        self.prefix = prefix
        self.k = 0
        self.lines = []

    def add(self, line):
        self.k += 1
        lab = "@%s%d" % (self.prefix, self.k)
        self.lines.append(lab + " " + line)
        return lab

    def raw(self, line):
        self.lines.append(line)


def lex_rows(n, blocks, maxvar):
    """Replicates satcore's lex_rows clause list and aux numbering.
    Returns (clauses, maxvar, per-transposition structure)."""
    clauses = []
    struct = []
    for lo, hi in blocks:
        for i in range(lo, hi - 1):
            cols = [j for j in range(n) if j not in (i, i + 1)]
            pairs = [(sb.var(i, j), sb.var(i + 1, j)) for j in cols]
            es = [None]
            for k, (a, b) in enumerate(pairs):
                e = es[-1]
                clauses.append(([-e] if e else []) + [a, -b])
                if k == len(pairs) - 1:
                    break
                maxvar += 1
                ne = maxvar
                clauses.append(([-e] if e else []) + [-a, -b, ne])
                clauses.append(([-e] if e else []) + [a, b, ne])
                es.append(ne)
            struct.append((i, pairs, es))
    return clauses, maxvar, struct


def coef_map(n):
    pos = sb.positions(n)
    N = len(pos)
    return {sb.var(*p): 2 ** (N - 1 - k) for k, p in enumerate(pos)}


def derive(proof, n, struct, aux_witness=None):
    """Append the derivation for every transposition. Returns the IDs of the
    kept clauses (A_k, c1_k, c2_k) in satcore's clause order."""
    cm = coef_map(n)
    keep = []
    for i, pairs, es in struct:
        pi = list(range(n))
        pi[i], pi[i + 1] = i + 1, i
        w = sb.witness(n, pi)
        if aux_witness:
            w = (w + " " + aux_witness(pi)).strip()
        d = [cm[a] - cm[b] for a, b in pairs]
        keep += derive_one(proof, w, pairs, d, es)
    return keep


def derive_one(proof, w, pairs, d, es):
    """Lex constraint sum_k d_k (a_k - b_k) >= 0 (all d_k > 0, d_k > sum of later d)
    by `dom` with witness w, then the aux-encoded clauses A_k, c1_k, c2_k.
    Returns their labels (A_1, c1_1, c2_1, A_2, ...)."""
    assert all(x > 0 for x in d)
    keep = []
    if True:
        # goal #2 (not x <= sigma x) needs one cutting-planes step: premise NOT L
        # plus the negated goal (= L) add up to 0 >= 1.
        L = proof.add("dom %s >= 0 : %s : subproof\n  proofgoal #2\n    pol -1 -2 + ;\n  qed : -1 ;\nqed ;"
                      % (" ".join("%d x%d %d x%d" % (dk, a, -dk, b) for dk, (a, b) in zip(d, pairs)), w))
        helpers = [L]
        D1, D2 = {}, {}
        ids_c = {}
        m = len(pairs)
        for k in range(1, m):  # e_k, k = 1..m-1 (es[k])
            e, ep = es[k], es[k - 1]
            a, b = pairs[k - 1]
            if ep:
                D1[k] = proof.add("red %s : x%d -> 0 ;" % (sb.opb_clause([-e, ep]), e))
                helpers.append(D1[k])
            helpers.append(proof.add("red %s : x%d -> 0 ;" % (sb.opb_clause([-e, a, -b]), e)))
            D2[k] = proof.add("red %s : x%d -> 0 ;" % (sb.opb_clause([-e, -a, b]), e))
            helpers.append(D2[k])
            pre = [-ep] if ep else []
            ids_c[k] = (proof.add("red %s : x%d -> 1 ;" % (sb.opb_clause(pre + [-a, -b, e]), e)),
                        proof.add("red %s : x%d -> 1 ;" % (sb.opb_clause(pre + [a, b, e]), e)))
        G = L
        S = 0
        for k in range(1, m + 1):  # A_k, 1-based
            if k >= 2:
                parts = [G]
                if k - 1 in D1:
                    parts.append("%s %d * +" % (D1[k - 1], S))
                parts.append("%s %d * +" % (D2[k - 1], d[k - 2]))
                S += d[k - 2]
                G = proof.add("pol %s ;" % " ".join(parts))
                helpers.append(G)
            a, b = pairs[k - 1]
            ep = es[k - 1]
            A = proof.add("rup %s : %s ;" % (sb.opb_clause(([-ep] if ep else []) + [a, -b]), G))
            keep.append(A)
            if k < m:
                keep.extend(ids_c[k])
        proof.raw("deld %s ;" % " ".join(helpers))
    return keep
