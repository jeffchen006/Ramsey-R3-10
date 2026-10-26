#!/usr/bin/env python3
"""Independent check of ext27.py certificates (notes/symsat.md F10). Does not import ext27.py.

For one certificate (H as graph6, involution s of H, f, list of vertex 10-sets) it:
  1. checks H: 27 vertices, triangle-free, alpha(H) <= 7; s: automorphism of H, s^2 = id,
     exactly f - 7 fixed points;
  2. builds G's known part from F10 itself: x=27, x'=28, A=29..35, b1,b1',b2,b2' = 36..39;
     N(x) = A+{b1,b2}, N(x') = A+{b1',b2'}; all other pairs among 27..39 non-edges except the
     4 pairs {b1,b2}x{b1',b2'}; x, x' have no H-neighbour; sigma = s on H, (x x')(b1 b1')(b2 b2');
  3. variables = sigma-orbits on the unknown pairs (union-find; numbered by least pair);
  4. CNF = triangle clauses + for each given 10-set (checked: 10 distinct vertices, no known
     edge inside) the clause "some unknown pair inside is an edge";
  5. CaDiCaL writes a DRAT proof; drat-trim must print "s VERIFIED".
UNSAT of this CNF means: no triangle-free G with alpha <= 9 of the F10 form with sigma|H = s.
Usage: ext27_verify.py CERT.json [CERT.json ...]   prints one line per certificate.
"""
import itertools
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, "./tools")
from check_graph import parse_graph6, triangle_free, alpha  # noqa: E402

BIN = "./tools/bin"
N = 40


def check(path, work):
    d = json.load(open(path))
    h = parse_graph6(d["g6"])
    s, f = d["s"], d["f"]
    assert len(h) == 27 and triangle_free(h) and alpha(h) <= 7, "H is not a (3,8,27)-graph"
    assert sorted(s) == list(range(27)) and all(s[s[i]] == i for i in range(27))
    assert all(((h[u] >> v) & 1) == ((h[s[u]] >> s[v]) & 1) for u in range(27) for v in range(27))
    assert sum(s[i] == i for i in range(27)) == f - 7
    x, xp, A, b1, b1p, b2, b2p = 27, 28, list(range(29, 36)), 36, 37, 38, 39
    sig = list(s) + [xp, x] + A + [b1p, b1, b2p, b2]
    edge = {}                            # known pairs: True / False; unknown pairs absent
    for u in range(27):
        for v in range(u + 1, 27):
            edge[(u, v)] = bool((h[u] >> v) & 1)
    new = list(range(27, 40))
    for u, v in itertools.combinations(new, 2):
        edge[(u, v)] = False
    for a in A:
        edge[(x, a)] = edge[(xp, a)] = True
    for e in [(x, b1), (x, b2), (xp, b1p), (xp, b2p)]:
        edge[e] = True
    for e in [(b1, b1p), (b2, b2p), (b1, b2p), (b1p, b2)]:
        del edge[e]
    for u in (x, xp):
        for v in range(27):
            edge[(v, u)] = False
    unknown = [(u, v) for u in range(N) for v in range(u + 1, N) if (u, v) not in edge]
    assert len(unknown) == 11 * 27 + 4
    # sigma must preserve the known part
    pr = lambda u, v: (u, v) if u < v else (v, u)
    for (u, v), val in edge.items():
        assert edge.get(pr(sig[u], sig[v])) == val, "sigma does not preserve known part"
    parent = {e: e for e in unknown}

    def find(e):
        while parent[e] != e:
            parent[e] = parent[parent[e]]; e = parent[e]
        return e
    for (u, v) in unknown:
        a, b = find((u, v)), find(pr(sig[u], sig[v]))
        if a != b:
            parent[max(a, b)] = min(a, b)
    reps = sorted(set(find(e) for e in unknown))
    var = {r: i + 1 for i, r in enumerate(reps)}

    def lit(u, v):                       # True / False / variable
        e = pr(u, v)
        return edge[e] if e in edge else var[find(e)]
    cls = []
    for t in itertools.combinations(range(N), 3):
        ls = [lit(t[0], t[1]), lit(t[0], t[2]), lit(t[1], t[2])]
        if any(l is False for l in ls):
            continue
        c = [-l for l in ls if l is not True]
        assert c, "triangle in known part"
        cls.append(c)
    ntri = len(cls)
    for vs in d["sets"]:
        assert len(vs) == 10 and len(set(vs)) == 10 and all(0 <= v < N for v in vs)
        ls = [lit(u, v) for u, v in itertools.combinations(vs, 2)]
        assert not any(l is True for l in ls), "10-set contains a known edge"
        c = sorted(set(l for l in ls if l is not False))
        assert c, "independent 10-set in known part"
        cls.append(c)
    cnf = os.path.join(work, "c.cnf"); proof = os.path.join(work, "c.drat")
    with open(cnf, "w") as fh:
        fh.write(f"p cnf {len(var)} {len(cls)}\n")
        for c in cls:
            fh.write(" ".join(map(str, c)) + " 0\n")
    r = subprocess.run([f"{BIN}/cadical", "-q", cnf, proof], capture_output=True, text=True)
    st = [l for l in r.stdout.split("\n") if l.startswith("s ")]
    if st != ["s UNSATISFIABLE"]:
        return f"FAIL cadical {st}"
    r = subprocess.run([f"{BIN}/drat-trim", cnf, proof, "-t", "100000"], capture_output=True, text=True)
    dt = [l for l in r.stdout.split("\n") if l.startswith("s ")]
    res = "VERIFIED" if dt == ["s VERIFIED"] else f"FAIL drat-trim {dt}"
    return f"{res} vars={len(var)} tri={ntri} sets={len(d['sets'])}"


def main():
    with tempfile.TemporaryDirectory(dir="./runs/symsat/work") as work:
        for p in sys.argv[1:]:
            try:
                out = check(p, work)
            except AssertionError as e:
                out = f"FAIL assert {e}"
            print(os.path.basename(p), out, flush=True)


if __name__ == "__main__":
    main()
