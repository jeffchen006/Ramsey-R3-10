#!/usr/bin/env python3
"""Attachment-only projection of two maximizing score-two root strata."""

import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import time

from pysat.solvers import Cadical195

from compact_tight import SharedFormula
from factor_sat import graph_matrix
from kernel_projection import bits, decode, encode, independent_masks
from max_root import catalogue, count_edges, squares_floor
from score_sat import direct_scores, star_score_terms
from tight_forest_sat import add_anchor_forests, add_pin


def attachment_matrix(formula, kernel, order, degree):
    matrix, outer = graph_matrix(formula, kernel, order, degree)
    for first, second in combinations(outer, 2):
        matrix[first][second] = matrix[second][first] = -formula.true
    return matrix, outer


def base(formula, kernel, order, degree, pin):
    assert degree * count_edges(kernel) == 2 * squares_floor(order, degree)
    matrix, outer = attachment_matrix(formula, kernel, order, degree)
    width = 2 * degree
    for row in matrix[:width]:
        formula.exactly(row, degree)
    for vertex in outer:
        for row in (matrix[vertex][:degree-1], matrix[vertex][degree-1:width-2]):
            formula.atleast(row, 2)
            formula.atmost(row, 3)
    for first, second in zip(outer, list(outer)[1:]):
        formula.lex_leq(zip(matrix[first][:width], matrix[second][:width]))
    for first, second in combinations(range(width), 2):
        shared = [formula.both(matrix[first][other], matrix[second][other]) for other in range(order)]
        if matrix[first][second] == formula.true:
            formula.atmost(shared, 0)
        else:
            formula.atleast(shared, 2)
            formula.atmost(shared, 3)
    for first, second in combinations(outer, 2):
        shared = [formula.both(matrix[first][other], matrix[second][other]) for other in range(width)]
        formula.atmost(shared, 3)
    root_pair = width - 2, width - 1
    edge_squares = count_edges(kernel)
    for root in root_pair:
        anchors = [coord for coord in range(width - 2) if matrix[root][coord] == formula.true]
        high = {vertex: formula.thresholds([matrix[vertex][coord] for coord in anchors], 3)[2]
                for vertex in outer}
        for anchor in anchors:
            fixed_high = sum(kernel[coord].bit_count() == 2 for coord in bits(kernel[anchor]))
            contributions = [formula.both(matrix[anchor][vertex], high[vertex]) for vertex in outer]
            formula.exactly(contributions, edge_squares - (degree - 1) - fixed_high)
    add_anchor_forests(formula, matrix, degree)
    if pin is not None:
        add_pin(formula, matrix, degree, pin, False, True, kernel)
    adjacency = [sum((matrix[first][second] == formula.true) << second for second in range(width))
                 for first in range(width)]
    for seed in independent_masks(adjacency, (1 << width) - 1):
        missing = degree + 1 - seed.bit_count()
        if 1 <= missing <= 3:
            avoid = [formula.thresholds([matrix[vertex][coord] for coord in bits(seed)], 1)[0]
                     for vertex in outer]
            formula.atmost([-lit for lit in avoid], (0, 0, 2, 5)[missing])
    return matrix


def add_mixed_at_roots(formula, matrix, roots):
    @lru_cache(maxsize=None)
    def high(first, second):
        return formula.thresholds([formula.both(left, right) for left, right in zip(matrix[first], matrix[second])], 3)[2]

    for root in roots:
        neighbors = [coord for coord, lit in enumerate(matrix[root]) if lit == formula.true]
        for other, lit in enumerate(matrix[root]):
            if other == root or lit != -formula.true:
                continue
            eligible = [coord for coord in neighbors if matrix[other][coord] != -formula.true]
            for triple in combinations(eligible, 3):
                marks = [high(first, second) for first, second in combinations(triple, 2)]
                guard = [-matrix[other][coord] for coord in triple]
                formula.add(*guard, *marks)
                formula.add(*guard, *(-mark for mark in marks))


def add_star(formula, matrix, degree, mode, level=2, dense_min=5, balanced_degree=2):
    roots = 2 * degree - 2, 2 * degree - 1
    marked = {root: [] for root in roots}
    for edge, terms in star_score_terms(formula, matrix, *roots, no_singletons=True):
        if edge == roots:
            continue
        root = next(root for root in edge if root in roots)
        thresholds = formula.thresholds(terms, level + 1)
        formula.add(-thresholds[level])
        if mode == 'balanced':
            formula.add(thresholds[0])
        marked[root].append(thresholds[level - 1])
    assert all(len(marks) == degree - 1 for marks in marked.values())
    if mode == 'dense':
        formula.atleast([lit for marks in marked.values() for lit in marks], dense_min)
    elif mode == 'balanced':
        for marks in marked.values():
            formula.exactly(marks, balanced_degree)
        add_mixed_at_roots(formula, matrix, roots)
    else:
        raise ValueError(mode)


def solve(kernel, order, degree, pin, mode, output):
    start = time.process_time()
    with Cadical195() as solver:
        formula = SharedFormula(solver)
        matrix = base(formula, kernel, order, degree, pin)
        base_vars, base_clauses = formula.variables, formula.clauses
        if mode != 'base':
            add_star(formula, matrix, degree, mode)
        print(f'built cpu={time.process_time()-start:.3f} vars={formula.variables} clauses={formula.clauses} '
              f'added_vars={formula.variables-base_vars} added_clauses={formula.clauses-base_clauses}', flush=True)
        status = solver.solve()
        print(f'done cpu={time.process_time()-start:.3f} result={status} {solver.accum_stats()}', flush=True)
        if not status:
            return
        positive = set(solver.get_model())
        graph = [sum((lit in positive) << coord for coord, lit in enumerate(row)) for row in matrix]
        scores = direct_scores(graph)
        roots = 2 * degree - 2, 2 * degree - 1
        assert scores[roots] == 2
        stars = [Counter(score for edge, score in scores.items() if root in edge) for root in roots]
        if mode != 'base':
            assert all(max(star) <= 2 for star in stars)
        if mode == 'dense':
            assert sum(star[2] for star in stars) >= 7
        elif mode == 'balanced':
            assert all(star[0] == 0 and star[2] == 3 for star in stars)
        print(f'projection only, endpoint star score counts={stars}', flush=True)
        output.write_text(encode(graph) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('key', type=int, choices=(24, 25, 26, 28, 29, 32))
    parser.add_argument('pin', type=int, choices=range(6, 15))
    parser.add_argument('mode', choices=('base', 'dense', 'balanced'))
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    code = list(catalogue(40, 9))[args.key]
    print(f'key={args.key} kernel={code!r} pin={args.pin} mode={args.mode}', flush=True)
    solve(decode(code), 40, 9, args.pin, args.mode, args.output)


if __name__ == '__main__':
    main()
