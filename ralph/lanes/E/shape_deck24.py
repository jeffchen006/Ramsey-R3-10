#!/usr/bin/env python3
"""Isomorphism-invariant high-degree shape screen for all-missing e8 decks."""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
from time import process_time

from cubic32 import pin_graph
from involution_cores import bits, graph
from involution_sat import from_graph6


def identify(adj, keep):
    remaining = keep
    components = []
    while remaining:
        todo = remaining & -remaining
        count = valency_sum = 0
        while todo:
            bit = todo & -todo
            todo ^= bit
            remaining ^= bit
            site = bit.bit_length()-1
            valency = (adj[site] & keep).bit_count()
            if valency > 2:
                return None
            valency_sum += valency
            count += 1
            todo |= adj[site] & remaining
        assert valency_sum in (2*count, 2*(count-1))
        components.append((count, valency_sum == 2*count))
    return tuple(sorted(components))


def anchors(core, groups, high_count):
    domains = tuple(sum(1 << v for v in range(8) if sum(col >> v & 1 for col in group) == 1) for group in groups)
    return {identify(core, mask) for mask in domains if mask.bit_count() == high_count}


def options(core, groups, residue, high_count, cap=3):
    shapes = anchors(core, groups, high_count)
    keep = sum(1 << v for v in range(8) if residue[v] == 0)
    missing = high_count - keep.bit_count()
    assert 0 <= missing <= 2
    if not shapes:
        return None
    if len(shapes) != 1:
        return ()
    goal, = shapes
    pinned, parts = pin_graph(core, groups)
    sites = []
    for own, part in enumerate(parts):
        for vertex in part:
            word = pinned[vertex]
            can_reach = word.bit_count() + sum(min(cap, sum(not (word & pinned[other]) for other in other_part))
                                              for index, other_part in enumerate(parts) if index != own)
            if can_reach >= 7:
                sites.append((own, vertex))
    accepted = []
    for choice in combinations(sites, missing):
        marked = tuple(vertex for _, vertex in choice)
        high_mask = keep | sum(1 << vertex for vertex in marked)
        if len(marked) != 2:
            if identify(pinned, high_mask) == goal:
                accepted.append(marked)
            continue
        (first_group, left), (second_group, right) = choice
        if first_group == second_group or pinned[left] & pinned[right]:
            continue
        joined = list(pinned)
        joined[left] |= 1 << right
        joined[right] |= 1 << left
        if identify(joined, high_mask) == goal:
            accepted.append(marked)
    return tuple(accepted)


def control():
    import pynauty
    controls = Counter()
    for order in range(1, 7):
        relabels = {}
        pool = tuple(combinations(range(order), 2))
        for links in range(min(order+1, len(pool)+1)):
            for chosen in combinations(pool, links):
                adj = graph(order, chosen)
                signature = identify(adj, (1 << order)-1)
                if signature is None:
                    assert max(row.bit_count() for row in adj) > 2
                    controls['rejected_valency'] += 1
                    continue
                exact = pynauty.certificate(pynauty.Graph(order, adjacency_dict={v: list(bits(row)) for v, row in enumerate(adj)}))
                if signature in relabels:
                    assert relabels[signature] == exact
                else:
                    assert exact not in relabels.values()
                    relabels[signature] = exact
                controls['max_degree2_labelled'] += 1
        controls['max_degree2_classes'] += len(relabels)
    circ = graph(13, [(v, (v+shift) % 13) for v in range(13) for shift in (1, 5)])
    for shift in range(13):
        mask = ((1 << 13)-1) ^ sum(1 << ((shift+v) % 13) for v in (0, 1, 6))
        histogram = Counter((row & mask).bit_count() for v, row in enumerate(circ) if mask >> v & 1)
        maxdegree = max(histogram)
        marked = sum(1 << v for v, row in enumerate(circ) if mask >> v & 1 and (row & mask).bit_count() == maxdegree)
        shape = identify(circ, marked)
        if shift == 0:
            expected = (histogram, shape)
        assert (histogram, shape) == expected
        controls['translated_cards'] += 1
    assert expected[1] is not None
    print('shape controls', dict(controls), 'C13 shape', expected[1], flush=True)


def sample(plan, indexes):
    rows = plan.read_bytes().splitlines()
    sizes = Counter()
    for index in map(int, indexes.read_text().split()):
        key, groups, residue, high = json.loads(rows[index])
        core = tuple(from_graph6(key))
        result = options(core, groups, residue, high)
        assert result is not None
        sizes[len(result)] += 1
        print(index, len(result), json.dumps(result, separators=(',', ':')))
    print('anchors sample', dict(sorted(sizes.items())), process_time(), 'CPU-s', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--indexes', type=Path)
    args = parser.parse_args()
    if args.plan is None:
        control()
    else:
        sample(args.plan, args.indexes)
