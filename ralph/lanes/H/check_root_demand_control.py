#!/usr/bin/env python3
"""Calibrate the local demand/attachment predicates on known small graphs."""

from collections import Counter
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from check_graph import alpha, parse_graph6, triangle_free


def cycle(size):
    return [{(vertex-1) % size, (vertex+1) % size} for vertex in range(size)]


def root_local(neighbors, root):
    exterior = set(range(len(neighbors))) - {root} - neighbors[root]
    attachments = {anchor: neighbors[anchor] & exterior for anchor in neighbors[root]}
    demands = [(vertex,) for vertex in sorted(exterior)]
    demands += [(left, right) for left, right in combinations(sorted(exterior), 2)
                if right not in neighbors[left] and not (neighbors[left] & neighbors[right] & exterior)]
    cover = {demand: {anchor for anchor, attached in attachments.items() if set(demand) <= attached}
             for demand in demands}
    return exterior, attachments, cover


def audit(neighbors, root, counts):
    exterior, attachments, cover = root_local(neighbors, root)
    for attached in attachments.values():
        assert all(not (neighbors[vertex] & attached) for vertex in attached)
        assert all(vertex in attached or neighbors[vertex] & attached for vertex in exterior)
    assert all(cover.values())
    counts['roots'] += 1
    counts['singletons'] += len(exterior)
    counts['pairs'] += len(cover) - len(exterior)
    for first, second in combinations(cover, 2):
        if any(other in neighbors[vertex] for vertex in first for other in second):
            assert cover[first].isdisjoint(cover[second])
            counts['incompatible'] += 1


def main():
    counts = Counter()
    for root in range(5):
        audit(cycle(5), root, counts)
    assert counts == {'roots': 5, 'singletons': 10, 'pairs': 0, 'incompatible': 5}
    assert not root_local(cycle(6), 0)[2][(3,)]
    assert not root_local(cycle(7), 0)[2][(2, 5)]
    print('C5: five tight two-demand controls. Non-MTF C6/C7: uncovered singleton/pair.')

    controls = [parse_graph6(line) for line in (ROOT / 'gluing/val/r3_7_22.g6').read_text().splitlines()]
    controls = [adj for adj in controls if all(mask.bit_count() == 6 for mask in adj)]
    assert len(controls) == 10
    counts.clear()
    for adj in controls:
        assert len(adj) == 22 and alpha(adj) == 6 and triangle_free(adj)
        neighbors = [{vertex for vertex in range(len(adj)) if mask >> vertex & 1} for mask in adj]
        assert all(right in neighbors[left] or neighbors[left] & neighbors[right]
                   for left, right in combinations(range(22), 2))
        for root in range(22):
            audit(neighbors, root, counts)
    assert counts['roots'] == 220 and counts['pairs'] > 0 and counts['incompatible'] > 0
    print('Ten known 6-regular (3,7,22) classes:', dict(counts))


if __name__ == '__main__':
    main()
