#!/usr/bin/env python3
"""Verify the paired-window inequalities on known small graphs."""

from pathlib import Path
from sys import argv

from check_root_cover import graph
from test_strip_window import brute, decode


def controls(catalogue, extremals):
    cases = 0
    for line in catalogue.read_text().splitlines():
        marks = brute(line, 2, 2, True)
        if not marks:
            continue
        adj = decode(line)
        independence = graph.alpha(graph.parse_graph6(line))
        edges_twice = sum(map(len, adj))
        universe = set(range(len(adj)))
        for mask_first, mask_second in marks:
            sides = [{vertex for vertex in universe if mask >> vertex & 1} for mask in (mask_first, mask_second)]
            exterior = universe - set.union(*sides)
            expected = 0
            for side in sides:
                signatures = {tuple(sorted(side & adj[vertex])) for vertex in exterior}
                missing_double = int(not any(len(signature) == 2 for signature in signatures))
                assert sum(len(adj[vertex]) for vertex in side) == 6 - missing_double
                expected += 6 - missing_double
            assert edges_twice <= expected + independence * len(exterior)
            for vertex in exterior:
                assert edges_twice <= expected + independence * (len(exterior)-1) + len(adj[vertex])
            cases += 1
    assert cases == 21
    print(f'{cases} exact degree sums and exterior-corrected bounds')

    for line in extremals.read_text().splitlines():
        adj = decode(line)
        exclusive_vertices = 0
        for left in range(len(adj)):
            for right in range(left):
                if left in adj[right]:
                    continue
                for own, opposite in ((left, right), (right, left)):
                    for vertex in adj[own] - adj[opposite]:
                        assert adj[vertex] & (adj[opposite] - adj[own])
                        exclusive_vertices += 1
        print(f'n={len(adj)}: {exclusive_vertices} exclusive vertices have opposite witnesses')


if __name__ == '__main__':
    controls(Path(argv[1]), Path(argv[2]))
