#!/usr/bin/env python3
"""cert/check_pbp.py - check that a VeriPB proof satisfies the conditions of meta-lemma M-IS.

Written by agent `cert` (critic finding X3). Independent of the proof writers.

M-IS (notes/cert_design.md sec. 1.2): a proof checked with core TRI (+ other input)
stays valid if all independent-set clauses IS_all are added to the input, provided:
  (W) every witness of `red`/`dom` acts on edge variables 1..N as
      "a vertex permutation sigma, except that some edge variables may map to 1":
      each edge var maps to a positive edge var or to 1 (never 0, a negative literal,
      or an aux var), and the edge -> edge part is e -> sigma(e) for ONE bijection
      sigma of the vertices (unmentioned edge vars count as e -> e);
  (D) no input/core constraint is deleted: `del`, `delc` are rejected (`deld` only
      removes derived constraints; VeriPB enforces that);
  (I) no positive numeric constraint ID <= n_input is referenced (so the proof text
      is the same up to a shift of derived IDs when IS_all is added to the input);
  (R) only these rules occur: f, def_order block, load_order, red, dom (with
      subproofs made of proofgoal/pol/rup/qed), rup, pol, deld, core, output
      EQUISATISFIABLE, conclusion NONE, end. No `a` (unchecked assertion).
  (P) with --perm-only: no witness may map an edge variable to 1. Needed when the claim
      is a non-monotone constraint such as "edges <= E" (critic Review 18, Q1): M-IS then
      covers IS_all + claim, because both are closed under vertex permutations.
Usage: check_pbp.py --n N --input-constraints K [--order colex|rowmajor] [--perm-only] PROOF.pbp
Exit 0 and "RESULT: OK" iff all conditions hold.
"""
import argparse
import re
import sys


def tokens(path):
    for line in open(path):
        line = line.split("%", 1)[0]
        for t in line.replace(";", " ; ").split():
            yield t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--input-constraints", type=int, required=True)
    ap.add_argument("--order", default="colex", choices=["colex", "rowmajor"])
    ap.add_argument("--perm-only", action="store_true",
                    help="every witness acts on edges as a pure vertex permutation (no edge -> 1); "
                         "needed when the core carries a claim such as 'edges <= E' (critic Q1)")
    ap.add_argument("proof")
    a = ap.parse_args()
    n, nin = a.n, a.input_constraints
    N = n * (n - 1) // 2
    # edge var -> vertex pair, colex numbering (as gen.py / satcore)
    pair = {}
    for j in range(n):
        for i in range(j):
            if a.order == "colex":
                pair[j * (j - 1) // 2 + i + 1] = (i, j)
            else:
                pair[i * n - i * (i + 1) // 2 + (j - i)] = (i, j)
    var_of = {p: v for v, p in pair.items()}

    errors = []
    stats = {}
    toks = list(tokens(a.proof))
    k = 0

    def err(msg):
        if len(errors) < 20:
            errors.append(msg)

    def stmt():
        """Return the tokens of one statement (up to ';'), advancing k."""
        nonlocal k
        out = []
        while k < len(toks) and toks[k] != ";":
            out.append(toks[k])
            k += 1
        k += 1
        return out

    def check_ids(ts, where):
        for t in ts:
            if re.fullmatch(r"\d+", t) and 0 < int(t) <= nin:
                err("%s references input constraint ID %s" % (where, t))

    def check_rule_ids(st, where):
        """IDs in pol (RPN; a number before '*' or 'd' is a scalar) and rup hints."""
        if st[0] == "pol":
            ids = [t for i, t in enumerate(st[1:], 1)
                   if not (i + 1 < len(st) and st[i + 1] in ("*", "d"))]
            check_ids(ids, where)
        elif st[0] == "rup":
            check_ids(st[st.index(":") + 1:] if ":" in st else [], where)

    def sub_stmt(st, depth, where):
        if not st:
            return depth
        if st[0] == "proofgoal":
            return sub_stmt(st[2:], depth + 1, where)
        if st[0] == "qed":
            return depth - 1
        if st[0] in ("pol", "rup"):
            check_rule_ids(st, where)
        else:
            err("%s: rule %s in subproof" % (where, st[0]))
        return depth

    def check_witness(ws, where):
        m = {}
        i = 0
        while i < len(ws):
            x = ws[i]
            i += 1
            if i < len(ws) and ws[i] == "->":
                i += 1
            if i >= len(ws):
                err("%s: witness ends early" % where)
                return
            y = ws[i]
            i += 1
            mx = re.fullmatch(r"x(\d+)", x)
            if not mx:
                err("%s: witness maps a non-variable %s" % (where, x))
                return
            m[int(mx.group(1))] = y
        sigma_edges = {}
        for v, y in m.items():
            if v > N:
                continue  # aux variable: free (IS clauses contain no aux var)
            if y == "1":
                continue
            my = re.fullmatch(r"x(\d+)", y)
            if not my or int(my.group(1)) > N:
                err("%s: edge var x%d -> %s (not a positive edge var or 1)" % (where, v, y))
                return
            sigma_edges[v] = int(my.group(1))
        to_one = {v for v, y in m.items() if v <= N and y == "1"}
        img = {e: sigma_edges.get(e, e) for e in range(1, N + 1) if e not in to_one}
        # reconstruct the vertex map from incident edges
        sig = {}
        for v in range(n):
            inc = [var_of[(min(v, u), max(v, u))] for u in range(n) if u != v]
            inc = [e for e in inc if e in img]
            if len(inc) < 2:
                err("%s: cannot determine sigma(%d)" % (where, v))
                return
            cand = None
            for e1, e2 in zip(inc, inc[1:]):
                common = set(pair[img[e1]]) & set(pair[img[e2]])
                if len(common) != 1:
                    err("%s: images of edges at vertex %d do not share one vertex" % (where, v))
                    return
                c = common.pop()
                if cand is not None and c != cand:
                    err("%s: inconsistent sigma(%d)" % (where, v))
                    return
                cand = c
            sig[v] = cand
        if sorted(sig.values()) != list(range(n)):
            err("%s: sigma is not a bijection" % where)
            return
        for e, f in img.items():
            i, j = pair[e]
            s1, s2 = sig[i], sig[j]
            if (min(s1, s2), max(s1, s2)) != pair[f]:
                err("%s: edge x%d -> x%d not induced by sigma" % (where, e, f))
                return
        kind = "perm" if any(sig[v] != v for v in range(n)) else "id"
        kind += "+to1" if to_one else ""
        if to_one and a.perm_only:
            err("%s: witness sets edge variables to 1 (not allowed with --perm-only)" % where)
            return
        stats["witness " + kind] = stats.get("witness " + kind, 0) + 1

    seen_output = False
    while k < len(toks):
        if toks[k] == "pseudo-Boolean" and k == 0:
            stmt_ = []
            while toks[k] != "3.0":
                k += 1
            k += 1
            continue
        start = k
        lab = None
        if toks[k].startswith("@"):
            lab = toks[k]
            k += 1
        rule = toks[k]
        where = "statement %d (%s)" % (start, rule)
        stats[rule] = stats.get(rule, 0) + 1
        if rule == "f":
            ts = stmt()
            if len(ts) != 2 or int(ts[1]) != nin:
                err("f line says %s, expected %d input constraints" % (ts[1:], nin))
        elif rule == "def_order":
            # Parse the block to its own matching "end ;" (critic P1). Its soundness as an
            # order is VeriPB's job; here only the structure: sections vars/spec/def/
            # transitivity/reflexivity ... end, proof/proofgoal ... qed, and inside them
            # only variable lists, constraints, pol and rup. Any other rule -> error.
            k += 2  # "def_order" <name>
            stack = ["def_order"]
            openers = {"vars", "spec", "def", "transitivity", "reflexivity"}
            listwords = {"left", "right", "aux", "fresh_right", "fresh_aux_1", "fresh_aux_2"}
            at_start = True
            while stack:
                if k >= len(toks):
                    err("%s: def_order block not closed" % where)
                    break
                t = toks[k]
                k += 1
                if t == ";":
                    at_start = True
                    continue
                if not at_start:
                    continue
                at_start = False
                if t in openers:
                    stack.append(t)
                    at_start = True  # "vars left ..." / "def <constraint>" follow without ';'
                elif t == "end":
                    top = stack.pop()
                    if top not in openers and top != "def_order":
                        err("%s: 'end' closes '%s'" % (where, top))
                        break
                    if k < len(toks) and toks[k] == "spec":
                        k += 1
                elif t == "proof":
                    stack.append("proof")
                    at_start = True
                elif t == "proofgoal":
                    stack.append("proofgoal")
                    k += 1  # goal id
                    at_start = True
                elif t == "qed":
                    top = stack.pop()
                    if top not in ("proof", "proofgoal"):
                        err("%s: 'qed' closes '%s'" % (where, top))
                        break
                elif t in listwords and stack[-1] == "vars":
                    pass
                elif t in ("pol", "rup") and stack[-1] == "proofgoal":
                    pass
                elif stack[-1] in ("def", "spec") and (re.fullmatch(r"[+-]?\d+", t) or (
                        t.startswith("@") and k < len(toks) and re.fullmatch(r"[+-]?\d+", toks[k]))):
                    pass  # a constraint "<coef> <lit> ... >= <rhs>" (optionally labelled)
                else:
                    err("%s: '%s' not allowed inside def_order (section %s)" % (where, t, stack[-1]))
                    break
            if not stack and k < len(toks) and toks[k] == ";":
                k += 1
        elif rule == "load_order":
            stmt()
        elif rule in ("red", "dom"):
            ts = stmt()
            body = ts[1:]
            if ":" not in body:
                err("%s: no witness" % where)
                continue
            c = body.index(":")
            rest = body[c + 1:]
            tail = None
            if ":" in rest:
                c2 = rest.index(":")
                if rest[c2 + 1:c2 + 2] != ["subproof"]:
                    err("%s: unexpected tokens after witness" % where)
                tail = rest[c2 + 2:]
                rest = rest[:c2]
            check_witness(rest, where)
            if tail is not None:
                depth = sub_stmt(tail, 1, where)
                while depth > 0 and k < len(toks):
                    depth = sub_stmt(stmt(), depth, where)
        elif rule in ("rup", "pol"):
            ts = stmt()
            check_rule_ids(ts, where)
        elif rule == "deld":
            ts = stmt()
            check_ids(ts[1:], where)
        elif rule in ("del", "delc"):
            stmt()
            err("%s: deletion of core/input constraints is not allowed" % where)
        elif rule == "core":
            ts = stmt()
            check_ids(ts[2:], where)
        elif rule == "output":
            seen_output = True
            ts = stmt()
            if ts[1:] != ["EQUISATISFIABLE", "FILE"]:
                err("output must be EQUISATISFIABLE FILE, found %s" % ts[1:])
        elif rule == "conclusion":
            ts = stmt()
            if ts[1:] != ["NONE"]:
                err("conclusion must be NONE, found %s" % ts[1:])
        elif rule == "end":
            stmt()
        else:
            err("%s: rule not allowed" % where)
            stmt()
    if not seen_output:
        err("no 'output EQUISATISFIABLE FILE' section")
    for key in sorted(stats):
        print("  %-24s %d" % (key, stats[key]))
    if errors:
        for e in errors:
            print("ERROR:", e)
        print("RESULT: FAIL")
        sys.exit(1)
    print("RESULT: OK (M-IS conditions W, D, I, R%s hold)" % (", P" if a.perm_only else ""))


if __name__ == "__main__":
    main()
