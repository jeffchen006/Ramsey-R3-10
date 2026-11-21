#!/usr/bin/env python3
"""Small exact controls of the cross-neighborhood argument."""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
from check_graph import brute_alpha, triangle_free


def link(graph, first, second, offset):
    for phase in range(3):
        left, right = 3*first + phase, 3*second + (phase + offset) % 3
        graph[left] |= 1 << right
        graph[right] |= 1 << left


def induced(graph, vertices):
    vertices = sorted(vertices)
    return [sum(1 << index for index, right in enumerate(vertices) if graph[left] >> right & 1)
            for left in vertices]


def main():
    circulant = [sum(1 << ((v+step) % 35) for step in (1, 7, 11, 16, 19, 24, 28, 34))
                 for v in range(35)]
    sigma = [11*v % 35 for v in range(35)]
    assert triangle_free(circulant)
    fixed = {v for v in range(35) if sigma[v] == v}
    moving = set(range(35)) - fixed
    assert len(fixed) == 5 and len(moving) == 30
    for left, right in combinations(range(35), 2):
        assert circulant[left] >> right & 1 == circulant[sigma[left]] >> sigma[right] & 1
    shapes = Counter()
    for v in moving:
        orbit = {v, sigma[v], sigma[sigma[v]]}
        neighbors = {u for u in range(35) if any(circulant[w] >> u & 1 for w in orbit)}
        attach = len(fixed & neighbors)
        moved_neighbors = neighbors & moving
        assert not orbit & neighbors and len(moved_neighbors) % 3 == 0
        assert all(not (circulant[u] >> w & 1) for u in fixed & neighbors for w in moved_neighbors)
        assert 35-3-attach-len(moved_neighbors) <= 17
        assert 17 <= len(moved_neighbors) <= 27 and attach == 1
        shapes[attach, len(moved_neighbors)] += 1
    print('C35 independent-cross-neighborhood check:', dict(shapes))

    pairs = list(combinations(range(4), 2))
    counts = Counter()
    shape = None
    for shifts in product(range(1, 4), repeat=len(pairs)):
        graph = [0] * 12
        for (first, second), mask in zip(pairs, shifts):
            for offset in (1, 2):
                if mask >> (offset - 1) & 1:
                    link(graph, first, second, offset)
        if triangle_free(graph):
            independence = brute_alpha(graph)
            counts[independence, shifts.count(3)] += 1
            if independence <= 4:
                shape = graph
                assert all(row.bit_count() == 4 for row in graph)
                assert all(brute_alpha(induced(graph, [v for v in range(12) if v//3 != orbit])) == 4
                           for orbit in range(4))
    assert counts == {(4, 2): 6, (5, 0): 24, (5, 1): 36}
    print('Triangle-free order-12 candidates (alpha, #double):', dict(sorted(counts.items())))

    passing = 0
    for pattern in product(range(3), repeat=4):
        graph = shape.copy() + [0, 0, 0]
        for orbit, offset in enumerate(pattern):
            link(graph, 4, orbit, offset)
        if triangle_free(graph):
            passing += 1
            residual = induced(graph, [v for v in range(12) if not any(graph[j] >> v & 1 for j in (13, 14))])
            assert len(residual) == 4 and all(not row for row in residual)
    assert passing == 6
    print(f'{passing}/81 triangle-free single-matching controls all leave an independent four-set')


if __name__ == '__main__':
    main()
