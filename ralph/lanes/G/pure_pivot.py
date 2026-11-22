#!/usr/bin/env python3
"""Order-27 covers at a path centre and the opposite leaf or full anchor."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations, islice, product
from pathlib import Path

from canon_strip import validate
from check_root_cover import graph, vertices
from root_glue import independent
from strip_completion import Completion


def roles(marks, star, occupied):
    for centre in marks:
        if centre == star or tuple(sorted((centre, star))) in occupied:
            continue
        yield 'leaf', centre, centre
        for other_leaf in marks:
            if other_leaf in (centre, star) or tuple(sorted((centre, other_leaf))) in occupied:
                continue
            yield 'full', centre, other_leaf


def local_control():
    marks = (0, 1, 2, 3)
    pivot = 4
    candidates = tuple(combinations(marks, 2))
    for star, present in product(marks, range(1 << len(candidates))):
        occupied = {pair for bit, pair in enumerate(candidates) if present >> bit & 1}
        expected = set()
        for centre, leaf in product(marks, (*marks, pivot)):
            if len({star, centre, leaf}) != 3:
                continue
            holes = {tuple(sorted((centre, star))), tuple(sorted((centre, leaf)))}
            if holes & occupied:
                continue
            expected.add(('leaf', centre, centre) if leaf == pivot else ('full', centre, leaf))
        assert set(roles(marks, star, occupied)) == expected
    print('256 role snapshots match independent missing-double oracle')


def instance(encoded, first, second, role, centre, peer, eager):
    adj = graph.parse_graph6(encoded)
    assert len(adj) == 27
    retained = validate(adj, min(first, second), max(first, second))
    active = tuple(tuple(vertices(mask)) for mask in (first, second))
    stars, = ((left, right) for left, right in product(*active) if adj[left] >> right & 1)
    roots, pivots = (27, 28), (29, 30)
    sides = tuple((*marks, pivot) for marks, pivot in zip(active, pivots, strict=True))
    occupied = {tuple(vertices(adj[vertex] & second)) for vertex in retained if (adj[vertex] & second).bit_count() == 2}
    assert (role, centre, peer) in set(roles(active[1], stars[1], occupied))
    holes = {tuple(sorted((centre, stars[1]))), tuple(sorted((centre, pivots[1] if role == 'leaf' else peer)))}
    after = 35 if role == 'leaf' else 36
    common = tuple(range(31, after))
    exclusive = (tuple(range(after, 37)), (37, 38, 39))
    deleted = (*common, *exclusive[0], *exclusive[1])
    exterior = (*retained, *deleted)
    fixed = {(left, right): bool(adj[left] >> right & 1) for left, right in combinations(range(27), 2)}
    for index, (root, pivot, side) in enumerate(zip(roots, pivots, sides, strict=True)):
        for other in range(40):
            if other != root:
                fixed[tuple(sorted((root, other)))] = other in roots or other in side
            if other != pivot and other not in roots:
                fixed[tuple(sorted((pivot, other)))] = other in common or other in exclusive[index]
        expected = Counter({(anchor,): 4 for anchor in active[index]})
        expected.update(pair for pair in combinations(active[index], 2) if not index or pair not in holes)
        seen = Counter(tuple(vertices(adj[vertex] & (first if not index else second))) for vertex in retained)
        assert seen <= expected
        for vertex, signature in zip(exclusive[1-index], sorted((expected - seen).elements()), strict=True):
            for anchor in active[index]:
                fixed[anchor, vertex] = anchor in signature
    for left, right in combinations(deleted, 2):
        if left not in exclusive[0] or right not in exclusive[1]:
            fixed[left, right] = False
    present = [0] * 40
    for (left, right), value in fixed.items():
        if value:
            present[left] |= 1 << right
            present[right] |= 1 << left
    for left, right in combinations(range(40), 2):
        if present[left] & present[right] and (left, right) not in fixed:
            fixed[left, right] = False
    problem = Completion(40, fixed)
    problem.triangles()
    problem.maximal()
    double_supports = {vertex: [] for vertex in exterior}
    for index, side in enumerate(sides):
        supports = {vertex: {anchor: problem.edgeof(vertex, anchor) for anchor in side} for vertex in exterior}
        for incident in supports.values():
            problem.bound(incident.values(), 1, 2)
        for anchor in side:
            singles = [problem.and_all(lit if other == anchor else -lit for other, lit in incident.items())
                       for incident in supports.values()]
            problem.bound(singles, 4, 4)
        optional = []
        for left, right in combinations(side, 2):
            double = [problem.and2(incident[left], incident[right]) for incident in supports.values()]
            for vertex, literal in zip(exterior, double, strict=True):
                double_supports[vertex].append(literal)
            if index:
                count = int((left, right) not in holes)
                problem.bound(double, count, count)
            elif right != pivots[0] or left == stars[0]:
                count = int(right != pivots[0])
                problem.bound(double, count, count)
            else:
                problem.bound(double, 0, 1)
                optional.extend(double)
        if not index:
            problem.bound(optional, 2, 2)
    degree7, degree8 = [], []
    for vertex in exterior:
        selectors = problem.exact_degree(vertex, (7, 8, 9))
        for double in double_supports[vertex]:
            problem.add((-selectors[7], -double))
        degree7.append(selectors[7])
        degree8.append(selectors[8])
    profile = problem.formula.new()
    for choice, low, middle in ((profile, 6, 0), (-profile, 5, 2)):
        start = len(problem.formula.clauses)
        problem.bound(degree7, low, low)
        problem.bound(degree8, middle, middle)
        for index in range(start, len(problem.formula.clauses)):
            problem.formula.clauses[index] += (-choice,)
    if eager:
        for count in (7, 6):
            for chosen in islice(independent(adj, (1 << 27) - 1, count, count), eager):
                for index, domain in enumerate(exclusive):
                    for extra in combinations(domain, 9-count):
                        problem.add(problem.independent_clause((*chosen, *extra, pivots[1-index])))
    return problem


def extract(keys, output):
    counts = Counter()
    with output.open('w') as stream:
        for row in keys.read_text().splitlines():
            row_id, first, second, encoded = row.split()
            first, second = int(first), int(second)
            adj = graph.parse_graph6(encoded)
            retained = validate(adj, first, second)
            for near, far in ((first, second), (second, first)):
                active = tuple(vertices(far))
                star, = (vertex for vertex in active if adj[vertex] & near)
                occupied = {tuple(vertices(adj[vertex] & far)) for vertex in retained if (adj[vertex] & far).bit_count() == 2}
                for role, centre, peer in roles(active, star, occupied):
                    counts[role] += 1
                    print(row_id, near, far, role, centre, peer, peer, encoded, file=stream)
    print(dict(counts))


if __name__ == '__main__':
    CLI = ArgumentParser(description=__doc__)
    CLI.add_argument('keys', type=Path)
    CLI.add_argument('output', type=Path)
    ARGS = CLI.parse_args()
    local_control()
    extract(ARGS.keys, ARGS.output)
