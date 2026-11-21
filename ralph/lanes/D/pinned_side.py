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
                 triangle=True, codegree='all', fixed_min_cycles=False):
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

    if fixed_min_cycles:
        minimum = sum(row.bit_count() for row in kernel) // 2
        thresholds = {}

        def common_terms(first, second, excluded=None):
            return [formula.both(edge[first][witness], edge[second][witness])
                    for witness in range(order) if witness != excluded
                    and edge[first][witness] != -yes and edge[second][witness] != -yes]

        def codegree_thresholds(first, second):
            key = tuple(sorted((first, second)))
            if key not in thresholds:
                products = common_terms(first, second)
                fixed_count = products.count(yes)
                hits = [product for product in products if product != yes]
                selected = []
                for target in (2, 3):
                    if target <= fixed_count:
                        selected.append(yes)
                    elif target > fixed_count + len(hits):
                        selected.append(-yes)
                    else:
                        claim = formula.var()
                        formula.atleast(hits, target - fixed_count, (-claim,))
                        selected.append(claim)
                formula.add(-selected[1], selected[0])
                thresholds[key] = tuple(selected)
            return thresholds[key]

        for coord in range(1, degree + 1):
            neighbors = [vertex for vertex, literal in enumerate(edge[coord]) if literal == yes]
            for endpoint in neighbors:
                if fixed_min_cycles == 'deficit':
                    flags = [flag for other in neighbors if other != endpoint
                             for flag in codegree_thresholds(endpoint, other)]
                    formula.atleast(flags, minimum)
                else:
                    common = [term for other in neighbors if other != endpoint
                              for term in common_terms(endpoint, other, coord)]
                    formula.atleast(common, minimum)

    return edge


def enumerate_profile(degree, kernel, side, profile, min_edge, mode, output, diameter=True, private=True,
                      triangle=True, codegree='all', fixed_min_cycles=False):
    start = time.process_time()
    outputs = 0
    cuts = 0
    with Cadical195() as solver:
        formula = Formula(solver)
        matrix = pinned_graph(formula, degree, kernel, side, profile, min_edge, diameter, private, triangle,
                              codegree, fixed_min_cycles)
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
    parser.add_argument('--fixed-min-cycles', choices=('direct', 'deficit'))
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
    assert args.fixed_min_cycles != 'deficit' or args.codegree == 'all'
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
                             args.codegree, args.fixed_min_cycles)
                with args.export_cnf.open('w') as dimacs:
                    print(f'p cnf {formula.variables} {len(clauses)}', file=dimacs)
                    dimacs.writelines(' '.join(map(str, clause + [0])) + '\n' for clause in clauses)
                return
            enumerate_profile(args.degree, kernel, args.side, profile, args.min_edge, args.mode, output,
                              not args.omit_diameter, not args.omit_private, not args.omit_outer_triangles,
                              args.codegree, args.fixed_min_cycles)


if __name__ == '__main__':
    main()
