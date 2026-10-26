#!/usr/bin/env python3
"""cert/check_cnf.py - check that a CNF file is a sound Ramsey (3,s,n) formula.

Written by agent `cert`. Shares no code with satcore, sms or cert/gen.py
(the edge-variable map is re-derived here on purpose).

Claim checked: every clause of CNF is satisfied by every triangle-free graph
on n vertices with independence number < s (edge variables only), OR the clause
appears in one of the --extra files (clauses whose justification is checked
elsewhere: symmetry breaking, case-split units, cardinality encodings, ...).
If this check passes and CNF is UNSAT, then
    (no (3,s,n)-graph) or (some --extra clause is unjustified).

Accepted clause kinds (edge variables 1..n(n-1)/2):
  TRI      exactly {-e_ij, -e_ik, -e_jk} for a triangle i<j<k
  IS       exactly {+e_ab : a<b in S} for an s-set S
  TRI+     (with --weak) a superset of a TRI clause
  IS+      (with --weak) a superset of an IS clause
  TAUT     contains x and -x
  EXTRA:f  clause (as a literal set) is in --extra file f
Anything else is an error. Variables > n(n-1)/2 may occur only in EXTRA clauses.

With --require-all-tri the file must ALSO contain every one of the C(n,3)
triangle clauses (completeness; critic X4: implied constraints D are only true in
models that are triangle-free). --opb reads an OPB file whose constraints are all
clauses (coefficients 1, ">= 1"), e.g. a VeriPB input.
Usage:
  check_cnf.py --n N --s S [--order colex|rowmajor] [--weak] [--opb]
               [--require-all-tri] [--extra FILE]... [--max-errors K] CNF
Exit code 0 iff every clause is accepted and the DIMACS syntax is strict-valid.
"""
import argparse
import hashlib
import sys
from itertools import combinations


def edge_map(n, order):
    """Return dict var -> (i, j) with i < j."""
    m = {}
    if order == "colex":
        v = 0
        for j in range(n):
            for i in range(j):
                v += 1
                m[v] = (i, j)
    elif order == "rowmajor":
        v = 0
        for i in range(n):
            for j in range(i + 1, n):
                v += 1
                m[v] = (i, j)
    else:
        raise SystemExit("bad order")
    assert len(m) == n * (n - 1) // 2
    return m


def read_dimacs(path):
    """Strict DIMACS reader. Yields clauses (tuples). Checks header counts."""
    nvars = ncls = None
    count = 0
    cur = []
    with open(path, "rb") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.decode("ascii").strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("p"):
                if nvars is not None:
                    raise ValueError("%s:%d: second p line" % (path, lineno))
                parts = line.split()
                if len(parts) != 4 or parts[1] != "cnf":
                    raise ValueError("%s:%d: bad p line" % (path, lineno))
                nvars, ncls = int(parts[2]), int(parts[3])
                continue
            if nvars is None:
                raise ValueError("%s:%d: clause before p line" % (path, lineno))
            for tok in line.split():
                lit = int(tok)
                if lit == 0:
                    yield tuple(cur)
                    count += 1
                    cur = []
                else:
                    if abs(lit) > nvars:
                        raise ValueError("%s:%d: var %d > %d" % (path, lineno, abs(lit), nvars))
                    cur.append(lit)
    if cur:
        raise ValueError("%s: last clause not ended by 0" % path)
    if nvars is None:
        raise ValueError("%s: no p line" % path)
    if count != ncls:
        raise ValueError("%s: header says %d clauses, found %d" % (path, ncls, count))


def read_opb_clauses(path):
    """OPB file -> clauses; every constraint must be 'sum 1 [~]x_i >= 1 ;'."""
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("*"):
                continue
            if not line.endswith(";"):
                raise ValueError("%s:%d: constraint does not end with ';'" % (path, lineno))
            t = line[:-1].split()
            if len(t) < 2 or t[-2] != ">=" or t[-1] != "1" or len(t) % 2 != 0:
                raise ValueError("%s:%d: not a clause: %s" % (path, lineno, line))
            cl = []
            for c, lit in zip(t[:-2:2], t[1:-2:2]):
                if c != "1":
                    raise ValueError("%s:%d: coefficient %s" % (path, lineno, c))
                neg = lit.startswith("~")
                v = int(lit.lstrip("~").lstrip("x"))
                if not lit.lstrip("~").startswith("x") or v <= 0:
                    raise ValueError("%s:%d: bad literal %s" % (path, lineno, lit))
                cl.append(-v if neg else v)
            yield tuple(cl)


def has_clique(adj, verts, size):
    """True if graph (adj: vertex -> set) restricted to verts has a clique of given size."""
    verts = sorted(verts)

    def ext(chosen, cand):
        if len(chosen) == size:
            return True
        if len(chosen) + len(cand) < size:
            return False
        for idx, v in enumerate(cand):
            if ext(chosen + [v], [w for w in cand[idx + 1:] if w in adj[v]]):
                return True
        return False

    return ext([], verts)


def classify(clause, emap, nedge, s, weak):
    lits = set(clause)
    if any(-l in lits for l in lits):
        return "TAUT"
    if any(abs(l) > nedge for l in lits):
        return None
    neg = [emap[-l] for l in lits if l < 0]
    pos = [emap[l] for l in lits if l > 0]
    # exact triangle clause
    if not pos and len(neg) == 3:
        vs = {v for e in neg for v in e}
        if len(vs) == 3:
            return "TRI"
    # exact independent-set clause
    if not neg and len(pos) == s * (s - 1) // 2:
        vs = {v for e in pos for v in e}
        if len(vs) == s:
            return "IS"  # s vertices and C(s,2) distinct pairs => all pairs
    if not weak:
        return None
    for edges, size, tag in ((neg, 3, "TRI+"), (pos, s, "IS+")):
        if len(edges) < size * (size - 1) // 2:
            continue
        adj = {}
        for a, b in edges:
            adj.setdefault(a, set()).add(b)
            adj.setdefault(b, set()).add(a)
        if has_clique(adj, adj.keys(), size):
            return tag
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--s", type=int, required=True)
    ap.add_argument("--order", default="colex")
    ap.add_argument("--weak", action="store_true")
    ap.add_argument("--extra", action="append", default=[])
    ap.add_argument("--max-errors", type=int, default=10)
    ap.add_argument("--opb", action="store_true")
    ap.add_argument("--require-all-tri", action="store_true")
    ap.add_argument("cnf")
    a = ap.parse_args()

    emap = edge_map(a.n, a.order)
    nedge = len(emap)
    extras = {}
    for path in a.extra:
        for c in read_dimacs(path):
            extras.setdefault(frozenset(c), path)

    counts = {}
    errors = 0
    total = 0
    tri_seen = set()
    reader = read_opb_clauses(a.cnf) if a.opb else read_dimacs(a.cnf)
    for idx, c in enumerate(reader, 1):
        total += 1
        kind = classify(c, emap, nedge, a.s, a.weak)
        if kind == "TRI":
            tri_seen.add(frozenset(v for l in c for v in emap[-l]))
        if kind is None:
            path = extras.get(frozenset(c))
            if path is not None:
                kind = "EXTRA:" + path
        if kind is None:
            errors += 1
            if errors <= a.max_errors:
                print("UNJUSTIFIED clause #%d: %s" % (idx, " ".join(map(str, c))))
            kind = "UNJUSTIFIED"
        counts[kind] = counts.get(kind, 0) + 1

    if a.require_all_tri:
        missing = a.n * (a.n - 1) * (a.n - 2) // 6 - len(tri_seen)
        print("triangle clauses present: %d distinct of %d" % (len(tri_seen), a.n * (a.n - 1) * (a.n - 2) // 6))
        if missing:
            print("RESULT: FAIL (%d triangle clauses missing)" % missing)
            sys.exit(1)
    h = hashlib.sha256(open(a.cnf, "rb").read()).hexdigest()
    print("file %s sha256 %s" % (a.cnf, h))
    print("n=%d s=%d order=%s clauses=%d" % (a.n, a.s, a.order, total))
    for k in sorted(counts):
        print("  %-30s %d" % (k, counts[k]))
    if errors:
        print("RESULT: FAIL (%d unjustified clauses)" % errors)
        sys.exit(1)
    print("RESULT: OK (every clause is valid or listed as extra)")


if __name__ == "__main__":
    main()
