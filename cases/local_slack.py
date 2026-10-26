#!/usr/bin/env python3
"""Tightness of the independent-set hierarchy (Lemma H in notes/cases_local.md) on real graphs.

For a (3,k)-graph G (triangle-free, alpha < k) and an independent set I with |I| = s,
X_I = V - I - N(I) is triangle-free with alpha(X_I) < k - s, so
    |X_I| <= R(3,k-s) - 1   and   e(X_I) >= e(3,k-s,|X_I|).
This script reports, for each s, the minimum slack e(X_I) - e(3,k-s,|X_I|) over all
independent s-sets, and how many sets reach slack 0, 1, 2.
Usage: tools/venv/bin/python cases/local_slack.py FILE.g6 [--k 10] [--smax 3] [--limit N]
"""
import argparse
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
import networkx as nx
from etables import e3


def indep_sets(adj, n, s):
    """All independent s-sets as sorted tuples (adj = list of neighbour bitmasks)."""
    def rec(start, chosen, forbid):
        if len(chosen) == s:
            yield tuple(chosen)
            return
        for v in range(start, n):
            if not (forbid >> v) & 1:
                yield from rec(v + 1, chosen + [v], forbid | adj[v] | (1 << v))
    yield from rec(0, [], 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--smax", type=int, default=3)
    ap.add_argument("--limit", type=int, default=10 ** 9)
    a = ap.parse_args()
    tot = {s: Counter() for s in range(1, a.smax + 1)}
    size = {s: Counter() for s in range(1, a.smax + 1)}
    sizebad = 0
    ng = 0
    for line in open(a.file):
        line = line.strip()
        if line.startswith(">>graph6<<"):
            line = line[10:]
        if not line:
            continue
        ng += 1
        if ng > a.limit:
            break
        G = nx.from_graph6_bytes(line.encode())
        n = G.number_of_nodes()
        adj = [0] * n
        for u, v in G.edges():
            adj[u] |= 1 << v
            adj[v] |= 1 << u
        for s in range(1, a.smax + 1):
            for I in indep_sets(adj, n, s):
                cover = 0
                for v in I:
                    cover |= adj[v] | (1 << v)
                X = [v for v in range(n) if not (cover >> v) & 1]
                xm = 0
                for v in X:
                    xm |= 1 << v
                eX = sum(bin(adj[v] & xm).count("1") for v in X) // 2
                lb = e3(a.k - s, len(X))
                size[s][len(X)] += 1
                if lb is None:
                    sizebad += 1
                    continue
                tot[s][min(eX - lb, 9)] += 1
    print(f"graphs: {ng if ng <= a.limit else a.limit}; size-bound violations: {sizebad}")
    for s, c in tot.items():
        print(f"s={s}: slack histogram (9 = >=9): {dict(sorted(c.items()))}")
        print(f"     |X| histogram: {dict(sorted(size[s].items()))}")


if __name__ == "__main__":
    main()
