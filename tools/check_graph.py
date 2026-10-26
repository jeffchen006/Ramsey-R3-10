#!/usr/bin/env python3
"""Independent checker for (3,k,n)-graphs. Pure Python, no dependencies.

Usage:
  check_graph.py [--k K] [--n N] FILE   FILE has graph6 lines (a ">>graph6<<" header is
                                        allowed), or one 0/1 adjacency matrix
  check_graph.py --selftest

For each graph it prints n, edge count, degree range, triangle-free, alpha,
and whether it is a (3,K)-graph (triangle-free and alpha < K). Exit code 0 only
if every graph is a (3,K)-graph (and has N vertices, if --n is given);
1 if a graph fails; 2 if the input is malformed or has no graphs.
"""
import argparse
import itertools
import random
import sys


class InputError(Exception):
    pass


HEADER = ">>graph6<<"


def parse_graph6(line):
    """Strict graph6 parse (n < 258048): checks characters, length and zero padding."""
    s = line.strip()
    if s.startswith(HEADER):
        s = s[len(HEADER):]
    if not s:
        raise InputError("empty graph6 string")
    if any(not 63 <= ord(c) <= 126 for c in s):
        raise InputError("bad character in graph6 string %r" % s[:20])
    data = [ord(c) - 63 for c in s]
    if data[0] == 63:
        if len(data) < 4 or data[1] == 63:
            raise InputError("unsupported graph6 size field")
        n = (data[1] << 12) | (data[2] << 6) | data[3]
        if n < 63:
            raise InputError("long size field used for n=%d < 63" % n)
        data = data[4:]
    else:
        n = data[0]
        data = data[1:]
    if n == 0:
        raise InputError("graph with 0 vertices")
    nbits = n * (n - 1) // 2
    if len(data) != (nbits + 5) // 6:
        raise InputError("graph6 length %d does not match n=%d" % (len(data), n))
    bits = []
    for x in data:
        for s in range(5, -1, -1):
            bits.append((x >> s) & 1)
    if any(bits[nbits:]):
        raise InputError("nonzero padding bits in graph6 string")
    adj = [0] * n
    i = 0
    for j in range(1, n):
        for u in range(j):
            if bits[i]:
                adj[u] |= 1 << j
                adj[j] |= 1 << u
            i += 1
    return adj


def to_graph6(adj):
    n = len(adj)
    if n >= 63:
        raise ValueError("to_graph6 supports n < 63 only")
    bits = [(adj[u] >> j) & 1 for j in range(1, n) for u in range(j)]
    bits += [0] * (-len(bits) % 6)
    out = [chr(n + 63)]
    for i in range(0, len(bits), 6):
        x = 0
        for b in bits[i:i + 6]:
            x = (x << 1) | b
        out.append(chr(x + 63))
    return "".join(out)


def parse_matrix(lines):
    rows = [l.split() if " " in l.strip() else list(l.strip()) for l in lines if l.strip()]
    n = len(rows)
    adj = [0] * n
    for u in range(n):
        if len(rows[u]) != n:
            raise InputError("matrix is not square")
        for v in range(n):
            if rows[u][v] == "1":
                adj[u] |= 1 << v
    for u in range(n):
        if (adj[u] >> u) & 1:
            raise InputError("loop at %d" % u)
        for v in range(n):
            if ((adj[u] >> v) & 1) != ((adj[v] >> u) & 1):
                raise InputError("not symmetric at (%d,%d)" % (u, v))
    return adj


def triangle_free(adj):
    n = len(adj)
    for u in range(n):
        for v in range(u + 1, n):
            if (adj[u] >> v) & 1 and adj[u] & adj[v]:
                return False
    return True


def alpha(adj):
    """Maximum independent set size, plain branch and bound."""
    n = len(adj)
    best = [0]

    def rec(P, size):
        if P == 0:
            if size > best[0]:
                best[0] = size
            return
        if size + bin(P).count("1") <= best[0]:
            return
        # branch on the vertex in P with the most neighbours in P
        v, dv = -1, -1
        Q = P
        while Q:
            w = (Q & -Q).bit_length() - 1
            Q &= Q - 1
            d = bin(adj[w] & P).count("1")
            if d > dv:
                v, dv = w, d
        if dv == 0:
            rec(0, size + bin(P).count("1"))
            return
        rec(P & ~adj[v] & ~(1 << v), size + 1)
        rec(P & ~(1 << v), size)

    rec((1 << n) - 1, 0)
    return best[0]


def report(adj, k):
    n = len(adj)
    degs = [bin(a).count("1") for a in adj]
    tf = triangle_free(adj)
    a = alpha(adj)
    ok = tf and a < k
    print("n=%d e=%d deg=[%d,%d] triangle_free=%s alpha=%d (3,%d)-graph=%s"
          % (n, sum(degs) // 2, min(degs), max(degs), tf, a, k, ok))
    return ok


def brute_alpha(adj):
    n = len(adj)
    for s in range(n, 0, -1):
        for S in itertools.combinations(range(n), s):
            if all(not (adj[u] >> v) & 1 for u, v in itertools.combinations(S, 2)):
                return s
    return 0


def check(cond, what):
    # explicit test, so that "python3 -O" does not skip it
    if not cond:
        raise SystemExit("selftest FAILED: " + what)


def must_reject(line, what):
    try:
        parse_graph6(line)
    except InputError:
        return
    raise SystemExit("selftest FAILED: accepted bad graph6 (%s)" % what)


def selftest():
    rnd = random.Random(1)
    for _ in range(300):
        n = rnd.randint(1, 13)
        adj = [0] * n
        for u in range(n):
            for v in range(u + 1, n):
                if rnd.random() < 0.3:
                    adj[u] |= 1 << v
                    adj[v] |= 1 << u
        check(alpha(adj) == brute_alpha(adj), "alpha vs brute force")
        check(parse_graph6(to_graph6(adj)) == adj, "graph6 round trip")
        tf = all(not ((adj[u] >> v) & 1 and (adj[v] >> w) & 1 and (adj[u] >> w) & 1)
                 for u, v, w in itertools.combinations(range(n), 3))
        check(triangle_free(adj) == tf, "triangle test vs brute force")
    # C5 and the Petersen graph
    c5 = [0] * 5
    for i in range(5):
        c5[i] |= 1 << ((i + 1) % 5) | 1 << ((i - 1) % 5)
    check(alpha(c5) == 2 and triangle_free(c5), "C5")
    check(parse_graph6(HEADER + "Dhc") == c5, "header strip")
    pet = [0] * 10
    edges = [(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)] + \
            [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    for u, v in edges:
        pet[u] |= 1 << v
        pet[v] |= 1 << u
    check(alpha(pet) == 4 and triangle_free(pet), "Petersen")
    for bad, what in [("Dhd", "nonzero padding"), ("Dhc~~~", "too long"), ("Dh", "too short"),
                      ("Dhc junk", "bad character"), (":Dh", "sparse6"), ("?", "n=0"),
                      ("~??Dhc", "long size field for n<63"), ("", "empty")]:
        must_reject(bad, what)
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description="Check (3,k)-graphs.")
    ap.add_argument("--k", type=int, default=10, help="require alpha < K (default 10)")
    ap.add_argument("--n", type=int, default=None, help="require exactly N vertices")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("file", nargs="?")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    if a.file is None:
        ap.error("FILE is required")
    if a.k < 1 or (a.n is not None and a.n < 1):
        ap.error("--k and --n must be positive")
    try:
        lines = [l for l in open(a.file).read().splitlines() if l.strip()]
        if lines and all(set(l.strip()) <= set("01 ") for l in lines):
            graphs = [parse_matrix(lines)]
        else:
            graphs = [parse_graph6(l) for l in lines]
        if not graphs:
            raise InputError("no graphs in %s" % a.file)
    except (InputError, OSError, UnicodeDecodeError) as e:
        print("ERROR: %s" % e)
        return 2
    allok = True
    for adj in graphs:
        ok = report(adj, a.k)
        if a.n is not None and len(adj) != a.n:
            print("  FAIL: n=%d, required n=%d" % (len(adj), a.n))
            ok = False
        allok &= ok
    print("%d graph(s) checked, all pass: %s" % (len(graphs), allok))
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
