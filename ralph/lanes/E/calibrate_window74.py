#!/usr/bin/env python3
"""Compare independent labeled triangle/alpha oracles to edge deletion and star moves."""

from itertools import combinations
from pathlib import Path
import subprocess
import sys

from involution_sat import from_graph6, to_graph6


def edge_set(graph):
    return frozenset((left, right) for left, right in combinations(range(len(graph)), 2)
                     if graph[left] >> right & 1)


def oracle(edges, tri, ind):
    return not any(test <= edges for test in tri) and all(test & edges for test in ind)


def run(program, args, row, order):
    result = subprocess.run([program, *map(str, args)], input=row + '\n', text=True,
                            capture_output=True, check=True, timeout=5)
    assert all(len(from_graph6(line)) == order for line in result.stdout.splitlines())
    return [edge_set(from_graph6(line)) for line in result.stdout.splitlines()]


def calibrate():
    rows = Path(sys.argv[1]).read_text().splitlines()
    stats = [0, 0, 0, 0, 0, 0]
    for row in rows:
        adj = from_graph6(row)
        alpha = 4
        domain = range(len(adj))
        edges = edge_set(adj)
        assert to_graph6(adj) == row
        tri, ind = (tuple(frozenset(combinations(subset, 2)) for subset in combinations(domain, count))
                    for count in (3, alpha+1))
        assert oracle(edges, tri, ind)
        deleted = [edges - {edge} for edge in edges if oracle(edges - {edge}, tri, ind)]
        actual = run('./edge_down74', [alpha], row, len(adj))
        assert set(actual) == set(deleted) and len(actual) == len(deleted)
        stats[0] += len(deleted)
        for idx, (radius, delta) in enumerate(((1, 0), (2, 0), (4, 0), (4, 1), (4, -1)), 1):
            expected = []
            for pivot, neighbors in enumerate(adj):
                pinned = frozenset(edge for edge in edges if pivot not in edge)
                target = neighbors.bit_count() + delta
                if not 0 <= target <= alpha:
                    continue
                for new in combinations((vert for vert in domain if vert != pivot), target):
                    added = sum(not (neighbors >> vert & 1) for vert in new)
                    if int(delta == 0) <= added <= radius:
                        edit = pinned | {tuple(sorted((pivot, vert))) for vert in new}
                        if oracle(edit, tri, ind):
                            expected.append(edit)
            actual = run('./star74', [alpha, radius, delta], row, len(adj))
            assert set(actual) == set(expected) and len(actual) == len(expected)
            stats[idx] += len(actual)
    assert all(stats)
    print(f'{len(rows)} (3,5;11) controls; exact labeled oracle totals (down, star r1/r2/r4/+1/-1): {stats}')


if __name__ == '__main__':
    calibrate()
