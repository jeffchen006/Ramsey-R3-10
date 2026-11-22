#!/usr/bin/env python3
"""Enumerate ordered mixed roles with a noncross degree-nine pivot."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations, product
from pathlib import Path

from canon_strip import validate
from check_root_cover import graph, vertices


def choices(active, star, occupied):
    eligible = [pair for pair in combinations(active, 2) if pair not in occupied]
    for first, second in combinations(eligible, 2):
        if not set(first).intersection(second) and star in (*first, *second):
            yield 'full-matching', *first, *second
        if star in first and star in second:
            yield 'full-middle', *first, *second


def test_choices():
    active = (0, 2, 3, 5)
    pivot = 6
    pairs = tuple(combinations(active, 2))
    visits = Counter()
    for occupied_mask, star in product(range(1 << len(pairs)), active):
        occupied = {pair for index, pair in enumerate(pairs) if occupied_mask >> index & 1}
        expect = []
        for first, second in combinations(combinations((*active, pivot), 2), 2):
            if pivot in (*first, *second) or first in occupied or second in occupied:
                continue
            degree = Counter((*first, *second))
            if degree[star] == 2:
                expect.append(('full-middle', *first, *second))
            if degree[star] and max(degree.values()) == 1:
                expect.append(('full-matching', *first, *second))
        assert sorted(expect) == sorted(choices(active, star, occupied))
        visits[bool(expect)] += 1
    print('mixed full local oracle', dict(visits), flush=True)


def extract(keys, output):
    counts = Counter()
    with output.open('w') as stream:
        for row in keys.read_text().splitlines():
            row_id, first, second, encoded = row.split()
            first, second = int(first), int(second)
            adj = graph.parse_graph6(encoded)
            assert len(adj) == 27
            outside = validate(adj, first, second)
            for path_mask, mixed_mask in ((first, second), (second, first)):
                active = tuple(vertices(mixed_mask))
                star, = (vertex for vertex in active if adj[vertex] & path_mask)
                occupied = {tuple(vertices(adj[vertex] & mixed_mask)) for vertex in outside
                            if (adj[vertex] & mixed_mask).bit_count() == 2}
                for role in choices(active, star, occupied):
                    counts[role[0]] += 1
                    print(row_id, path_mask, mixed_mask, *role, encoded, file=stream)
    print('mixed full target', dict(counts), flush=True)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('keys', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    test_choices()
    extract(args.keys, args.output)
