#!/usr/bin/env python3
"""Unpinned two-side incidence model for a perfect-matching kernel."""

import argparse
from itertools import combinations, permutations
from pathlib import Path
import time

from pysat.solvers import Cadical195

from factor_sat import Formula, decode
from matching_kernel import perfect_matching


def build(formula, degree, order, symmetry):
    width = degree - 1
    outside = order - 2 * degree
    left, right = [[[formula.var() for _ in range(width)] for _ in range(outside)] for _ in range(2)]
    for first, second in zip(left, right):
        for left_lit, right_lit in zip(first, second):
            formula.add(-left_lit, -right_lit)
        for row in (first, second):
            formula.atleast(row, 1)
            formula.atmost(row, 3)
    for side in (left, right):
        for coordinate in range(width):
            formula.exactly([row[coordinate] for row in side], width - 1)
        for first, second in combinations(range(width), 2):
            formula.atmost([formula.both(row[first], row[second]) for row in side], 2)
        if order < 6 * degree - 12:
            for first, second, third in combinations(range(width), 3):
                formula.atmost([formula.both(formula.both(row[first], row[second]), row[third]) for row in side], 1)
    for first in range(width):
        for second in range(width):
            if first != second:
                formula.atmost([formula.both(row[first], opposite[second])
                                for row, opposite in zip(left, right)], 3)
    for first, second in combinations(range(outside), 2):
        cross = [formula.both(edge, partner) for source, target in ((left, right), (right, left))
                 for edge, partner in zip(source[first], target[second])]
        for side in (left, right):
            for edge, partner in zip(side[first], side[second]):
                formula.add(-edge, -partner, *cross)
    if symmetry:
        joined = [first + second for first, second in zip(left, right)]
        for first, second in zip(joined, joined[1:]):
            formula.lex_leq(zip(first, second))
        for first, second in zip(range(width - 1), range(1, width)):
            formula.lex_leq((row[first], row[second]) for row in left)
    return left, right


def control(args, solver, graph_sides):
    assert args.degree == 5
    kernel = decode(args.catalogue.read_text().splitlines()[args.index])
    pairing = perfect_matching(kernel, 0)
    width = args.degree - 1
    inside = range(args.degree + 1, 2 * args.degree)
    for line in args.control.read_text().splitlines():
        graph = decode(line)
        original = [(tuple(bool(graph[index] >> (coord + 1) & 1) for coord in range(width)),
                     tuple(bool(graph[index] >> inside[target] & 1) for target in pairing))
                    for index in range(2 * args.degree, len(graph))]
        arrangements = [sorted((tuple(left[index] for index in perm), tuple(right[index] for index in perm))
                               for left, right in original) for perm in permutations(range(width))]
        minimum = min(arrangements, key=lambda rows: ([left for left, _ in rows], [right for _, right in rows]))
        assumptions = [edge if value else -edge for side, matrix in enumerate(graph_sides)
                       for row, values in zip(matrix, minimum) for edge, value in zip(row, values[side])]
        assert solver.solve(assumptions=assumptions)
    print(f'PASS ambient C16 solutions={len(args.control.read_text().splitlines())}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('degree', type=int)
    parser.add_argument('order', type=int)
    parser.add_argument('--no-symmetry', action='store_true')
    parser.add_argument('--control', type=Path)
    parser.add_argument('--catalogue', type=Path)
    parser.add_argument('--index', type=int)
    args = parser.parse_args()
    with Cadical195() as solver:
        start = time.process_time()
        formula = Formula(solver)
        sides = build(formula, args.degree, args.order, not args.no_symmetry)
        print(f'build_cpu={time.process_time()-start:.6f} variables={formula.variables} clauses={formula.clauses}',
              flush=True)
        if args.control:
            control(args, solver, sides)
        else:
            solve_start = time.process_time()
            state = solver.solve()
            print(f'feasible={int(state)} solve_cpu={time.process_time()-solve_start:.6f} {solver.accum_stats()}')
            if state:
                positive = set(solver.get_model())
                for side in sides:
                    print(' '.join(str(sum((edge in positive) << coord for coord, edge in enumerate(row)))
                                   for row in side))


if __name__ == '__main__':
    main()
