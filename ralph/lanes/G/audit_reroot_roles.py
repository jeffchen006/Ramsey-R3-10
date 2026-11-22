#!/usr/bin/env python3
"""Bind B roles with a five-anchor hole-pair oracle, without the scheduler."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations
from pathlib import Path

from check_root_cover import graph, vertices


def expected(source):
    roster = set()
    for line in source.read_text().splitlines():
        parent_id, compact, wide, encoded = line.split()
        small, large = int(compact), int(wide)
        adj = graph.parse_graph6(encoded)
        outside = tuple(vertex for vertex in range(21) if not ((small | large) >> vertex & 1))
        cross, = (anchor for anchor in vertices(small) if adj[anchor] & large)
        contacts = Counter(adj[vertex] & small for vertex in outside)
        expected_contacts = Counter(1 << anchor for anchor in vertices(small) for _ in range(4))
        expected_contacts.update((1 << left) | (1 << right) for left, right in combinations(vertices(small), 2))
        expected_contacts[1 << cross] -= 1
        assert contacts == expected_contacts and len(outside) == 14
        same = [*vertices(small), 21, 22]
        hole_candidates = [frozenset(pair) for pair in combinations(same, 2) if max(pair) >= 21]
        for holes in combinations(hole_candidates, 2):
            if any(sum(pivot in hole for hole in holes) != 1 for pivot in (21, 22)):
                continue
            first, = (next(iter(hole - {21})) for hole in holes if 21 in hole)
            second, = (next(iter(hole - {22})) for hole in holes if 22 in hole)
            if first == second == cross:
                shape = 'middle'
            elif first != second and cross in (first, second):
                shape = 'matching'
            else:
                continue
            for overlap in (0, 1):
                if overlap and first > second:
                    continue
                kind = f'B.{25 + overlap}.{shape}'
                key = f'{parent_id}_{compact}_{wide}_{shape}_{first}_{second}_{overlap}'
                row = (kind, key, str(overlap))
                assert row not in roster
                roster.add(row)
    return roster


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('shell_map', type=Path)
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    roster = expected(args.source)
    from_map = [tuple(row.split()[:3]) for row in args.shell_map.read_text().splitlines() if row.startswith('B.')]
    assert len(from_map) == len(roster) and set(from_map) == roster
    counts = Counter(key[0] for key in roster)
    for kind in sorted(counts):
        print(kind, counts[kind])
    args.out.write_text(''.join(' '.join(key) + '\n' for key in sorted(roster) if key[0].endswith('middle')))


if __name__ == '__main__':
    main()
