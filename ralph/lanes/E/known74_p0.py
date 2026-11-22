#!/usr/bin/env python3
"""Test the all-known e74-window branch at e(W)=8 and zero deficit."""

from collections import Counter
from itertools import combinations
from math import comb
from pathlib import Path
import json
import sys

from deficit73 import by_combinations, by_cycles, mask, mask_union, wing_options
from involution_cores import bits, graph
from involution_sat import from_graph6, witnesses


def independent_groups(adj, core, width, pattern):
    if pattern is not None:
        yield from (group for _, group in wing_options(adj, core, width, {sum(pattern): pattern}))
        return
    free = ((1 << len(adj)) - 1) ^ core
    subsets = [subset for size in range(1, core.bit_count()+1) for subset in witnesses(adj, core, size)]
    yield from (group for group in witnesses(adj, free, width)
                if all(mask_union(adj, subset, group).bit_count() >= subset.bit_count() for subset in subsets))


def candidates(adj, core, width, pattern):
    full = (1 << len(adj)) - 1
    assert len(adj) == core.bit_count() + 3 * width
    choices = set(independent_groups(adj, core, width, pattern))
    for first, second in combinations(sorted(choices), 2):
        if first & second:
            continue
        last = full ^ (core | first | second)
        if last > second and last in choices:
            yield first, second, last


def direct(adj, core, width, pattern):
    free = ((1 << len(adj)) - 1) ^ core

    def valid(group):
        return (all(not (adj[vertex] & group) for vertex in bits(group)) and
                (pattern is None or sorted((adj[vertex] & group).bit_count() for vertex in bits(core)) == pattern) and
                next(witnesses(adj, core | group, width+1), None) is None)

    for selected in combinations(tuple(bits(free)), width):
        first = mask(selected)
        if not valid(first):
            continue
        for other in combinations(tuple(bits(free ^ first)), width):
            second = mask(other)
            last = free ^ (first | second)
            if first < second < last and valid(second) and valid(last):
                yield first, second, last


def cross_contacts(adj, wings):
    return all(adj[vertex] & other for wing in wings for other in wings if other != wing for vertex in bits(wing))


def controls():
    edges = [(vertex, (vertex+1) % 4) for vertex in range(4)]
    edges += [(vertex, site) for base in (4, 8, 12) for vertex in (0, 2) for site in (base, base+1)]
    edges += [(vertex, site) for base in (4, 8, 12) for vertex, site in ((1, base+2), (3, base+3))]
    reference = tuple(mask(range(base, base+4)) for base in (4, 8, 12))
    pattern = [1, 1, 2, 2]
    for removed in (False, True):
        adj = graph(16, [pair for pair in edges if not removed or pair != (0, 4)])
        expected = set(direct(adj, 15, 4, pattern))
        assert set(candidates(adj, 15, 4, pattern)) == expected
        assert (reference in expected) == (not removed)
        unrestricted = set(direct(adj, 15, 4, None))
        assert set(candidates(adj, 15, 4, None)) == unrestricted and expected <= unrestricted
    cross_edges = [(0, 2), (2, 4), (4, 1), (1, 3), (3, 5), (5, 0)]
    assert cross_contacts(graph(6, cross_edges), (3, 12, 48))
    assert not cross_contacts(graph(6, cross_edges[:-1]), (3, 12, 48))
    print('positive/minus-one decomposition matched direct toy oracle', flush=True)


def target(catalogue, output, stride, relaxed=False):
    corpus = catalogue.read_text().splitlines()
    assert len(corpus) == len(set(corpus)) == 1624
    histogram = Counter()
    stats = Counter()
    with output.open('x', encoding='ascii') as stream:
        for index, key in enumerate(corpus):
            adj = from_graph6(key)
            assert len(adj) == 26 and sum(row.bit_count() for row in adj) == 148
            forced = mask(vertex for vertex, row in enumerate(adj) if row.bit_count() == 7)
            histogram[forced.bit_count()] += 1
            if forced.bit_count() != 4:
                continue
            stats['eligible_cards'] += 1
            if (stats['eligible_cards'] - 1) % stride:
                continue
            stats['tested_cards'] += 1
            eligible = forced | mask(vertex for vertex, row in enumerate(adj) if row.bit_count() == 6)
            stats['four_subsets'] += comb(eligible.bit_count() - 4, 4)
            cores = set(by_combinations(adj, forced, eligible))
            assert cores == by_cycles(adj, forced, eligible)
            stats['qualified_cards'] += bool(cores)
            stats['cores'] += len(cores)
            for core in sorted(cores):
                pattern = None if relaxed else [1] * 4 + [2] * 4
                marks = list(candidates(adj, core, 6, pattern))
                assert set(marks) == set(direct(adj, core, 6, pattern))
                stats['wing_partitions'] += len(marks)
                for wings in marks:
                    if relaxed or cross_contacts(adj, wings):
                        count = 'relaxed_marks' if relaxed else 'contact_marks'
                        stats[count] += 1
                        print(json.dumps((index, key, core, wings)), file=stream)
    assert histogram == {0: 106, 1: 316, 2: 614, 3: 428, 4: 160}
    print('conditional known-window pattern:', dict(stats), flush=True)


if __name__ == '__main__':
    controls()
    if len(sys.argv) > 1:
        target(*map(Path, sys.argv[1:3]), stride=int(sys.argv[3]) if len(sys.argv) > 3 else 1,
               relaxed=(len(sys.argv) > 4 and sys.argv[4] == 'relaxed'))
