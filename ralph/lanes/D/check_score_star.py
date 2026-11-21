#!/usr/bin/env python3
"""Check both rooted-star score rows after deleting all exterior edges."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path

from pysat.solvers import Cadical195

from check_score_sat import direct_score
from compact_tight import SharedFormula
from forest_score import circulant
from kernel_projection import bits, decode
from max_root import catalogue, squares_floor
from score_sat import star_score_terms
from score_star import add_mixed_at_roots, add_star, attachment_matrix, base


def reroot(graph, first, second):
    front = list(bits(graph[first] ^ (1 << second))) + list(bits(graph[second] ^ (1 << first)))
    fixed = front + [first, second]
    rest = sorted(set(range(len(graph))) - set(fixed),
                  key=lambda vertex: tuple(graph[vertex] >> coord & 1 for coord in fixed))
    perm = fixed + rest
    return [sum((graph[vertex] >> coord & 1) << index for index, coord in enumerate(perm)) for vertex in perm]


def pin(formula, matrix, graph):
    for first, second in combinations(range(len(graph)), 2):
        formula.add(matrix[first][second] if graph[first] >> second & 1 else -matrix[first][second])


def rooted(graph, degree):
    width = 2 * degree
    roots = width - 2, width - 1
    kernel = [row & ((1 << roots[0]) - 1) for row in graph[:roots[0]]]
    projected = [row if coord < width else row & ((1 << width) - 1) for coord, row in enumerate(graph)]
    no_singletons = all((graph[first] & graph[second]).bit_count() >= 2
                        for first, second in combinations(range(len(graph)), 2) if not graph[first] >> second & 1)
    with Cadical195() as solver:
        formula = SharedFormula(solver)
        matrix, _ = attachment_matrix(formula, kernel, len(graph), degree)
        checks = []
        scores = []
        for edge, terms in star_score_terms(formula, matrix, *roots, no_singletons):
            want = direct_score(graph, *edge)
            scores.append(want)
            assert want == direct_score(projected, *edge)
            thresholds = formula.thresholds(terms, degree)
            checks.extend(threshold if want > index else -threshold for index, threshold in enumerate(thresholds))
        assert len(scores) == 2 * degree - 1
        pin(formula, matrix, projected)
        assert solver.solve()
        model = set(solver.get_model())
        for lit in checks:
            assert lit in model and not solver.solve(assumptions=[-lit])

    mixed = True
    for root in roots:
        for other, row in enumerate(graph):
            if other == root or row >> root & 1 or (common := row & graph[root]).bit_count() != 3:
                continue
            marks = [(graph[first] & graph[second]).bit_count() for first, second in combinations(bits(common), 2)]
            mixed &= len(set(marks)) > 1
    with Cadical195() as solver:
        formula = SharedFormula(solver)
        matrix, _ = attachment_matrix(formula, kernel, len(graph), degree)
        add_mixed_at_roots(formula, matrix, roots)
        pin(formula, matrix, projected)
        assert solver.solve() == mixed
    return len(checks), mixed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('controls', type=Path)
    args = parser.parse_args()
    controls = [decode(code) for path in sorted(args.controls.glob('eager-*.g6'))
                for code in path.read_text().splitlines()]
    assert len(controls) == 13
    checks = Counter()
    for control in controls + [circulant(20, (-6, -5, -2, 2, 5, 6))]:
        degree = control[0].bit_count()
        for first, second in combinations(range(len(control)), 2):
            if not control[first] >> second & 1:
                continue
            graph = reroot(control, first, second)
            count, mixed = rooted(graph, degree)
            checks[len(control), 'thresholds'] += count
            checks[len(control), 'mixed', mixed] += 1
    assert checks[16, 'mixed', True] and checks[20, 'mixed', False]
    print(f'PASS independent two-star thresholds and mixed checks: {dict(checks)}', flush=True)

    degree = 5
    width = 2 * degree
    clebsch = [graph for graph in controls if all(direct_score(graph, first, second) == 4
               for first, row in enumerate(graph) for second in bits(row) if second > first)]
    assert len(clebsch) == 1
    graph = reroot(clebsch[0], 0, next(bits(clebsch[0][0])))
    projected = [row if coord < width else row & ((1 << width) - 1) for coord, row in enumerate(graph)]
    kernel = [row & ((1 << (width - 2)) - 1) for row in graph[:width - 2]]
    for mode, count, expected in [('dense', 8, True), ('dense', 9, False),
                                  ('balanced', 4, True), ('balanced', 3, False)]:
        with Cadical195() as solver:
            formula = SharedFormula(solver)
            matrix = base(formula, kernel, len(graph), degree, 6)
            add_star(formula, matrix, degree, mode, 4, dense_min=count, balanced_degree=count)
            pin(formula, matrix, projected)
            assert solver.solve() == expected
    counts = Counter()
    for code in catalogue(16, 5):
        kernel = decode(code)
        if sum(row.bit_count() for row in kernel) * 5 != 4 * squares_floor(16, 5):
            continue
        with Cadical195() as solver:
            formula = SharedFormula(solver)
            base(formula, kernel, 16, 5, 6)
            counts[solver.solve()] += 1
    assert counts == {True: 1, False: 2}
    print(f'PASS known tight C16 projected keys: {dict(counts)}; four opposite forced-mark controls')


if __name__ == '__main__':
    main()
