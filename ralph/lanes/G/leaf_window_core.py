#!/usr/bin/env python3
"""Check the seven surviving marked anchors after deleting a low-degree mark."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations
from pathlib import Path

from check_root_cover import graph, vertices


def support_ok(adj, region, side, private):
    patterns = Counter(adj[vertex] & side for vertex in vertices(region))
    return bool(patterns) and all(1 <= mask.bit_count() <= 2 and count <= (private if mask.bit_count() == 1 else 1)
                                  for mask, count in patterns.items())


def masks(adj, large_size, small_size, private, stats):
    universe = (1 << len(adj)) - 1
    for group in combinations(range(len(adj)), large_size):
        large = sum(1 << vertex for vertex in group)
        if any(adj[vertex] & large for vertex in group):
            continue
        stats['independent large'] += 1
        touch = 0
        for vertex in group:
            touch |= adj[vertex]
        other = universe ^ (large | touch)
        if other.bit_count() != small_size - 1 or any(adj[vertex] & other for vertex in vertices(other)):
            continue
        for star in vertices(touch):
            if (adj[star] & large).bit_count() != 1 or adj[star] & other:
                continue
            stats['preliminary pairs'] += 1
            small = other | (1 << star)
            outside = universe ^ (large | small)
            if support_ok(adj, outside, large, private) and support_ok(adj, outside, small, private):
                stats['retained pairs'] += 1
                yield (small, large)


def simple(adj, large_size, small_size, private):
    universe = (1 << len(adj)) - 1
    out = set()
    for anchors in combinations(range(len(adj)), small_size + large_size):
        edges = [(left, right) for left, right in combinations(anchors, 2) if adj[left] >> right & 1]
        if len(edges) != 1:
            continue
        total = sum(1 << vertex for vertex in anchors)
        for group in combinations(anchors, small_size):
            if sum(vertex in group for vertex in edges[0]) != 1:
                continue
            small = sum(1 << vertex for vertex in group)
            large = total ^ small
            if all(support_ok(adj, universe ^ total, side, private) for side in (small, large)):
                out.add((small, large))
    return out


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('controls', type=Path)
    parser.add_argument('cores', type=Path)
    args = parser.parse_args()
    stats = Counter()
    count = 0
    for row in args.controls.read_text().splitlines():
        adj = graph.parse_graph6(row)
        assert set(masks(adj, 2, 2, 2, stats)) == simple(adj, 2, 2, 2)
        count += 1
    assert count == 410 and stats['retained pairs'] == 42
    print('smaller marked control', count, dict(stats))

    stats = Counter()
    count = 0
    for row in args.cores.read_text().splitlines():
        adj = graph.parse_graph6(row)
        assert len(adj) == 22 and graph.triangle_free(adj) and graph.alpha(adj) == 6
        for pair in masks(adj, 4, 3, 4, stats):
            print(count + 1, *pair, row)
        count += 1
    assert count == 191
    print('full order22 core list', count, dict(stats), flush=True)


if __name__ == '__main__':
    main()
