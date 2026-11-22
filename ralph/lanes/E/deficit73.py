#!/usr/bin/env python3
"""Exact 73-edge mark census for the deficient e(W)=8 crown."""

from collections import Counter
from itertools import combinations, product
import json
from math import comb
from pathlib import Path
import sys

from involution_cores import bits, graph
from involution_sat import from_graph6, witnesses
from window73 import read_census


def mask(vertices):
    return sum(1 << vertex for vertex in vertices)


def by_combinations(adj, forced, eligible):
    for extra in combinations(tuple(bits(eligible & ~forced)), 8 - forced.bit_count()):
        chosen = forced | mask(extra)
        if all((adj[vertex] & chosen).bit_count() == 2 for vertex in bits(chosen)):
            yield chosen


def cycles(adj, eligible, length):
    def walk(path, occupied):
        root, end = path[0], path[-1]
        if len(path) == length:
            if path[1] < end and adj[end] >> root & 1:
                yield occupied
            return
        for vertex in bits(adj[end] & eligible & ~occupied & ~((2 << root) - 1)):
            forbidden = occupied ^ (1 << end)
            if len(path) + 1 == length:
                forbidden ^= 1 << root
            if not adj[vertex] & forbidden:
                yield from walk((*path, vertex), occupied | (1 << vertex))

    return {chosen for root in bits(eligible) for chosen in walk((root,), 1 << root)}


def by_cycles(adj, forced, eligible):
    found = {cycle for cycle in cycles(adj, eligible, 8) if cycle & forced == forced}
    for left, right in combinations(sorted(cycles(adj, eligible, 4)), 2):
        if left & right or (left | right) & forced != forced:
            continue
        if not any(adj[vertex] & right for vertex in bits(left)):
            found.add(left | right)
    return found


def wing_options(adj, core, width, required):
    free = ((1 << len(adj)) - 1) ^ core
    independent = [subset for size in range(1, core.bit_count()+1) for subset in witnesses(adj, core, size)]
    for group in witnesses(adj, free, width):
        row = [(adj[vertex] & group).bit_count() for vertex in bits(core)]
        total = sum(row)
        if total not in required or min(row) == 0 or max(row) > max(required[total]):
            continue
        if sorted(row) != required[total]:
            continue
        if any(mask_union(adj, subset, group).bit_count() < subset.bit_count() for subset in independent):
            continue
        yield total, group


def mask_union(adj, subset, allowed):
    union = 0
    for vertex in bits(subset):
        union |= adj[vertex] & allowed
    return union


def wing_partitions(adj, core, width, required):
    groups = {total: set() for total in required}
    for total, group in wing_options(adj, core, width, required):
        groups[total].add(group)
    small, large = sorted(required)
    outside = ((1 << len(adj)) - 1) ^ core
    for last, first in product(sorted(groups[large]), sorted(groups[small])):
        if last & first:
            continue
        second = outside ^ (last | first)
        if second > first and second in groups[small]:
            yield first, second, last


def direct_partitions(adj, core, width, required):
    outside = ((1 << len(adj)) - 1) ^ core
    small, large = sorted(required)

    def valid(group, total):
        assert group.bit_count() == width
        if any(group & adj[vertex] for vertex in bits(group)):
            return False
        if sorted((adj[vertex] & group).bit_count() for vertex in bits(core)) != required[total]:
            return False
        return next(witnesses(adj, core | group, width+1), None) is None

    for block in combinations(tuple(bits(outside)), width):
        large_group = mask(block)
        if not valid(large_group, large):
            continue
        others = outside ^ large_group
        for portion in combinations(tuple(bits(others)), width):
            first = mask(portion)
            other = others ^ first
            if first < other and valid(first, small) and valid(other, small):
                yield first, other, large_group


def control():
    for adj in (graph(9, [(vertex, (vertex+1) % 8) for vertex in range(8)]),
                graph(9, [(base+offset, base+(offset+1) % 4) for base in (0, 4) for offset in range(4)])):
        assert set(by_combinations(adj, 3, 511)) == by_cycles(adj, 3, 511) == {255}
        assert not set(by_combinations(adj, 257, 511)) and not by_cycles(adj, 257, 511)
    core = 15
    edges = [(vertex, (vertex+1) % 4) for vertex in range(4)]
    edges += [(vertex, base+vertex) for vertex in range(4) for base in (4, 8)]
    edges += [(vertex, site) for vertex in (0, 2) for site in (12, 13)] + [(1, 14), (3, 15)]
    required = {4: [1, 1, 1, 1], 6: [1, 1, 2, 2]}
    planted = tuple(mask(range(base, base+4)) for base in (4, 8, 12))
    for toggled in (edges, [pair for pair in edges if pair != (0, 12)]):
        adj = graph(16, toggled)
        expected = set(direct_partitions(adj, core, 4, required))
        assert set(wing_partitions(adj, core, 4, required)) == expected
        assert (planted in expected) == (toggled == edges)
    print('cycle controls C8, 2C4 and forced isolate; full toy partition oracle with plant and deletion')


def target(catalogue, output, stride=1):
    histogram = read_census(catalogue, 26, 73, 62)
    assert histogram == {0: 15, 1: 16, 2: 31}
    count = Counter()
    with output.open('x', encoding='ascii') as stream:
        for index, key in enumerate(catalogue.read_text().splitlines()):
            adj = from_graph6(key)
            forced = mask(vertex for vertex, row in enumerate(adj) if row.bit_count() == 7)
            if forced.bit_count() != 2:
                continue
            count['eligible_cards'] += 1
            if (count['eligible_cards'] - 1) % stride:
                continue
            count['tested_cards'] += 1
            eligible = forced | mask(vertex for vertex, row in enumerate(adj) if row.bit_count() == 6)
            count['six_subsets'] += comb(eligible.bit_count() - 2, 6)
            candidates = sorted(by_combinations(adj, forced, eligible))
            assert set(candidates) == by_cycles(adj, forced, eligible)
            count['qualified_cards'] += bool(candidates)
            for core in candidates:
                required = {10: [1]*6 + [2]*2, 14: [1]*2 + [2]*6}
                count['core_masks'] += 1
                marks = list(wing_partitions(adj, core, 6, required))
                assert set(marks) == set(direct_partitions(adj, core, 6, required))
                for first, second, large in marks:
                    count['marks'] += 1
                    hits = [sum(not (adj[vertex] & large) for vertex in bits(group)) for group in (first, second)]
                    if max(hits) <= 1:
                        count['marks_after_large_contact'] += 1
                        print(json.dumps((index, key, core, first, second, large, hits)), file=stream)
    print('exact filtered marked 73-edge windows:', dict(count), flush=True)


if __name__ == '__main__':
    control()
    if len(sys.argv) > 1:
        target(*map(Path, sys.argv[1:3]), stride=int(sys.argv[3]) if len(sys.argv) == 4 else 1)
