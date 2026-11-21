#!/usr/bin/env python3
"""Extract the full marked mixed-pivot j=4 source from the paired j=3 keys."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations, product
from pathlib import Path

from canon_strip import validate
from check_root_cover import graph, vertices


def choices(active, star, occupied):
    for first, second in combinations(active, 2):
        if (first, second) in occupied:
            continue
        for peer in active:
            if peer not in (first, second) and star in (first, second, peer):
                yield 'matching', first, second, peer
            if peer == star and star in (first, second):
                yield 'middle', first, second, peer


def brute_choices(active, star, occupied):
    pivot = max(active) + 1
    count = Counter()
    for pair in combinations((*active, pivot), 2):
        count[pair] = 1
    for holes in combinations(count, 2):
        pivot_hole = [pair for pair in holes if pivot in pair]
        if len(pivot_hole) != 1 or any(pair in occupied for pair in holes):
            continue
        first, second = next(pair for pair in holes if pivot not in pair)
        peer, _ = pivot_hole[0]
        degree = Counter(vertex for pair in holes for vertex in pair)
        if not degree[star]:
            continue
        if max(degree.values()) == 1:
            yield 'matching', first, second, peer
        elif max(degree.values()) == 2 and degree[star] == 2:
            yield 'middle', first, second, peer


def control():
    active = (0, 2, 3, 5)
    pairs = tuple(combinations(active, 2))
    positive = negative = 0
    for mask, star in product(range(1 << len(pairs)), active):
        occupied = {pair for idx, pair in enumerate(pairs) if mask >> idx & 1}
        expect = sorted(brute_choices(active, star, occupied))
        assert expect == sorted(choices(active, star, occupied))
        positive += bool(expect)
        negative += not expect
    print(f'width-4 local oracle: {positive} positive and {negative} negative snapshots')


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('keys', type=Path, nargs='?')
    parser.add_argument('output', type=Path, nargs='?')
    args = parser.parse_args()
    control()
    if not args.keys:
        return
    stats = Counter()
    with args.output.open('w') as output:
        for row in args.keys.read_text().splitlines():
            row_id, first, second, encoded = row.split()
            first, second = int(first), int(second)
            adj = graph.parse_graph6(encoded)
            outside = validate(adj, first, second)
            stats['input_marks'] += 1
            for path_mask, mixed_mask in ((first, second), (second, first)):
                active = tuple(vertices(mixed_mask))
                star, = (vertex for vertex in active if adj[vertex] & path_mask)
                occupied = {tuple(vertices(adj[vertex] & mixed_mask)) for vertex in outside
                            if (adj[vertex] & mixed_mask).bit_count() == 2}
                accepted = list(choices(active, star, occupied))
                stats['oriented_marks'] += bool(accepted)
                for case, first_hole, second_hole, peer in accepted:
                    stats[case] += 1
                    print(row_id, path_mask, mixed_mask, case, first_hole, second_hole, peer, encoded, file=output)
    print(dict(stats))


if __name__ == '__main__':
    main()
