#!/usr/bin/env python3
"""Assign mixed strip roles on named residual-window sources."""

from argparse import ArgumentParser
from collections import Counter
from pathlib import Path

from canon_strip import validate
from check_root_cover import graph, vertices
from mixed_full_cover import choices as full_choices
from mixed_strip_cover import choices


def cover(rows, degree, minimum=None):
    for row in rows:
        row_id, first, second, encoded = row.split()
        first, second = int(first), int(second)
        adj = graph.parse_graph6(encoded)
        if minimum is not None:
            assert min(neighbors.bit_count() for neighbors in adj) == minimum
        outside = validate(adj, first, second)
        for path_mask, mixed_mask in ((first, second), (second, first)):
            active = tuple(vertices(mixed_mask))
            star, = (vertex for vertex in active if adj[vertex] & path_mask)
            blocks = (tuple(vertices(adj[vertex] & mixed_mask)) for vertex in outside)
            occupied = {block for block in blocks if len(block) == 2}
            for role in (choices if degree == 8 else full_choices)(active, star, occupied):
                yield (row_id, path_mask, mixed_mask, *role, encoded)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('degree', type=int, choices=(8, 9))
    parser.add_argument('--minimum', type=int)
    args = parser.parse_args()
    count = Counter()
    with args.input.open() as source, args.output.open('w') as output:
        for role in cover(source, args.degree, args.minimum):
            count[role[3]] += 1
            print(*role, file=output)
    print(dict(count))


if __name__ == '__main__':
    main()
