"""Independently bind every physical ID4 marking in a canonical stem source."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path

from high_r24_lift import find_rows
from paircut_r23 import decode, independent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stems', type=Path)
    parser.add_argument('plan', type=Path)
    args = parser.parse_args()
    graphs = args.stems.read_text().splitlines()
    assert graphs == sorted(set(graphs))
    counts = Counter()
    marked_counts = Counter()
    population = []
    for stem in graphs:
        size, edges = decode(stem)
        assert size == 20 and 44 <= len(edges) <= 49
        edge_set = set(edges)
        assert not any(all(pair in edge_set for pair in combinations(triple, 2))
                       for triple in combinations(range(size), 3))
        assert next(independent(tuple(range(size)), edge_set, 7), None) is None
        rows = tuple(find_rows(stem))
        assert rows
        counts[len(edges)] += 1
        marked_counts[len(edges)] += len(rows)
        population.extend((len(edges), stem, row) for row in rows)
    with args.plan.open('w') as out:
        for rank, (edges, stem, row) in enumerate(sorted(population), 1):
            print(rank, edges, ','.join(map(str, row)), stem, sep='\t', file=out)
    for level in range(44, 50):
        print(f'e={level} stems={counts[level]} marked={marked_counts[level]}')


if __name__ == '__main__':
    main()
