#!/usr/bin/env python3
"""Degree-class projection using the actual paired window adjacency."""

from argparse import ArgumentParser
from collections import Counter
from functools import cache
from itertools import combinations, product
from pathlib import Path
from time import process_time

from check_root_cover import graph, vertices


def independent_bound(adj):
    @cache
    def solve(mask):
        if not mask:
            return 0
        vertex = max(vertices(mask), key=lambda index: (adj[index] & mask).bit_count())
        left = mask ^ (1 << vertex)
        return max(solve(left), 1 + solve(left & ~adj[vertex]))
    return solve


def degree_ceiling(adj, independent, support, survivor_mask, possible_cross):
    available = survivor_mask
    for anchor in vertices(support & ((1 << len(adj)) - 1)):
        available &= ~adj[anchor]
    return support.bit_count() + independent(available) + possible_cross


def missing(adj, side, survivor_mask):
    anchors = tuple(vertices(side))
    wanted = Counter({1 << anchor: 4 for anchor in anchors})
    wanted.update((1 << first) | (1 << second) for first, second in combinations(anchors, 2))
    observed = Counter(adj[vertex] & side for vertex in vertices(survivor_mask))
    assert not (observed - wanted)
    return sorted((wanted - observed).elements())


def advance(states, options):
    return {(used_left | left, used_right | right, lows + int(degree == 7), mids + int(degree == 8))
            for used_left, used_right, lows, mids in states
            for left, right, cap, singleton in options
            if not (used_left & left or used_right & right)
            and (used_left | left).bit_count() <= 2 and (used_right | right).bit_count() <= 2
            for degree in range(7 if singleton else 8, min(9, cap) + 1)
            if lows + int(degree == 7) <= 6 and mids + int(degree == 8) <= 2}


def feasible(row):
    _, first, second, encoded = row.split()
    sides = int(first), int(second)
    adj = graph.parse_graph6(encoded)
    shared = len(adj)-24
    survivor_mask = ((1 << len(adj)) - 1) ^ sides[0] ^ sides[1]
    stars = tuple(next(anchor for anchor in vertices(side) if adj[anchor] & other)
                  for side, other in (sides, sides[::-1]))
    peers = tuple((0, *(1 << anchor for anchor in vertices(side ^ (1 << star))))
                  for side, star in zip(sides, stars, strict=True))
    centers = 1 << len(adj), 1 << (len(adj)+1)
    left_missing, right_missing = tuple(missing(adj, side, survivor_mask) for side in sides)
    assert len(left_missing) == len(right_missing) == 6-shared
    independent = independent_bound(adj)
    common = list(product(peers[0], peers[1]))
    left_groups = [[(left, 0, other) for left in peers[0]] for other in right_missing]
    right_groups = [[(0, right, other) for right in peers[1]] for other in left_missing]

    states = {(0, 0, 0, 0)}
    common_options = [(left, right, degree_ceiling(adj, independent, centers[0] | centers[1] | left | right,
                                                  survivor_mask, 0), not (left | right))
                      for left, right in common]
    for _ in range(shared):
        states = advance(states, common_options)
    for index, groups in enumerate((left_groups, right_groups)):
        for group in groups:
            options = []
            for left, right, other in group:
                extra = left | right
                fixed_cross = left_missing if index == 0 else right_missing
                possible_cross = sum(not (support & extra) for support in fixed_cross)
                support = centers[index] | other | extra
                cap = degree_ceiling(adj, independent, support, survivor_mask, possible_cross)
                options.append((left, right, cap, support.bit_count() == 2))
            states = advance(states, options)
            if not states:
                break
    s7 = s8 = 0
    for vertex in vertices(survivor_mask):
        degree = adj[vertex].bit_count()
        s8 += degree <= 7
        s7 += degree <= 6 and all((adj[vertex] & side).bit_count() == 1 for side in sides)
    projected = {(low, mid) for left, right, low, mid in states if left.bit_count() == right.bit_count() == 2}
    profiles = [(low, mid) for low, mid in ((6, 0), (5, 2)) if any(
        0 <= low - used_low <= s7 and 0 <= mid - used_mid
        and low - used_low + mid - used_mid <= s8 for used_low, used_mid in projected)]
    return len(profiles), s7, len(projected)


def controls(path):
    cases = 0
    for line in path.read_text().splitlines():
        adj = graph.parse_graph6(line)
        independent = independent_bound(adj)
        universe = (1 << len(adj)) - 1
        for first, second in combinations(range(len(adj)), 2):
            if adj[first] >> second & 1:
                continue
            palette = (1 << first) | (1 << second)
            common = adj[first] & adj[second]
            left, right = adj[first] ^ common, adj[second] ^ common
            for vertex in vertices(adj[first] | adj[second]):
                remaining = universe & ~(palette | left | right | common)
                support = adj[vertex] & palette
                cross = (right if left >> vertex & 1 else left if right >> vertex & 1 else 0)
                assert adj[vertex].bit_count() <= degree_ceiling(adj, independent, support, remaining, cross.bit_count())
                cases += 1
        for mask in range(1 << min(7, len(adj))):
            members = tuple(vertices(mask))
            literal = max((len(part) for size in range(len(members) + 1) for part in combinations(members, size)
                           if not any(adj[left] >> right & 1 for left, right in combinations(part, 2))), default=0)
            assert independent(mask) == literal
    assert advance({(0, 0, 0, 0)}, [(1, 0, 7, True)]) == {(1, 0, 1, 0)}
    assert not advance({(1, 0, 0, 0)}, [(1, 0, 9, True), (2, 0, 7, False)])
    print('controls', cases, 'literal ceilings, 384 exact MISs and DP tests', flush=True)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('keys', type=Path, nargs='?')
    parser.add_argument('--controls', type=Path)
    args = parser.parse_args()
    if args.controls:
        controls(args.controls)
    if args.keys:
        stats = Counter()
        for row in args.keys.read_text().splitlines():
            start = process_time()
            profiles, eligible, states = feasible(row)
            order = ord(row.split()[-1][0])-63
            stats[order, profiles] += 1
            print('_'.join(row.split()[:-1]), order, profiles, eligible, states, f'{process_time()-start:.6f}')
        print('TOTAL', dict(stats))
