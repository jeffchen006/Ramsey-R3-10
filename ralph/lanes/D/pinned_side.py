#!/usr/bin/env python3
"""Complete a rooted cap-three graph with one fixed support multiset."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path
import time

from pysat.solvers import Cadical195

from factor_sat import Formula, bits, decode, encode, independent_witness


class ClauseList(list):
    add_clause = list.append


def pinned_graph(formula, degree, kernel, side, profile, min_edge, diameter=True, private=True,
                 triangle=True, codegree='all'):
    width = degree - 1
    limit = (1 << width) - 1
    opposite = range((1 - side) * width, (2 - side) * width)
    fixed = [((kernel[vertex] >> (side * width)) & limit) | (1 << width) for vertex in opposite]
    outer = fixed + sorted(profile.elements())
    order = len(outer) + degree + 1
    yes = formula.true
    edge = [[-yes] * order for _ in range(order)]

    def connect(first, second, literal):
        edge[first][second] = edge[second][first] = literal

    for coord in range(degree):
        connect(0, 1 + coord, yes)
    for row, support in enumerate(outer, start=degree + 1):
        for coord in bits(support):
            connect(row, 1 + coord, yes)
    for first, second in combinations(range(len(outer)), 2):
        if not outer[first] & outer[second]:
            connect(first + degree + 1, second + degree + 1, formula.var())
    if triangle:
        for first, second, third in combinations(range(order), 3):
            triple = (edge[first][second], edge[first][third], edge[second][third])
            if -yes not in triple:
                formula.add(*(-literal for literal in triple))
    for neighbors in edge:
        formula.exactly(neighbors, degree)

    for first, second in combinations(range(order), 2):
        products = [formula.both(edge[first][neighbor], edge[second][neighbor]) for neighbor in range(order)
                    if edge[first][neighbor] != -yes and edge[second][neighbor] != -yes]
        if codegree == 'all' or (codegree == 'coord' and first <= degree):
            formula.atmost(products, 3)
        if diameter:
            formula.add(edge[first][second], *products)
        if private and first > degree:
            source, target = outer[first - degree - 1], outer[second - degree - 1]
            if source & target and min(source.bit_count(), target.bit_count()) == 1:
                formula.atleast(products, 2)

    if min_edge:
        minimum = sum(row.bit_count() for row in kernel) // 2
        reverse = [sum((mask.bit_count() - 1) for mask in outer if mask >> coord & 1)
                   for coord in range(degree)]
        if min(reverse) < minimum:
            formula.add()
        fixed_vertices = range(degree + 1, degree + 1 + len(fixed))
        free_vertices = range(degree + 1 + len(fixed), order)
        for member, support in enumerate(fixed, start=degree + 1):
            products = [formula.both(edge[member][neighbor], edge[other][neighbor])
                        for neighbor in free_vertices for other in fixed_vertices if other != member
                        and edge[member][neighbor] != -yes and edge[other][neighbor] != -yes]
            offset = sum(sum(bool(mask >> coord & 1) for mask in fixed) for coord in bits(support & limit))
            formula.atleast(products, minimum - offset)

    return edge


def enumerate_profile(degree, kernel, side, profile, min_edge, mode, output, diameter=True, private=True,
                      triangle=True, codegree='all'):
    start = time.process_time()
    outputs = 0
    cuts = 0
    with Cadical195() as solver:
        formula = Formula(solver)
        matrix = pinned_graph(formula, degree, kernel, side, profile, min_edge, diameter, private, triangle, codegree)
        order = len(matrix)
        universe = (1 << order) - 1
        while solver.solve():
            positive = set(lit for lit in solver.get_model() if lit > 0)
            if mode == 'relax':
                print(f'FEASIBLE_RELAXATION cuts={cuts} cpu={time.process_time()-start:.5f}', flush=True)
                return
            adj = [sum(1 << target for target, edge in enumerate(row) if edge in positive) for row in matrix]
            indep = independent_witness([universe ^ (neighbors | 1 << vertex)
                                         for vertex, neighbors in enumerate(adj)], degree + 1)
            if indep:
                formula.add(*(matrix[first][second] for first, second in combinations(bits(indep), 2)))
                cuts += 1
            else:
                outputs += 1
                print(encode(adj), file=output, flush=True)
                if mode == 'first':
                    print(f'VALID_MODEL cuts={cuts} cpu={time.process_time()-start:.5f}', flush=True)
                    return
                formula.add(*(-matrix[first][second] for first, second in combinations(range(order), 2)
                              if matrix[first][second] in positive))
        print(f'EXHAUSTED outputs={outputs} cuts={cuts} cpu={time.process_time()-start:.5f}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('degree', type=int)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('index', type=int)
    parser.add_argument('side', type=int, choices=(0, 1))
    parser.add_argument('profiles', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--line', type=int, default=0, help='1-indexed; 0 tests every input profile')
    parser.add_argument('--min-edge', action='store_true')
    parser.add_argument('--mode', choices=('relax', 'first', 'all'), default='all')
    parser.add_argument('--omit-diameter', action='store_true')
    parser.add_argument('--omit-private', action='store_true')
    parser.add_argument('--omit-outer-triangles', action='store_true')
    parser.add_argument('--codegree', default='all', choices=('all', 'coord', 'none'))
    parser.add_argument('--export-cnf', type=Path)
    args = parser.parse_args()
    assert args.mode == 'relax' or (not (args.omit_diameter or args.omit_private or args.omit_outer_triangles)
                                    and args.codegree == 'all')
    kernel = decode(args.catalogue.read_text().splitlines()[args.index])
    assert len(kernel) == 2 * (args.degree - 1) and max(map(int.bit_count, kernel)) <= 2
    assert args.export_cnf is None or (args.mode == 'relax' and args.line > 0)
    with args.output.open('w') as output:
        for pos, line in enumerate(args.profiles.read_text().splitlines(), start=1):
            if args.line and pos != args.line:
                continue
            profile = Counter(dict(tuple(map(int, entry.split(':'))) for entry in line.split()))
            assert all(0 < mask < 1 << (args.degree - 1) and 1 <= mask.bit_count() <= 3 and count > 0
                       for mask, count in profile.items())
            print(f'PIN line={pos} size={sum(profile.values())}', flush=True)
            if args.export_cnf:
                clauses = ClauseList()
                formula = Formula(clauses)
                pinned_graph(formula, args.degree, kernel, args.side, profile, args.min_edge,
                             not args.omit_diameter, not args.omit_private, not args.omit_outer_triangles,
                             args.codegree)
                with args.export_cnf.open('w') as dimacs:
                    print(f'p cnf {formula.variables} {len(clauses)}', file=dimacs)
                    dimacs.writelines(' '.join(map(str, clause + [0])) + '\n' for clause in clauses)
                return
            enumerate_profile(args.degree, kernel, args.side, profile, args.min_edge, args.mode, output,
                              not args.omit_diameter, not args.omit_private, not args.omit_outer_triangles,
                              args.codegree)


if __name__ == '__main__':
    main()
