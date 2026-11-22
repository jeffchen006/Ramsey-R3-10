#!/usr/bin/env python3
"""Build literal triangle-free role addbacks without using the SAT encoder."""

from collections import Counter
from itertools import combinations, product
from pathlib import Path
from sys import argv

from check_root_cover import graph, vertices


def addback(row):
    row_id, path_mask, mixed_mask, case, *hole_fields, encoded = row.split()
    old = graph.parse_graph6(encoded)
    adjacency = [set(vertices(neighbors)) for neighbors in old] + [set() for _ in range(13)]
    masks = int(path_mask), int(mixed_mask)
    active = tuple(set(vertices(mask)) for mask in masks)
    assert not (active[0] & active[1])
    stars, = ((first, second) for first, second in product(*active) if second in adjacency[first])
    pivots, roots = (29, 30), (27, 28)
    sides = tuple(anchors | {pivot} for anchors, pivot in zip(active, pivots, strict=True))
    kept = set(range(27)).difference(*active)
    outside = kept | set(range(31, 40))
    first_hole, second_hole, peer_left, peer_right = map(int, hole_fields)
    absent = ({(stars[0], pivots[0]), (min(active[0] - {stars[0]}), pivots[0])},
              {(first_hole, second_hole), (peer_left, peer_right)})
    degree_holes = Counter(vertex for pair in absent[1] for vertex in pair)
    assert (case == 'full-middle' and degree_holes[stars[1]] == 2
            or case == 'full-matching' and max(degree_holes.values()) == 1 and degree_holes[stars[1]] == 1)

    def edge(left, right):
        adjacency[left].add(right)
        adjacency[right].add(left)

    edge(*roots)
    common = tuple(range(31, 36))
    exclusive = ((36,), (37, 38, 39))
    for index, (side, pivot, root) in enumerate(zip(sides, pivots, roots, strict=True)):
        for anchor in side:
            edge(root, anchor)
        full = Counter({(anchor,): 4 for anchor in side})
        full.update(pair for pair in combinations(sorted(side), 2) if pair not in absent[index])
        observed = Counter(tuple(sorted(adjacency[vertex] & side)) for vertex in kept)
        assert not (observed - full)
        missing = tuple((full - observed).elements())
        own = sorted((support for support in missing if pivot in support),
                     key=lambda support: (stars[index] not in support, support))
        other = sorted(support for support in missing if pivot not in support)
        for vertex, support in zip((*common, *exclusive[index]), own, strict=True):
            for anchor in support:
                edge(vertex, anchor)
        for vertex, support in zip(exclusive[1-index], other, strict=True):
            for anchor in support:
                edge(vertex, anchor)
        assert Counter(tuple(sorted(adjacency[vertex] & side)) for vertex in outside) == full
    assert all(not adjacency[left] & adjacency[right] for left in range(40) for right in adjacency[left])
    assert tuple(len(adjacency[pivot]) for pivot in pivots) == (7, 9)
    assert sorted(len(adjacency[anchor]) for anchor in sides[0]) == [7, 8, 9, 9, 9]
    assert sorted(len(adjacency[anchor]) for anchor in sides[1]) == [8, 8, 8, 9, 9]
    assert len(adjacency[pivots[0]] & adjacency[pivots[1]]) == 5
    restored = set(range(40)).difference(pivots, *(adjacency[pivot] for pivot in pivots))
    assert restored == set(range(27))
    assert [sum(1 << vertex for vertex in adjacency[index] & restored) for index in range(27)] == old
    return row_id, case


if __name__ == '__main__':
    visits = Counter(addback(row)[1] for row in Path(argv[1]).read_text().splitlines())
    print('triangle-free addbacks (not MTF or alpha controls):', dict(visits))
