#!/usr/bin/env python3
"""Shared-support projection for all uncrossed mixed-strip pivots."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations, product
from pathlib import Path
from time import process_time

from pysat.solvers import Cadical195

from mixed_strip_completion import instance


def atleast(problem, literals, count):
    return -problem.and_all(-problem.and_all(group) for group in combinations(literals, count))


def lower_if(problem, guard, choices, bound):
    if guard != -1:
        start = len(problem.formula.clauses)
        problem.bound(choices, bound, len(choices))
        if guard != 1:
            for idx in range(start, len(problem.formula.clauses)):
                problem.formula.clauses[idx] += (-guard,)


def budget(problem, adj, deleted, exclusive, low_degrees, shared, degree):
    terms = [problem.edgeof(left, right) for left, right in product(*exclusive)]
    for vertex in deleted:
        low = low_degrees[vertex]
        alias = problem.formula.new()
        problem.add((-low, alias))
        problem.add((low, -alias))
        terms.extend((low, alias))
    edge_count = sum(neighbors.bit_count() for neighbors in adj) // 2
    target = edge_count - (112 - 9 * degree + 9 * shared)
    problem.bound(terms, target, target)


def constraints(problem, sides, stars, pivots, exterior, cut_a, holes, *, both):
    edge = problem.edgeof
    cross_a, cross_b = stars
    pivot_a, pivot_b = pivots
    for anchor_a, anchor_b in product(*sides):
        witnesses = tuple(problem.and2(edge(anchor_a, vertex), edge(anchor_b, vertex))
                          for vertex in exterior)
        if (anchor_a, anchor_b) == stars:
            for lit in witnesses:
                problem.add((-lit,))
        elif both or anchor_a == pivot_a or anchor_b == pivot_b:
            problem.add(witnesses)
    if not both:
        return
    hole_count = Counter(anchor for pair in holes for anchor in pair)
    cut_a = frozenset(cut_a)
    for pivot in sides[1]:
        if pivot == cross_b:
            continue
        degree = 9 - hole_count[pivot]
        assert degree in (8, 9)
        # Previously certified maxima: d8 j4 and d9 j5 do not occur.
        cap = degree - 5
        codegree = tuple(edge(pivot, vertex) for vertex in sorted(cut_a))
        problem.bound(codegree, 1, cap)
        guards = [(atleast(problem, codegree, threshold), 4 if degree == 8 and threshold == 3
                   else threshold + 8 - degree) for threshold in range(1, cap + 1)]
        for anchor in (*sides[0], *sides[1]):
            if anchor in (pivot_a, pivot):
                continue
            contacts = tuple(problem.and2(edge(anchor, vertex), -edge(pivot, vertex))
                             for vertex in exterior if vertex not in cut_a)
            cross = int(anchor in stars)
            problem.bound(contacts, 0, 7 - cross)
            for guard, minimum in guards:
                lower_if(problem, guard, contacts, max(0, minimum - cross))


def parse(row):
    rowid, first, second, case, hole_left, hole_right, hole_peer, *tail = row.split()
    return '_'.join(row.split()[:-1]), (tail[-1], int(first), int(second), case, int(hole_left),
                                        int(hole_right), int(hole_peer), 0, *map(int, tail[:-1]))


def support_model(problem, metadata, model, *, both):
    sides, stars, pivots, exterior, cut_a, holes = metadata
    truth = set(model)
    masks = {vertex: tuple(frozenset(anchor for anchor in side if problem.edgeof(anchor, vertex) in truth)
                          for side in sides) for vertex in exterior}
    for index, side in enumerate(sides):
        counts = Counter(support[index] for support in masks.values())
        found_holes = {frozenset(pair) for pair in combinations(side, 2) if counts[frozenset(pair)] == 0}
        assert counts and all(len(support) in (1, 2) and count == (4 if len(support) == 1 else 1)
                              for support, count in counts.items())
        assert all(counts[frozenset((anchor,))] == 4 for anchor in side)
        assert len(found_holes) == 2
        if index:
            assert found_holes == {frozenset(pair) for pair in holes}
        else:
            assert all(pivots[0] in pair for pair in found_holes)
            assert frozenset((stars[0], pivots[0])) in found_holes
    codes = {}
    assert {vertex for vertex, support in masks.items() if pivots[0] in support[0]} == set(cut_a)
    for left, right in product(*sides):
        common = sum(left in support[0] and right in support[1] for support in masks.values())
        if (left, right) == stars:
            assert common == 0
        elif both or left == pivots[0] or right == pivots[1]:
            assert common >= 1
    for pivot in sides[1]:
        if pivot == stars[1]:
            continue
        cut_b = {vertex for vertex, support in masks.items() if pivot in support[1]}
        degree = len(cut_b) + 1
        codegree = len(set(cut_a) & cut_b)
        remaining = set(exterior) - set(cut_a) - cut_b
        order = 8 + len(remaining)
        anchor_degrees = tuple(int(anchor in stars) + sum(anchor in masks[vertex][index] for vertex in remaining)
                               for index, side in enumerate(sides) for anchor in side if anchor != pivots[index]
                               and anchor != pivot)
        if pivot != pivots[1]:
            old_pivot_degree = int(pivots[1] in stars) + sum(pivots[1] in masks[vertex][1] for vertex in remaining)
            anchor_degrees += (old_pivot_degree,)
        if both:
            assert 1 <= codegree <= degree - 5
            minimum = 4 if degree == 8 and codegree == 3 else max(0, order - 23)
            assert len(anchor_degrees) == 8 and all(minimum <= value <= 7 for value in anchor_degrees)
        codes[pivot] = (degree, codegree, min(anchor_degrees), max(anchor_degrees))
    return codes


def run_projection(row, mode):
    _, spec = parse(row)
    problem, metadata = instance(*spec, residual=True, attachment=mode)
    with Cadical195(bootstrap_with=problem.formula.clauses) as solver:
        if not solver.solve():
            return None
        return support_model(problem, metadata, solver.get_model(), both=mode == 'joint')


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('keys', type=Path, nargs='+')
    parser.add_argument('--detail', action='store_true')
    args = parser.parse_args()
    for path in args.keys:
        counts = Counter()
        timings = Counter()
        for row in path.read_text().splitlines():
            name, _ = parse(row)
            outcomes = []
            for mode in ('single', 'joint'):
                start = process_time()
                outcome = run_projection(row, mode)
                timings[mode] += process_time() - start
                outcomes.append(outcome)
            single, joint = outcomes
            assert single is not None or joint is None
            counts[(single is not None, joint is not None)] += 1
            if args.detail:
                print(name, single, joint, flush=True)
        print(path, sorted(counts.items()), dict(timings), flush=True)


if __name__ == '__main__':
    main()
