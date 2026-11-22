#!/usr/bin/env python3
"""Necessary boundary-neighbour domains for paired path/leaf completions."""

import argparse
from collections import Counter, deque
from itertools import combinations, product
from pathlib import Path

from audit_floor_covers import require
from audit_path_leaf import vertices
from audit_strip_extensions import mark, validate_graph
from filter_strip_supports import assignments, gap_list


def arc_consistent(domains, relations, stats):
    domains = [tuple(domain) for domain in domains]
    neighbors = [dict() for _ in domains]
    for (left, right), must_overlap in relations.items():
        neighbors[left][right] = neighbors[right][left] = must_overlap
    queue = deque((left, right) for left, peers in enumerate(neighbors) for right in peers)
    while queue:
        left, right = queue.popleft()
        wanted = neighbors[left][right]
        old = domains[left]
        if wanted:
            union = 0
            for candidate in domains[right]:
                union |= candidate
            new = tuple(candidate for candidate in old if candidate & union)
        else:
            new = tuple(candidate for candidate in old if any(not candidate & peer for peer in domains[right]))
        if len(new) != len(old):
            stats['arc_value_deletions'] += len(old) - len(new)
            if not new:
                return None
            domains[left] = new
            queue.extend((other, left) for other in neighbors[left] if other != right)
    return domains


def domain(allowed, needs, low, high):
    if high < low or allowed.bit_count() < low or any(not allowed & requirement for requirement in needs):
        return ()
    choices = tuple(1 << other for other in vertices(allowed))
    passing = []
    for size in range(low, min(high, len(choices))+1):
        for selected in combinations(choices, size):
            candidate = sum(selected)
            if all(candidate & requirement for requirement in needs):
                passing.append(candidate)
    return tuple(passing)


def controls():
    positive = 0
    for order, offsets, alpha in ((5, (1,), 2), (13, (1, 5), 4), (35, (1, 7, 11, 16), 8)):
        adj = tuple(sum(1 << ((vertex+delta) % order) for delta in (*offsets, *(-item for item in offsets)))
                    for vertex in range(order))
        from residue_bundle import triangle_free
        from audit_strip_extensions import independent
        require(triangle_free(adj) and next(independent(adj, alpha), None) is not None and
                next(independent(adj, alpha+1), None) is None, f'bad C{order} control')
        require(all((adj[left] >> right) & 1 or adj[left] & adj[right]
                    for left, right in combinations(range(order), 2)), 'control must be MTF')
        pivots = [(left, right) for left, right in combinations(range(order), 2) if not adj[left] >> right & 1]
        for first, second in pivots[::max(1, len(pivots)//20)]:
            cut = adj[first] | adj[second]
            retain = ((1 << order)-1) & ~(cut | (1 << first) | (1 << second))
            outside = tuple(vertices(retain))
            domains, actual, relations = [], [], {}
            for index, vertex in enumerate(outside):
                true_cut = adj[vertex] & cut
                known_degree = (adj[vertex] & retain).bit_count()
                domains.append(domain(cut, (adj[first], adj[second]),
                                      len(offsets)*2-known_degree, len(offsets)*2-known_degree))
                actual.append(true_cut)
                for prior, peer in enumerate(outside[:index]):
                    if adj[vertex] >> peer & 1:
                        relations[prior, index] = False
                    elif not adj[vertex] & adj[peer] & retain:
                        relations[prior, index] = True
            possible = arc_consistent(domains, relations, Counter())
            require(possible is not None and all(true_cut in got for true_cut, got in zip(actual, possible)),
                    f'C{order} genuine boundary removed')
            positive += 1
    for domains, overlap in ((((1,), (2,)), True), (((1,), (1,)), False)):
        require(arc_consistent(domains, {(0, 1): overlap}, Counter()) is None, 'bad infeasible pair retained')
    bound = (1, 2, 3)
    cases = 0
    for raw in product(range(1, 8), repeat=3):
        domains = [tuple(candidate for index, candidate in enumerate(bound) if mask >> index & 1) for mask in raw]
        pairs = tuple(combinations(range(3), 2))
        for choices in product((None, False, True), repeat=3):
            relations = {pair: state for pair, state in zip(pairs, choices) if state is not None}
            possible = arc_consistent(domains, relations, Counter())
            for candidate in product(*domains):
                if all(bool(candidate[left] & candidate[right]) == wanted for (left, right), wanted in relations.items()):
                    require(possible is not None and all(value in values for value, values in zip(candidate, possible)),
                            'arc filtering lost an exact solution')
            cases += 1
    print(f'controls: {positive} C5/C13/C35 projections, 2 negative mutations, {cases} exact three-domain cases')


def inspect(adj, first, second, stats):
    sides, stars, _ = mark(adj, first, second)
    sides = tuple((star, *(node for node in side if node != star)) for side, star in zip(sides, stars, strict=True))
    outside = tuple(vertices(((1 << len(adj))-1) ^ first ^ second))
    shared = len(adj)-24
    retained_count = len(outside)
    anchors = sides[0] + sides[1]
    shape = tuple(tuple(sum(1 << index for index, anchor in enumerate(side) if adj[vertex] >> anchor & 1)
                        for side in sides) for vertex in outside)
    gaps = tuple(gap_list(4, 4, (support[index] for support in shape)) for index in range(2))
    peer_checks = {}
    for left, right in combinations(range(retained_count), 2):
        x, y = outside[left], outside[right]
        if adj[x] >> y & 1:
            peer_checks[left, right] = False
        elif not adj[x] & adj[y]:
            peer_checks[left, right] = True
    anchor_needs = [tuple(bit for bit, anchor in enumerate(anchors)
                          if not (adj[vertex] >> anchor & 1 or adj[vertex] & adj[anchor])) for vertex in outside]
    baseline = False
    for left_leaf, right_leaf in product(range(1, 4), repeat=2):
        union_gaps = tuple(sum(1 << bit for bit in range(4) if any(value >> bit & 1 for value in gap))
                           for gap in gaps)
        if not (union_gaps[0] >> left_leaf & 1 and union_gaps[1] >> right_leaf & 1):
            continue
        centering = tuple((16,)*4 + tuple(16 | (1 << index) for index in range(1, 4) if index != leaf)
                          for leaf in (left_leaf, right_leaf))
        for exclusive_a, exclusive_b, common in assignments(shape, gaps, centering, shared, 5):
            stats['cross_roles'] += 1
            removed = tuple(left | (right << 5) for left, right in (*exclusive_a, *exclusive_b, *common))
            supports = tuple(left | (right << 5) for left, right in shape)
            columns = tuple(sum(1 << index for index, support in enumerate(removed) if support >> bit & 1)
                            for bit in (0, 1, 2, 3, 5, 6, 7, 8, 4, 9))
            possible = tuple(sum(1 << index for index, cut in enumerate(removed) if not support & cut)
                             for support in supports)
            centre_need = columns[8:]
            center_candidate = all(all(pool & need for need in centre_need) for pool in possible)
            if not center_candidate:
                continue
            baseline = True
            stats['centre_roles'] += 1
            domains = []
            for index, (pool, vertex) in enumerate(zip(possible, outside, strict=True)):
                needs = (*centre_need, *(columns[bit] for bit in anchor_needs[index]))
                degree = adj[vertex].bit_count()
                low = 7 + (supports[index].bit_count() > 2) - degree
                domains.append(domain(pool, needs, max(0, low), 9-degree))
                if not domains[-1]:
                    break
            if len(domains) != len(outside) or not domains[-1]:
                continue
            stats['unary_roles'] += 1
            if arc_consistent(domains, peer_checks, stats) is not None:
                stats['arc_roles'] += 1
                return 'ARC_PASS'
    return 'CUT_REJECT' if baseline else 'CENTRE_REJECT'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('keys', type=Path, nargs='?')
    parser.add_argument('--sample', type=int, default=0)
    args = parser.parse_args()
    controls()
    if args.keys:
        rows = args.keys.read_text().splitlines()
        if args.sample:
            rows = [rows[index*len(rows)//args.sample] for index in range(args.sample)]
        stats, outcomes = Counter(), Counter()
        for line in rows:
            row, first, second, encoded = line.split()
            result = inspect(validate_graph(encoded), int(first), int(second), stats)
            outcomes[result] += 1
            print(row, first, second, result, flush=True)
        print('outcomes', dict(outcomes), 'role stats', dict(stats), flush=True)


if __name__ == '__main__':
    main()
