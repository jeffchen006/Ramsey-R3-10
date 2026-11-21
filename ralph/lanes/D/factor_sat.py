#!/usr/bin/env python3
"""Two-side mask marginals and a slot-based, exact rooted extension encoding."""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import time

from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195

from kernel_cnf import ROOT
from mask_sat import bits, decode, independent_witness


def subsets(width, bound):
    for size in range(1, bound + 1):
        for group in combinations(range(width), size):
            yield sum(1 << item for item in group)


def intersecting_families(types):
    neighbors = {mask: {other for other in types if mask != other and mask & other} for mask in types}

    def extend(chosen, candidates, ruled):
        if not candidates and not ruled:
            yield chosen
        if candidates:
            pivot = max(sorted(candidates | ruled), key=lambda mask: len(candidates & neighbors[mask]))
            for vertex in sorted(candidates - neighbors[pivot]):
                yield from extend(chosen + (vertex,), candidates & neighbors[vertex], ruled & neighbors[vertex])
                candidates.remove(vertex)
                ruled.add(vertex)

    yield from extend((), set(types), set())


class Formula:
    def __init__(self, solver):
        self.solver = solver
        self.variables = 0
        self.clauses = 0
        self.products = {}
        self.true = self.var()
        self.add(self.true)

    def var(self):
        self.variables += 1
        return self.variables

    def add(self, *lits):
        if self.true in lits and (len(lits) != 1 or self.clauses):
            return
        clause = set(lit for lit in lits if lit != -self.true)
        if not any(-lit in clause for lit in clause):
            self.solver.add_clause(sorted(clause, key=lambda lit: (abs(lit), lit)))
            self.clauses += 1

    def atmost(self, lits, bound, unless=()):
        bound -= lits.count(self.true)
        lits = [lit for lit in lits if abs(lit) != self.true]
        if bound < 0:
            self.add(*unless)
        elif bound == 0:
            for lit in lits:
                self.add(*unless, -lit)
        elif bound < len(lits):
            enc = CardEnc.atmost(lits, bound, top_id=self.variables, encoding=EncType.seqcounter)
            self.variables = max(enc.nv, self.variables)
            for clause in enc.clauses:
                self.add(*unless, *clause)

    def atleast(self, lits, bound, unless=()):
        self.atmost([-lit for lit in lits], len(lits) - bound, unless)

    def exactly(self, lits, bound):
        self.atmost(lits, bound)
        self.atleast(lits, bound)

    def both(self, left, right):
        if left == right or abs(right) == self.true:
            return left if right != -self.true else right
        if abs(left) == self.true:
            return right if left == self.true else left
        if left == -right:
            return -self.true
        key = tuple(sorted((left, right)))
        if key not in self.products:
            prod = self.var()
            self.add(-prod, left)
            self.add(-prod, right)
            self.add(prod, -left, -right)
            self.products[key] = prod
        return self.products[key]


def add_obstructions(formula, degree, occupants, fixed, library):
    clauses = set()
    for width, reports in sorted(library.items()):
        for support in combinations(range(degree), int(width)):
            translated = {pattern: sum(1 << support[coord] for coord in bits(pattern))
                          for pattern in range(1, 1 << len(support))}
            for masks in reports:
                needed = Counter(translated[mask] for mask in masks)
                clause = []
                for mask, count in needed.items():
                    demand = count - fixed[mask]
                    if demand <= 0:
                        continue
                    levels = occupants.get(mask, ())
                    if demand > len(levels):
                        break
                    clause.append(-levels[demand - 1])
                else:
                    clauses.add(tuple(sorted(clause)))
    minimal = set()
    for clause in sorted(clauses, key=lambda row: (len(row), row)):
        if not any(subset in minimal for size in range(len(clause)) for subset in combinations(clause, size)):
            formula.add(*clause)
            minimal.add(clause)
    return len(minimal)


def build_side(formula, kernel, order, degree, minimum, shadow, side, library, no_k33):
    width = degree - 1
    own = list(range(side * width, (side + 1) * width))
    opposite = range((1 - side) * width, (2 - side) * width)
    loc = (1 << width) - 1
    fixed = Counter(((kernel[vertex] >> (side * width)) & loc) | (1 << width) for vertex in opposite)
    pair_bounds = {pair: 2 - sum(count for mask, count in fixed.items() if mask & pair == pair)
                   for pair in subsets(width, 2) if pair.bit_count() == 2}
    occupants = {}
    if no_k33 and any(mask.bit_count() == 3 and count > 1 for mask, count in fixed.items()):
        formula.add()
    for mask in subsets(width, 3):
        capacity = min((bound for pair, bound in pair_bounds.items() if mask & pair == pair), default=1)
        if no_k33 and mask.bit_count() == 3:
            capacity = min(capacity, 1)
        if capacity > 0:
            occupants[mask] = [formula.var() for _ in range(capacity)]
            for previous, later in zip(occupants[mask], occupants[mask][1:]):
                formula.add(-later, previous)

    def collect(predicate):
        return [lit for mask, lits in occupants.items() if predicate(mask) for lit in lits]

    formula.exactly(collect(lambda mask: True), order - 2 * degree)
    for local, vertex in enumerate(own):
        formula.exactly(collect(lambda mask: mask >> local & 1), width - kernel[vertex].bit_count())
        if minimum is not None:
            baseline = sum(kernel[neighbor].bit_count() for neighbor in bits(kernel[vertex]))
            contributions = [lit for mask, lits in occupants.items() if mask >> local & 1
                             for lit in lits * (mask.bit_count() - 1)]
            formula.atleast(contributions, minimum - baseline)
    for pair, bound in pair_bounds.items():
        formula.atmost(collect(lambda mask: mask & pair == pair), bound)
    if minimum is not None:
        lower = (degree * minimum + 1) // 2 - (2 * degree * width - 3 * (order - degree - 1))
        formula.atleast(collect(lambda mask: mask.bit_count() == 1), lower - fixed[1 << width])

    rows = set()
    for support in subsets(degree, shadow):
        types = [mask for mask in (occupants.keys() | fixed.keys()) if mask & ~support == 0]
        for family in intersecting_families(types):
            source = 0
            for mask in family:
                source |= mask
            lits = tuple(sorted(lit for mask in family for lit in occupants.get(mask, ())))
            bound = source.bit_count() - sum(fixed[mask] for mask in family)
            if bound < len(lits):
                rows.add((lits, bound))
    for lits, bound in sorted(rows):
        formula.atmost(list(lits), bound)
    forbidden = add_obstructions(formula, degree, occupants, fixed, library)
    return occupants, len(rows), forbidden


def channel(formula, occupants, memberships):
    selections = {mask: [formula.var() for _ in memberships] for mask in occupants}
    for index, mem in enumerate(memberships):
        formula.add(*(lits[index] for lits in selections.values()))
        for mask, lits in selections.items():
            for bit, lit in enumerate(mem):
                formula.add(-lits[index], lit if mask >> bit & 1 else -lit)
    for mask, levels in occupants.items():
        lits = selections[mask]
        formula.atmost(lits, len(levels))
        for index, level in enumerate(levels, 1):
            formula.atmost(lits, index - 1, (level,))
            formula.atleast(lits, index, (-level,))
    return selections


def graph_matrix(formula, kernel, order, degree):
    width = len(kernel)
    outer = range(width + 2, order)
    matrix = [[-formula.true] * order for _ in range(order)]
    for left, right in combinations(range(order), 2):
        if right < width:
            fixed = bool(kernel[left] >> right & 1)
        elif right == width:
            fixed = left < degree - 1
        elif right == width + 1:
            fixed = left >= degree - 1
        else:
            fixed = False if left in (width, width + 1) else None
        edge = formula.var() if fixed is None else (formula.true if fixed else -formula.true)
        matrix[left][right] = matrix[right][left] = edge
    return matrix, outer


def join(formula, kernel, order, degree, profiles, shadow_edges):
    width = degree - 1
    matrix, outer = graph_matrix(formula, kernel, order, degree)
    selections = []
    for side, occupants in enumerate(profiles):
        membership = [matrix[vertex][side * width:(side + 1) * width] for vertex in outer]
        selections.append(channel(formula, occupants, membership))
    for left, right in zip(outer, list(outer)[1:]):
        equal = formula.true
        for first, second in zip(reversed(matrix[left][:2 * width]), reversed(matrix[right][:2 * width])):
            formula.add(-equal, -first, second)
            same = formula.var()
            formula.add(-same, -first, second)
            formula.add(-same, first, -second)
            formula.add(same, -first, -second)
            formula.add(same, first, second)
            equal = formula.both(equal, same)

    for vertex in outer:
        formula.exactly(matrix[vertex], degree)
    for left, middle, right in combinations(range(order), 3):
        if right in outer:
            formula.add(-matrix[left][middle], -matrix[left][right], -matrix[middle][right])
    for left, right in combinations(range(order), 2):
        if matrix[left][right] == formula.true or right in (2 * width, 2 * width + 1):
            continue
        if right not in outer and (left < width) == (right < width):
            continue
        products = [formula.both(matrix[left][item], matrix[right][item]) for item in range(order)]
        formula.atmost(products, 3)
        formula.add(matrix[left][right], *products)

    if shadow_edges:
        for side, selected in enumerate(selections):
            for first, second in combinations(range(width), 2):
                single_a = selected.get(1 << first)
                single_b = selected.get(1 << second)
                pair = (1 << first) | (1 << second)
                if single_a is None or single_b is None or pair not in selected:
                    continue
                present = profiles[side][pair][0]
                for idx, left in enumerate(outer):
                    for jdx, right in enumerate(outer):
                        if idx != jdx:
                            formula.add(-single_a[idx], -single_b[jdx], -present, matrix[left][right])
    return matrix


def encode(adjacency):
    flags = [int(bool(adjacency[right] >> left & 1)) for right in range(len(adjacency)) for left in range(right)]
    flags.extend([0] * (-len(flags) % 6))
    return chr(63 + len(adjacency)) + ''.join(chr(63 + sum(flags[start + offset] << (5 - offset)
                   for offset in range(6))) for start in range(0, len(flags), 6))


def run(args, kernel, output):
    start = time.process_time()
    minimum = sum(row.bit_count() for row in kernel) // 2 if args.min_edge else None
    library = json.loads(args.obstructions.read_text()) if args.obstructions else {}
    with Cadical195() as solver:
        formula = Formula(solver)
        sides = (0, 1) if args.side is None else (args.side,)
        builds = [build_side(formula, kernel, args.order, args.degree, minimum, args.shadow, side, library, args.no_k33)
                  for side in sides]
        profiles = [occupants for occupants, _, _ in builds]
        matrix = join(formula, kernel, args.order, args.degree, profiles, args.shadow_edges) if args.side is None else None
        print(f'ENCODE types={list(map(len, profiles))} shadow={tuple(rows for _, rows, _ in builds)} '
              f'obstructions={tuple(forbidden for _, _, forbidden in builds)} '
              f'variables={formula.variables} clauses={formula.clauses} cpu={time.process_time()-start:.4f}', flush=True)
        outputs = 0
        iterations = 0
        learned = 0
        while not args.limit or outputs < args.limit:
            if not solver.solve():
                print(f'EXHAUSTED outputs={outputs} iterations={iterations} independent_cuts={learned} '
                      f'cpu={time.process_time()-start:.4f}', flush=True)
                return
            iterations += 1
            if iterations in (1, 10, 100, 1000, 10000):
                print(f'PROGRESS iterations={iterations} outputs={outputs} cpu={time.process_time()-start:.4f}', flush=True)
            positive = set(lit for lit in solver.get_model() if lit > 0)
            if matrix is None:
                profile = [(mask, sum(level in positive for level in levels)) for mask, levels in profiles[0].items()]
                print(' '.join(f'{mask}:{count}' for mask, count in profile if count), file=output)
                formula.add(*(-level for levels in profiles[0].values() for level in levels if level in positive))
            else:
                adj = [sum(1 << neighbor for neighbor, edge in enumerate(row) if edge in positive) for row in matrix]
                universe = (1 << args.order) - 1
                indep = independent_witness([universe ^ (neighbors | 1 << vertex) for vertex, neighbors in enumerate(adj)],
                                            args.degree + 1)
                if indep:
                    formula.add(*(matrix[left][right] for left, right in combinations(bits(indep), 2)))
                    learned += 1
                    continue
                print(encode(adj), file=output, flush=True)
                formula.add(*(-matrix[left][right] for left, right in combinations(range(args.order), 2)
                              if matrix[left][right] in positive))
            outputs += 1
        print(f'LIMIT outputs={outputs} iterations={iterations} independent_cuts={learned} '
              f'cpu={time.process_time()-start:.4f}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('order', type=int)
    parser.add_argument('degree', type=int)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('index', type=int)
    parser.add_argument('output', type=Path)
    parser.add_argument('--min-edge', action='store_true')
    parser.add_argument('--side', choices=(0, 1), type=int)
    parser.add_argument('--shadow', default=4, type=int, choices=range(0, 6))
    parser.add_argument('--shadow-edges', action='store_true')
    parser.add_argument('--obstructions', type=Path)
    parser.add_argument('--no-k33', action='store_true')
    parser.add_argument('--limit', default=0, type=int)
    args = parser.parse_args()
    kernel = decode(args.catalogue.read_text().splitlines()[args.index])
    assert len(kernel) == 2 * (args.degree - 1) and args.order > 2 * args.degree
    assert all(row.bit_count() <= 2 for row in kernel), 'This implementation only handles cap 3 kernels.'
    assert not args.no_k33 or args.order < 6 * args.degree - 12
    width = args.degree - 1
    assert all(not (row >> width) if index >= width else not (row & ((1 << width) - 1))
               for index, row in enumerate(kernel))
    with args.output.open('w') as output:
        run(args, kernel, output)


if __name__ == '__main__':
    main()
