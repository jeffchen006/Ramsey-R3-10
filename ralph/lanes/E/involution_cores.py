#!/usr/bin/env python3
"""Exact moving-set/attachment profiles for the two large-fixed involution strata."""

import argparse
from collections import Counter
from itertools import combinations, permutations, product
import json


RAMSEY = (0, 1, 3, 6, 9, 14, 18, 23, 28, 36, 41)


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def graph(order, edges):
    adj = [0] * order
    for left, right in edges:
        adj[left] |= 1 << right
        adj[right] |= 1 << left
    return tuple(adj)


def independent_extensions(adj):
    """(S, M minus N[S]) including the empty independent set."""
    def walk(pending, picked, anti):
        yield picked, anti
        for vertex in bits(pending):
            bit = 1 << vertex
            pending ^= bit
            yield from walk(pending & ~adj[vertex], picked | bit, anti & ~(adj[vertex] | bit))

    return walk((1 << len(adj)) - 1, 0, (1 << len(adj)) - 1)


def requirements(adj, groups, bound):
    """Report the residue for every independent moved subset."""
    for picked, anti in independent_extensions(adj):
        limit = bound - picked.bit_count()
        hit = sum(1 << orbit for orbit in {vertex // 2 for vertex in bits(picked)})
        retained = sum(1 << index for index, membership in enumerate(groups) if not membership & hit)
        yield retained, limit, anti.bit_count()


def acceptable(adj, groups, counts, bound):
    # The whole residue includes moved as well as fixed vertices.
    cache = {}
    for retained, alpha, moved in requirements(adj, groups, bound):
        if alpha < 0:
            return False
        if retained not in cache:
            cache[retained] = sum(counts[index] for index in bits(retained))
        if cache[retained] + moved >= RAMSEY[alpha + 1]:
            return False
    return True


def relabel_edges(edges, perm):
    return tuple(sorted(tuple(sorted((perm[left], perm[right]))) for left, right in edges))


def defects(order):
    edges = list(combinations(range(order), 2))
    perms = tuple(permutations(range(order)))
    seen = set()
    for size in range(order + 1):
        for row in combinations(edges, size):
            if row in seen:
                continue
            degrees = Counter(vertex for edge in row for vertex in edge)
            if max(degrees.values(), default=0) > 2:
                continue
            adj = graph(order, row)
            if any(adj[left] & adj[right] for left, right in row):
                continue
            automorphisms = []
            for perm in perms:
                image = relabel_edges(row, perm)
                seen.add(image)
                if row == image:
                    automorphisms.append(perm)
            yield row, tuple(degrees[index] for index in range(order)), automorphisms


def normalized_phases(order, joins):
    phases = [None] * order
    phases[0] = 0
    for _ in range(order):
        for left, right, phase in joins:
            if phases[left] is not None and phases[right] is None:
                phases[right] = phases[left] ^ phase ^ 1
            elif phases[right] is not None and phases[left] is None:
                phases[left] = phases[right] ^ phase ^ 1
    assert all(phase is not None for phase in phases)
    return tuple(phase ^ phases[left] ^ phases[right] for left, right, phase in joins)


def phases_on(order, joins):
    triples = []
    positions = {edge: pos for pos, edge in enumerate(joins)}
    for left, mid, right in combinations(range(order), 3):
        triple = ((left, mid), (left, right), (mid, right))
        if all(edge in positions for edge in triple):
            triples.append(tuple(positions[edge] for edge in triple))
    seen = set()
    for phases in product(range(2), repeat=len(joins)):
        if not all(phases[first] ^ phases[second] ^ phases[third] for first, second, third in triples):
            continue
        switch = normalized_phases(order, tuple((*edge, phase) for edge, phase in zip(joins, phases)))
        if switch not in seen:
            seen.add(switch)
            yield switch


def lift(sizes, joins, phases):
    edges = [(2 * orbit, 2 * orbit + 1) for orbit, size in enumerate(sizes) if not size]
    edges.extend((2 * left + bit, 2 * right + (phase ^ bit))
                 for (left, right), phase in zip(joins, phases) for bit in range(2))
    return graph(2 * len(sizes), edges)


def involution28():
    all_edges = set(combinations(range(6), 2))
    stats = Counter()
    seen = set()
    for defect, degrees, auts in defects(6):
        joins = tuple(sorted(all_edges.difference(defect)))
        phases_list = tuple(phases_on(6, joins))
        stats['defect_classes'] += 1
        choices = [(0, 1, 2, 3, 4) if degree == 0 else (5,) if degree == 1 else (5, 6)
                   for degree in degrees]
        for sizes in product(*choices):
            if max(sizes) != 6 or any(sizes[left] + sizes[right] < 11 for left, right in defect):
                continue
            eligible = tuple((left, right) for left, right in defect if sizes[left] == sizes[right] == 6)
            for indicators in product(range(2), repeat=len(eligible)):
                overlap = tuple(edge for edge, use in zip(eligible, indicators) if use)
                unique = list(sizes)
                for left, right in overlap:
                    unique[left] -= 1
                    unique[right] -= 1
                free = 28 - sum(unique) - len(overlap)
                if free < 0:
                    continue
                groups = (0,) + tuple(1 << index for index in range(6)) + tuple(
                    (1 << left) | (1 << right) for left, right in overlap)
                counts = (free, *unique, *(1 for _ in overlap))
                for phase in phases_list:
                    adj = lift(sizes, joins, phase)
                    stats['before_ramsey'] += 1
                    if not acceptable(adj, groups, counts, 9):
                        continue
                    stats['labelled_after_ramsey'] += 1
                    variants = []
                    for perm in auts:
                        perm_sizes = [0] * 6
                        for index, size in enumerate(sizes):
                            perm_sizes[perm[index]] = size
                        perm_joins = sorted((*sorted((perm[left], perm[right])), value)
                                            for (left, right), value in zip(joins, phase))
                        variants.append((tuple(perm_sizes), relabel_edges(overlap, perm),
                                         normalized_phases(6, perm_joins)))
                    key = (defect, min(variants))
                    if key in seen:
                        continue
                    seen.add(key)
                    yield {'defect': defect, 'sizes': sizes, 'overlap': overlap,
                           'phase': phase, 'adj': adj, 'groups': groups, 'counts': counts}
    print(json.dumps(dict(stats), sort_keys=True), flush=True)


def involution32():
    for count in (2, 3, 4):
        sizes = (5,) * (4 - count) + (6,) * count
        joins = tuple(combinations(range(4), 2))
        adj = lift(sizes, joins, (1,) * len(joins))
        groups = (0, 1, 2, 4, 8)
        counts = (32 - sum(sizes), *sizes)
        assert acceptable(adj, groups, counts, 9)
        yield {'sizes': sizes, 'adj': adj, 'groups': groups, 'counts': counts}


def calibrate():
    vertices = tuple(combinations(range(5), 2))
    sigma = tuple(vertices.index(tuple(sorted(1 - index if index < 2 else index for index in row)))
                  for row in vertices)
    fixed = [index for index, other in enumerate(sigma) if index == other]
    moved = [vertex for index, other in enumerate(sigma) if index < other for vertex in (index, other)]
    adj = graph(len(vertices), ((left, right) for left, right in combinations(range(len(vertices)), 2)
                               if not set(vertices[left]) & set(vertices[right])))
    moving = graph(len(moved), ((left, right) for left, right in combinations(range(len(moved)), 2)
                               if adj[moved[left]] & (1 << moved[right])))
    groups = tuple(sum(1 << (index // 2) for index in range(0, len(moved), 2)
                       if adj[vertex] & (1 << moved[index])) for vertex in fixed)
    assert acceptable(moving, groups, (1,) * len(groups), 4)
    assert not acceptable(moving, groups, (1,) * len(groups), 3)
    for order in range(1, 6):
        edges = tuple(combinations(range(order), 2))
        for word in range(1 << len(edges)):
            test = graph(order, (edge for index, edge in enumerate(edges) if word & (1 << index)))
            actual = dict(independent_extensions(test))
            expected = {}
            for picked in range(1 << order):
                if not any(test[vertex] & picked for vertex in bits(picked)):
                    expected[picked] = sum(1 << vertex for vertex in range(order)
                                           if not picked & ((1 << vertex) | test[vertex]))
            assert actual == expected
    print('Petersen (3,5;10) survives, (3,4;10) rejected; exact independent subsets and residues on 1099 graphs')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('calibrate', '28', '32'))
    parser.add_argument('--output')
    args = parser.parse_args()
    if args.mode == 'calibrate':
        calibrate()
        return
    rows = list(involution28() if args.mode == '28' else involution32())
    print(f'profiles={len(rows)} free={sorted(Counter(row["counts"][0] for row in rows).items())}')
    if args.mode == '28':
        print(f'sizes={sorted(Counter(tuple(sorted(row["sizes"])) for row in rows).items())}')
    if args.output:
        with open(args.output, 'w', encoding='ascii') as output:
            for row in rows:
                output.write(json.dumps(row, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
