#!/usr/bin/env python3
"""cert/sb.py - symmetry-breaking clauses with VeriPB dominance proofs.

Written by agent `cert`.

Order. Positions p_1..p_N are the edges in row-major order
(0,1),(0,2),...,(0,n-1),(1,2),...,(n-2,n-1); N = n(n-1)/2.
val(x) = sum_k 2^(N-k) x_{p_k}. A graph is "better" if val is larger.
VeriPB order lexmax(u, v) := val(u) - val(v) >= 0   (u is at least as good as v).

Every SB clause has the form NOT(alpha), alpha a partial assignment of edge
variables, with a vertex permutation pi such that val(pi(x)) > val(x) for EVERY
total x that extends alpha. VeriPB derives it with
    dom <clause> : x_p -> x_{pi^-1(p)} ... ;
The proof goals are: (1) every core clause maps under pi to a core clause
(true for the Ramsey formula, which is closed under vertex permutations), and
(2) val(pi(x)) > val(x) under alpha, which unit propagation on one PB constraint
proves. So VeriPB auto-proves each step.

Edge variables use colex numbering (as satcore): var(i,j) = j(j-1)/2 + i + 1.
"""
import itertools


VARORDER = "colex"  # or "rowmajor" (SMS); set before use
NVERT = None         # needed for rowmajor


def var(i, j):
    if i > j:
        i, j = j, i
    if VARORDER == "rowmajor":
        return i * NVERT - i * (i + 1) // 2 + (j - i)
    return j * (j - 1) // 2 + i + 1


POSITIONS = "rowmajor"  # order of the lex comparison; "colex" for MathCheck


def positions(n):
    if POSITIONS == "colex":
        return [(i, j) for j in range(n) for i in range(j)]
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def perm_edge(pinv, e):
    a, b = pinv[e[0]], pinv[e[1]]
    return (a, b) if a < b else (b, a)


def lex_clause(n, G, pi):
    """G: set of edges (i<j). pi: list, vertex v -> pi[v].
    If pi(G) is lex-better than G, return the clause NOT(alpha) (list of DIMACS
    literals) for the shortest prefix alpha that forces this; else None."""
    pinv = [0] * n
    for v, w in enumerate(pi):
        pinv[w] = v
    alpha = {}
    for p in positions(n):
        q = perm_edge(pinv, p)  # (pi G)_p = G_q
        a = p in G
        b = q in G
        if q != p:
            alpha[p] = a
            alpha[q] = b
        if a == b:
            continue
        if b and not a:
            return sorted((-var(*e) if val else var(*e)) for e, val in alpha.items())
        return None
    return None


def static_clauses(n, depth):
    """Partial lex-leader clauses for adjacent transpositions (j j+1),
    j=1..n-2, comparing the first `depth`+1 swapped position pairs."""
    out = []
    for j in range(1, n - 1):
        pi = list(range(n))
        pi[j], pi[j + 1] = j + 1, j
        pinv = pi  # transposition
        pairs = []
        seen = set()
        for p in positions(n):
            q = perm_edge(pinv, p)
            if q != p and p not in seen:
                pairs.append((p, q))
                seen.add(p)
                seen.add(q)
        pairs = pairs[: depth + 1]
        for k in range(len(pairs)):
            # all equality patterns of the first k pairs, then pair k is (0,1)
            for eq in itertools.product([0, 1], repeat=k):
                G = set()
                for (p, q), v in zip(pairs[:k], eq):
                    if v:
                        G.add(p)
                        G.add(q)
                p, q = pairs[k]
                G.add(q)  # x_p = 0, x_q = 1
                cl = lex_clause(n, G, pi)
                assert cl is not None
                out.append((cl, pi))
    return out


def witness(n, pi):
    pinv = [0] * n
    for v, w in enumerate(pi):
        pinv[w] = v
    parts = []
    for p in positions(n):
        q = perm_edge(pinv, p)
        if q != p:
            parts.append("x%d -> x%d" % (var(*p), var(*q)))
    return " ".join(parts)


def opb_clause(cl):
    return " ".join(("1 ~x%d" % -l) if l < 0 else ("1 x%d" % l) for l in cl) + " >= 1"


def write_veripb(path, n, nformula, sb, better="max", prefix=(), aux_witness=None):
    """sb: list of (clause, pi). Proof: input formula (nformula clauses) ->
    output formula = input + all SB clauses, EQUISATISFIABLE.
    prefix: proof lines before the order is loaded, each adding one constraint
    (e.g. MTF by `red`); aux_witness(pi): extra witness mappings for aux vars."""
    N = n * (n - 1) // 2
    sgn = 1 if better == "max" else -1
    coef = [sgn * 2 ** (N - 1 - k) for k in range(N)]
    us = " ".join("u%d" % k for k in range(1, N + 1))
    vs = " ".join("v%d" % k for k in range(1, N + 1))
    ws = " ".join("w%d" % k for k in range(1, N + 1))
    od = " ".join("%d u%d" % (c, k + 1) for k, c in enumerate(coef)) + " " + \
        " ".join("%d v%d" % (-c, k + 1) for k, c in enumerate(coef)) + " >= 0"
    with open(path, "w") as f:
        f.write("pseudo-Boolean proof version 3.0\n")
        f.write("f %d ;\n" % nformula)
        for line in prefix:
            f.write(line + "\n")
        f.write("def_order lexmax\n  vars\n    left %s ;\n    right %s ;\n    aux ;\n  end;\n" % (us, vs))
        f.write("  def\n    %s ;\n  end;\n" % od)
        f.write("  transitivity\n    vars\n      fresh_right %s ;\n    end;\n" % ws)
        f.write("    proof\n      proofgoal #1\n        pol -2 -3 + -1 + ;\n      qed : -1 ;\n    qed;\n  end;\nend;\n")
        f.write("load_order lexmax %s ;\n" % " ".join("x%d" % var(*p) for p in positions(n)))
        for cl, pi in sb:
            w = witness(n, pi)
            if aux_witness:
                w = (w + " " + aux_witness(pi)).strip()
            f.write("dom %s : %s ;\n" % (opb_clause(cl), w))
        f.write("load_order ;\n")
        if sb:
            a = nformula + len(prefix) + 1
            f.write("core range %d %d ;\n" % (a, a + len(sb)))
        f.write("output EQUISATISFIABLE FILE ;\nconclusion NONE ;\nend pseudo-Boolean proof ;\n")


def cnf_to_opb(cnf_path, opb_path):
    """Write a DIMACS CNF as OPB (clause C -> sum of literals >= 1)."""
    nv = 0
    cls = []
    cur = []
    for line in open(cnf_path):
        if line.startswith(("c", "p")):
            if line.startswith("p"):
                nv = int(line.split()[2])
            continue
        for t in line.split():
            l = int(t)
            if l == 0:
                cls.append(cur)
                cur = []
            else:
                cur.append(l)
    with open(opb_path, "w") as f:
        f.write("* #variable= %d #constraint= %d\n" % (nv, len(cls)))
        for c in cls:
            f.write(opb_clause(c) + " ;\n")
    return len(cls)
