#!/usr/bin/env python3
"""Compare exact two-edge swaps to a brute-force labeled oracle."""

from itertools import combinations
from pathlib import Path
import sys

from calibrate_window74 import edge_set, oracle, run
from involution_sat import from_graph6


totals = []
for row in Path(sys.argv[1]).read_text().splitlines():
    adj = from_graph6(row)
    alpha = 3
    domain = range(len(adj))
    edges = edge_set(adj)
    absent = set(combinations(domain, 2)) - edges
    tri, ind = (tuple(frozenset(combinations(subset, 2)) for subset in combinations(domain, count))
                for count in (3, alpha+1))
    assert oracle(edges, tri, ind)
    expected = set()
    for removed in combinations(edges, 2):
        punctured = edges - set(removed)
        if oracle(punctured, tri, ind):
            continue
        for inserted in combinations(absent, 2):
            edited = punctured | set(inserted)
            if oracle(edited, tri, ind):
                expected.add(edited)
    actual = run('./twoswap74', [alpha], row, len(adj))
    assert set(actual) == expected and len(actual) == len(expected)
    totals.append(len(expected))
assert totals and sum(totals)
print(f'{len(totals)} exact smaller (3,4;8) two-edge-swap controls: {totals}')
