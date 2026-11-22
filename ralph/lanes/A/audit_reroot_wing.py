#!/usr/bin/env python3
"""Necessary Ramsey screen on the newly retained neighbours of A's centre."""

from argparse import ArgumentParser
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
from pathlib import Path
from random import Random

from audit_a_side_reroot import (alpha, capacity, cases, cross_edge, mask, oracle_roles,
                                 parse_graph6, remnant, take, vertices)


def neighbours(adj, support):
    hitting = 0
    for vertex in vertices(support):
        hitting |= adj[vertex]
    return hitting


def optimistic(adj, anchors, support):
    exterior = ((1 << len(adj)) - 1) ^ anchors
    if any(adj[vertex] & support for vertex in vertices(support)):
        return None
    return support | (exterior & ~neighbours(adj, support))


def independent_oracle(adj):
    @lru_cache(maxsize=50000)
    def has(available, size):
        if size <= 0:
            return True
        while available.bit_count() >= size:
            bit = available & -available
            vertex = bit.bit_length() - 1
            available ^= bit
            if has(available & ~adj[vertex], size - 1):
                return True
        return False
    return has


def possible_wing(has, allowable, universe, max_alpha, degrees=None):
    degrees = dict(degrees or ())
    for index, seen in enumerate(allowable):
        if not has(seen, degrees.get(index, 0)):
            return False
    for count in range(len(allowable), 1, -1):
        for subset in combinations(allowable, count):
            missed = universe
            for additions in subset:
                missed &= ~additions
            if has(missed, max_alpha + 1 - count):
                return False
    return True


def multisets(pool, count):
    return sorted(set(combinations(sorted(pool), count)))


class Core:
    def __init__(self, adj, arm_a, arm_b):
        self.adj = adj
        self.arms = arm_a, arm_b
        self.cross_a, _ = cross_edge(adj, arm_a, arm_b)
        self.universe = (1 << len(adj)) - 1
        self.exterior = tuple(vertices(self.universe ^ arm_a ^ arm_b))
        self.has = independent_oracle(adj)
        self.allowed = lru_cache(maxsize=None)(lambda support: optimistic(adj, arm_a | arm_b, support))

    def screen(self, degree, holes_b, tag, triple, new_order, min_degree):
        arm_a, arm_b = self.arms
        pivot_s, pivot_a, pivot_b = (1 << 21, 1 << 26, 1 << 27)
        new_count = new_order - 22
        remainder_b = remnant(capacity(arm_b | pivot_b, holes_b), take(self.adj, self.exterior, arm_b))
        assert remainder_b is not None
        b_pool = [slot for slot in remainder_b.elements() if not slot & pivot_b]
        assert len(b_pool) == 15 - degree
        b_choices = multisets(b_pool, new_count)
        other_leaves = (pivot_s,) if tag == 'leaf' else tuple(1 << leaf for leaf in vertices(arm_a ^ (1 << self.cross_a)))
        for leaf in other_leaves:
            holes_a = (pivot_a | leaf, pivot_a | (1 << self.cross_a))
            remainder_a = remnant(capacity(arm_a | pivot_a | pivot_s, holes_a),
                                 take(self.adj, self.exterior, arm_a))
            assert remainder_a is not None
            a_pool = [slot & ~pivot_a for slot in remainder_a.elements() if slot & pivot_a and not slot & pivot_s]
            assert len(a_pool) - new_count == degree - 7 - triple
            for a_choices in multisets(a_pool, new_count):
                for b_tuple in b_choices:
                    for b_order in set(permutations(b_tuple)):
                        rows = tuple(self.allowed(a | b) for a, b in zip(a_choices, b_order, strict=True))
                        if None in rows:
                            continue
                        if min_degree:
                            too_low = (vertex for vertex, adjacent in enumerate(self.adj)
                                       if adjacent.bit_count() < min_degree)
                            if any(self.adj[vertex].bit_count() + sum((row >> vertex) & 1 for row in rows) < min_degree
                                   for vertex in too_low):
                                continue
                        if possible_wing(self.has, rows, self.universe, 7,
                                         ((index, min_degree - 1) for index in range(new_count))):
                            return True
        return False


def controls():
    cycle = tuple(mask(((vertex + 1) % 13, (vertex - 1) % 13)) for vertex in range(13))
    assert alpha(cycle) == 6
    positive = 0
    for wing in combinations(range(13), 3):
        if any(cycle[vertex] & mask(wing) for vertex in wing):
            continue
        order = [vertex for vertex in range(13) if vertex not in wing]
        adj = tuple(mask(index for index, vertex in enumerate(order) if cycle[old] >> vertex & 1)
                    for old in order)
        anchors = mask(range(0, len(order), 2))
        allowed, actual = [], []
        for vertex in wing:
            seen = mask(index for index, old in enumerate(order) if cycle[vertex] >> old & 1)
            projection = optimistic(adj, anchors, seen & anchors)
            assert projection is not None and projection & seen == seen
            allowed.append(projection)
            actual.append(seen)
        oracle = independent_oracle(adj)
        assert possible_wing(oracle, actual, (1 << len(adj)) - 1, 6)
        assert possible_wing(oracle, allowed, (1 << len(adj)) - 1, 6)
        positive += 1
    assert not possible_wing(independent_oracle((0,) * 4), (0,) * 4, 15, 7)
    assert possible_wing(independent_oracle((1 << 1, 1, 0, 0)), (0,) * 4, 15, 7)
    print('C13 independent triple positives', positive, 'I8 negative and one-edge escape PASS', flush=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('old', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--sample', type=int, default=192)
    args = parser.parse_args()
    controls()
    rng = Random(31412)
    by_degree = {8: [], 9: []}
    for line in args.old.read_text().splitlines():
        old, small_text, large_text, encoded = line.split()
        adj = tuple(parse_graph6(encoded))
        small, large = int(small_text), int(large_text)
        for degree in by_degree:
            for orientation, _, _, _, _, shape, hole, peer in oracle_roles(adj, small, large, degree):
                if orientation == 0:
                    identifier = '_'.join(map(str, (old, small, large, degree, orientation, shape, *hole, *peer)))
                    by_degree[degree].append((identifier, adj, small, large, tuple(map(mask, (hole, peer)))))
    outcomes = Counter()
    with args.output.open('w') as output:
        for degree, rows in by_degree.items():
            for identifier, adj, small, large, holes in rng.sample(rows, min(args.sample, len(rows))):
                core = Core(adj, small, large)
                for tag, triple, codegree, order in cases(degree):
                    if order == 27:
                        continue
                    minimum = order - 22
                    passes = core.screen(degree, holes, tag, triple, order, minimum)
                    outcomes[(degree, tag, triple, order, passes)] += 1
                    print(identifier, tag, triple, codegree, order, int(passes), file=output, sep='\t')
    for chain, count in sorted(outcomes.items()):
        print(*chain, count, flush=True)


if __name__ == '__main__':
    main()
