#!/usr/bin/env python3
"""For each graph (graph6 on stdin or file), compute Aut(G) with nauty (dreadnaut), enumerate
the group, and report the set of (p, f) for elements of prime order p with f fixed points.
Usage: autcycles.py FILE [--maxgroup N]   (FILE may be .gz)
Output: one line per graph with nontrivial group: index |Aut| types; then the union."""
import gzip
import re
import subprocess
import sys

sys.path.insert(0, "./tools")
from check_graph import parse_graph6  # noqa: E402

DREAD = "./tools/bin/dreadnaut"


def generators(adj):
    n = len(adj)
    lines = [f"n={n} g"]
    for v in range(n):
        nb = [u for u in range(n) if (adj[v] >> u) & 1 and u > v]
        lines.append(f"{v}: " + " ".join(map(str, nb)) + ";")
    inp = "-m\n" + "\n".join(lines)[:-1] + ".\nx\nq\n"
    out = subprocess.run([DREAD], input=inp, capture_output=True, text=True).stdout
    gens = []
    # generator lines are cycle notation, possibly wrapped; collect blocks before "level"
    text = out
    cur = []
    for line in text.split("\n"):
        if line.startswith("("):          # a new generator starts in column 0
            if cur:
                gens.append(" ".join(cur))
            cur = [line.strip()]
        elif cur and line.startswith(" ") and re.match(r"^[\d\s()]+$", line):  # wrapped
            cur.append(line.strip())
        else:
            if cur:
                gens.append(" ".join(cur)); cur = []
    if cur:
        gens.append(" ".join(cur))
    perms = []
    for gtxt in gens:
        p = list(range(n))
        for cyc in re.findall(r"\(([\d\s]+)\)", gtxt):
            c = list(map(int, cyc.split()))
            for i in range(len(c)):
                p[c[i]] = c[(i + 1) % len(c)]
        perms.append(tuple(p))
    m = re.search(r"grpsize=([\d.e+]+)", out)
    size = float(m.group(1)) if m else None
    return perms, size


def group_elements(gens, n, limit):
    e = tuple(range(n))
    seen = {e}
    fr = [e]
    while fr:
        nf = []
        for x in fr:
            for g in gens:
                y = tuple(g[x[i]] for i in range(n))
                if y not in seen:
                    seen.add(y)
                    nf.append(y)
                    if len(seen) > limit:
                        return None
        fr = nf
    return seen


def order(p):
    n = len(p)
    seen = [False] * n
    from math import gcd
    o = 1
    for i in range(n):
        if not seen[i]:
            L, j = 0, i
            while not seen[j]:
                seen[j] = True; j = p[j]; L += 1
            o = o * L // gcd(o, L)
    return o


def is_prime(m):
    return m > 1 and all(m % d for d in range(2, int(m ** 0.5) + 1))


def main():
    path = sys.argv[1]
    limit = 10 ** 6
    op = gzip.open if path.endswith(".gz") else open
    union = {}
    with op(path, "rt") as fh:
        for idx, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            adj = parse_graph6(line)
            n = len(adj)
            gens, size = generators(adj)
            if not gens:
                continue
            els = group_elements(gens, n, limit)
            assert els is not None and (size is None or abs(len(els) - size) < 0.5), (len(els), size)
            types = set()
            for g in els:
                o = order(g)
                if is_prime(o):
                    types.add((o, sum(g[i] == i for i in range(n))))
            print(idx, len(els), sorted(types), flush=True)
            for t in types:
                union.setdefault(t, []).append(idx)
    print("UNION", {t: len(v) for t, v in sorted(union.items())})


if __name__ == "__main__":
    main()
