#!/usr/bin/env python3
"""Full maximum-root extension pilot with eager or lazy square bounds."""

import argparse
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import time

from pysat.solvers import Cadical195

from factor_sat import Formula, graph_matrix
from mask_sat import independent_witness
from max_root import catalogue, count_edges, squares_floor
from kernel_projection import bits, decode, encode, independent_masks


def build(formula, kernel, order, degree, variant):
    matrix, outer = graph_matrix(formula, kernel, order, degree)
    vertices = range(order)
    fixed = tuple(vertex for vertex in vertices if vertex not in outer)
    max_squares = count_edges(kernel)
    max_singles = min(degree, (degree * max_squares) // 2 - squares_floor(order, degree))
    tight = max_singles == 0 and degree * max_squares == 2 * squares_floor(order, degree)
    for row in matrix:
        formula.exactly(row, degree)
    for first, second in zip(outer, list(outer)[1:]):
        formula.lex_leq(zip(matrix[first][:len(fixed)], matrix[second][:len(fixed)]))
    for first, second, third in combinations(vertices, 3):
        formula.add(-matrix[first][second], -matrix[first][third], -matrix[second][third])

    thresholds = [[(-formula.true,) * 2 for _ in vertices] for _ in vertices]
    singletons = defaultdict(list)
    for first, second in combinations(vertices, 2):
        edge = matrix[first][second]
        if edge == formula.true:
            continue
        shared = [formula.both(matrix[first][other], matrix[second][other]) for other in vertices]
        shared = [term for term in shared if term != -formula.true]
        formula.atmost(shared, 3)
        formula.atleast(shared, 2 if tight else 1, unless=(edge,))
        if len(shared) < 2:
            two = -formula.true
        else:
            two = formula.var()
            formula.atleast(shared, 2, unless=(-two,))
            formula.atmost(shared, 1, unless=(two,))
        if len(shared) < 3:
            three = -formula.true
        else:
            three = formula.var()
            formula.atleast(shared, 3, unless=(-three,))
            formula.atmost(shared, 2, unless=(three,))
        thresholds[first][second] = thresholds[second][first] = (two, three)
        if not tight and max_singles < degree:
            single = formula.both(-edge, -two)
            singletons[first].append(single)
            singletons[second].append(single)
    for singles in singletons.values():
        formula.atmost(singles, max_singles)

    for first, second in combinations(vertices, 2):
        edge = matrix[first][second]
        if edge == -formula.true or variant == 'baseline' or (variant == 'fixed' and edge != formula.true):
            continue
        if tight:
            terms = [formula.both(matrix[second][other], thresholds[first][other][1])
                     for other in vertices if other not in (first, second)]
            limit = max_squares - (degree - 1)
            formula.atleast(terms, limit, unless=(-edge,))
        else:
            terms = [formula.both(matrix[second][other], threshold) for other in vertices
                     if other not in (first, second) for threshold in thresholds[first][other]]
            limit = max_squares
        formula.atmost(terms, limit, unless=(-edge,))

    adj = [sum((matrix[first][second] == formula.true) << second for second in fixed) for first in fixed]
    for seed in independent_masks(adj, (1 << len(fixed)) - 1):
        missing = degree + 1 - seed.bit_count()
        if not 1 <= missing <= 3:
            continue
        avoid = []
        for vertex in outer:
            hit = -formula.true
            for coord in bits(seed):
                hit = -formula.both(-hit, -matrix[vertex][coord])
            avoid.append(-hit)
        formula.atmost(avoid, (0, 0, 2, 5)[missing])
    return matrix


def excess_square_edges(adj, maximum):
    for first, row in enumerate(adj):
        for second in bits(row & ~((1 << (first + 1)) - 1)):
            squares = {(min(left, right), max(left, right))
                       for left in bits(row ^ (1 << second))
                       for right in bits(adj[second] & adj[left] & ~(1 << first))}
            if len(squares) > maximum:
                edges = {(first, second)}
                for left, right in sorted(squares)[:maximum + 1]:
                    if not row >> left & 1:
                        left, right = right, left
                    edges.update((tuple(sorted((first, left))), tuple(sorted((second, right))),
                                  tuple(sorted((left, right)))))
                return edges
    return ()


def run(kernel, order, degree, variant, output):
    start = time.process_time()
    maximum = count_edges(kernel)
    with Cadical195() as solver:
        formula = Formula(solver)
        matrix = build(formula, kernel, order, degree, variant)
        print(f'built cpu={time.process_time()-start:.4f} vars={formula.variables} clauses={formula.clauses}', flush=True)
        checked = alpha_cuts = square_cuts = emitted = 0
        while solver.solve():
            checked += 1
            positive = set(solver.get_model())
            adj = [sum((edge in positive) << vertex for vertex, edge in enumerate(row)) for row in matrix]
            edges = excess_square_edges(adj, maximum)
            if edges:
                assert variant != 'eager'
                formula.add(*(-matrix[first][second] for first, second in sorted(edges)))
                square_cuts += 1
                continue
            complement = [((1 << order) - 1) & ~(row | (1 << index)) for index, row in enumerate(adj)]
            witness = independent_witness(complement, degree + 1)
            if witness:
                formula.add(*(matrix[first][second] for first, second in combinations(bits(witness), 2)))
                alpha_cuts += 1
                continue
            print(encode(adj), file=output, flush=True)
            formula.add(*(-matrix[first][second] for first, second in combinations(range(order), 2)
                          if adj[first] >> second & 1))
            emitted += 1
        print(f'exhausted cpu={time.process_time()-start:.4f} graphs={emitted} '
              f'candidates={checked} alpha_cuts={alpha_cuts} square_cuts={square_cuts} {solver.accum_stats()}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('order', type=int)
    parser.add_argument('degree', type=int)
    parser.add_argument('index', type=int)
    parser.add_argument('variant', choices=('baseline', 'fixed', 'eager'))
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    code = list(catalogue(args.order, args.degree))[args.index]
    print(f'kernel_index={args.index} graph6={code!r} variant={args.variant}', flush=True)
    with args.output.open('w') as output:
        run(decode(code), args.order, args.degree, args.variant, output)


if __name__ == '__main__':
    main()
