#!/usr/bin/env python3
"""Puncture a known window family, or audit the exact two-vertex lift."""

from itertools import combinations
from pathlib import Path
import argparse
import subprocess

from calibrate_window74 import edge_set, oracle
from involution_sat import from_graph6, to_graph6
from involution_cores import graph


def project(adj, removed):
    keep = tuple(vert for vert in range(len(adj)) if vert not in removed)
    edges = [(left, right) for left, right in combinations(range(len(keep)), 2) if adj[keep[left]] >> keep[right] & 1]
    return graph(len(keep), edges)


def calibrate(raw):
    controls = set()
    for row in raw:
        adj = from_graph6(row)
        for pair in ((0, 1), (2, 3)):
            controls.add(to_graph6(project(adj, pair)))
    totals = []
    for row in sorted(controls)[:32]:
        adj = from_graph6(row)
        order = len(adj)
        assert order == 9
        fixed = edge_set(adj)
        all_edges = tuple(combinations(range(order+2), 2))
        variable = tuple(edge for edge in all_edges if edge[1] >= order)
        triangle = tuple(frozenset(combinations(subset, 2)) for subset in combinations(range(order+2), 3))
        independent = tuple(frozenset(combinations(subset, 2)) for subset in combinations(range(order+2), 5))
        candidate = tuple(tuple(vert for vert in range(order) if mask >> vert & 1)
                          for mask in range(1 << order) if mask.bit_count() <= 4 and not any(
                              adj[left] >> right & 1 for left, right in combinations(
                                  (vert for vert in range(order) if mask >> vert & 1), 2)))

        def swapclass(edges):
            permutation = tuple(range(order)) + (order+1, order)
            return min(edges, frozenset(tuple(sorted((permutation[left], permutation[right]))) for left, right in edges),
                       key=lambda val: tuple(sorted(val)))

        low = set(variable)
        for gap in (3, 6, 8):
            expected = set()
            for left, first in enumerate(candidate):
                for second in candidate[left:]:
                    for edge in (0, 1):
                        if len(first) + len(second) + edge != gap:
                            continue
                        choices = {(vert, order) for vert in first} | {(vert, order+1) for vert in second}
                        if edge:
                            choices.add((order, order+1))
                        assert choices <= low
                        result = fixed | choices
                        if oracle(result, triangle, independent):
                            expected.add(swapclass(result))
            run = subprocess.run(['./pairlift74', '4', str(len(fixed) + gap)], input=row+'\n',
                                 text=True, capture_output=True, check=True, timeout=5)
            result = [swapclass(edge_set(from_graph6(line))) for line in run.stdout.splitlines()]
            assert expected == set(result) and len(result) == len(expected), (row, gap)
            totals.append(len(expected))
    assert len(totals) == 96 and sum(totals) and 0 in totals
    print(f'{len(totals)} exact smaller controls: {sum(totals)} solutions, {totals.count(0)} impossible inputs')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('calibrate', 'puncture'))
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    raw = args.path.read_text(encoding='ascii').splitlines()
    if args.mode == 'calibrate':
        calibrate(raw)
    else:
        import sys
        for row in raw:
            adj = from_graph6(row)
            for pair in combinations(range(len(adj)), 2):
                print(to_graph6(project(adj, pair)))


if __name__ == '__main__':
    main()
