#!/usr/bin/env python3
"""Shared totalizers and an optional global no-2/2-square clause family."""

from collections import defaultdict
from itertools import combinations

from factor_sat import Formula, graph_matrix
from kernel_cnf import Cnf
from kernel_projection import bits, independent_masks
from max_root import count_edges, squares_floor


class SharedFormula(Formula):
    new = Formula.var
    totalizer = Cnf.totalizer

    def add(self, *lits):
        return super().add(*(self.true if lit is True else -self.true if lit is False else lit for lit in lits))

    def thresholds(self, lits, cap):
        constant = min(cap, lits.count(self.true))
        variable = [lit for lit in lits if abs(lit) != self.true]
        out = [self.true] * constant + self.totalizer(variable, cap - constant)
        return out + [-self.true] * (cap - len(out))


def square22_clauses(formula, shared, high):
    for (first, second), common in shared.items():
        for (left, lit_left), (right, lit_right) in combinations(common, 2):
            if (first, second) < (left, right):
                formula.add(high[first][second], high[left][right], -lit_left, -lit_right)


def build_shared(formula, kernel, order, degree, mode, no22):
    matrix, outer = graph_matrix(formula, kernel, order, degree)
    vertices = range(order)
    width = 2 * degree
    maximum = count_edges(kernel)
    max_singles = min(degree, degree * maximum // 2 - squares_floor(order, degree))
    tight = degree * maximum == 2 * squares_floor(order, degree)
    assert not no22 or tight
    for row in matrix:
        formula.exactly(row, degree)
    for first, second in zip(outer, list(outer)[1:]):
        formula.lex_leq(zip(matrix[first][:width], matrix[second][:width]))
    for first, second, third in combinations(vertices, 3):
        formula.add(-matrix[first][second], -matrix[first][third], -matrix[second][third])

    twos = [[-formula.true for _ in vertices] for _ in vertices]
    high = [[-formula.true for _ in vertices] for _ in vertices]
    shared = {}
    singles = defaultdict(list)
    for first, second in combinations(vertices, 2):
        edge = matrix[first][second]
        if edge == formula.true:
            continue
        common = [(other, term) for other in vertices
                  if (term := formula.both(matrix[first][other], matrix[second][other])) != -formula.true]
        once, twice, thrice, four = formula.thresholds([term for _, term in common], 4)
        formula.add(-four)
        formula.add(edge, twice if tight else once)
        twos[first][second] = twos[second][first] = twice
        high[first][second] = high[second][first] = thrice
        if no22 and thrice != formula.true:
            shared[first, second] = common
        if not tight and max_singles < degree:
            single = formula.both(-edge, -twice)
            singles[first].append(single)
            singles[second].append(single)
    for terms in singles.values():
        formula.atmost(terms, max_singles)
    if tight:
        n3 = degree * (degree - 1) - 2 * (order - 1 - degree)
        for row in high:
            formula.exactly(row, n3)
    if no22:
        square22_clauses(formula, shared, high)

    for first, second in combinations(vertices, 2):
        edge = matrix[first][second]
        if edge == -formula.true or mode == 'baseline' or (mode == 'fixed' and edge != formula.true):
            continue
        rows = (high[first],) if tight else (twos[first], high[first])
        terms = [formula.both(matrix[second][other], row[other]) for row in rows
                 for other in vertices if other not in (first, second)]
        limit = maximum - (degree - 1) if tight else maximum
        formula.atmost(terms, limit, unless=(-edge,))
        if tight:
            formula.atleast(terms, limit, unless=(-edge,))

    adj = [sum((matrix[first][second] == formula.true) << second for second in range(width)) for first in range(width)]
    for seed in independent_masks(adj, (1 << width) - 1):
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
