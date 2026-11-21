#!/usr/bin/env python3
"""Exact fixed-residual MTF neighbourhood gluing, with deterministic DIMACS."""

import argparse
from itertools import combinations
from pathlib import Path

from pysat.card import CardEnc

from check_rows import graph, members, saturated


def independent(adj, pool, low, high, chosen=()):
    size = len(chosen)
    if size >= low:
        yield chosen
    if size < high:
        while pool.bit_count() + size >= low and pool:
            bit = pool & -pool
            vertex = bit.bit_length() - 1
            pool ^= bit
            yield from independent(adj, pool & ~adj[vertex], low, high, chosen + (vertex,))


class Formula:
    def __init__(self, last):
        self.last = last
        self.clauses = []

    def new(self):
        self.last += 1
        return self.last

    def add(self, literals):
        self.clauses.append(tuple(literals))

    def bound(self, literals, lower, upper):
        literals = tuple(literals)
        if upper < lower or upper < 0 or lower > len(literals):
            self.add(())
            return
        if lower > 0:
            card = CardEnc.atleast(lits=literals, bound=lower, top_id=self.last)
            self.last = max(self.last, card.nv)
            self.clauses.extend(card.clauses)
        if upper < len(literals):
            card = CardEnc.atmost(lits=literals, bound=upper, top_id=self.last)
            self.last = max(self.last, card.nv)
            self.clauses.extend(card.clauses)

    def write(self, path):
        with path.open('w') as stream:
            print(f'p cnf {self.last} {len(self.clauses)}', file=stream)
            for clause in self.clauses:
                print(*clause, 0, file=stream)


def encode(adj, root_degree, independence, min_degree, total_edges, full=True):
    size = len(adj)
    assert 0 < root_degree <= independence and min_degree <= root_degree
    assert graph.triangle_free(adj) and graph.alpha(adj) < independence
    incident = [[idx * size + vertex + 1 for vertex in range(size)] for idx in range(root_degree)]
    formula = Formula(root_degree * size)
    hedges = sum(map(int.bit_count, adj)) // 2
    cross_edges = None if total_edges is None else total_edges - hedges - root_degree

    for column in incident:
        for vertex, nbrs in enumerate(adj):
            formula.add([column[vertex], *(column[other] for other in members(nbrs))])
            for other in members(nbrs):
                if vertex < other:
                    formula.add((-column[vertex], -column[other]))
        formula.bound(column, min_degree - 1, independence - 1)

    singleton_cap = independence + 1 - root_degree
    max_mask = root_degree if cross_edges is None else min(
        root_degree, cross_edges - 2 * size + root_degree * singleton_cap + 2)
    for vertex, nbrs in enumerate(adj):
        formula.bound((column[vertex] for column in incident), max(1, min_degree - nbrs.bit_count()),
                      min(max_mask, independence - nbrs.bit_count()))

    if max_mask == 2:
        double = []
        for vertex in range(size):
            cell = [column[vertex] for column in incident]
            double.append(formula.new())
            for first, second in combinations(cell, 2):
                formula.add((-first, -second, double[-1]))
            for first in cell:
                formula.add([-double[-1], -first, *(lit for lit in cell if lit != first)])
        formula.bound(double, cross_edges - size, cross_edges - size)
        if cross_edges == 2 * size - root_degree * singleton_cap:
            for column in incident:
                private = []
                for vertex, hit in enumerate(column):
                    private.append(formula.new())
                    formula.add((-private[-1], hit))
                    formula.add((-private[-1], -double[vertex]))
                    formula.add((-hit, double[vertex], private[-1]))
                formula.bound(private, singleton_cap, singleton_cap)
    elif cross_edges is not None:
        formula.bound((lit for column in incident for lit in column), cross_edges, cross_edges)

    for first, second in combinations(range(size), 2):
        if adj[first] >> second & 1 or adj[first] & adj[second]:
            continue
        common = []
        for column in incident:
            common.append(formula.new())
            formula.add((-common[-1], column[first]))
            formula.add((-common[-1], column[second]))
        formula.add(common)

    if full:
        if root_degree >= 2:
            buckets = {independence + 1 - length: list(combinations(incident, length))
                       for length in range(2, root_degree + 1)}
            for indep in independent(adj, (1 << size) - 1, min(buckets), max(buckets)):
                for subset in buckets[len(indep)]:
                    formula.add(column[vertex] for column in subset for vertex in indep)
    return formula, incident


def control(adj, root, independence, full):
    from pysat.solvers import Cadical195

    root_neighbours = list(members(adj[root]))
    exterior = list(members(((1 << len(adj)) - 1) & ~(adj[root] | (1 << root))))
    residual = [sum(((adj[vertex] >> other) & 1) << idx for idx, other in enumerate(exterior))
                for vertex in exterior]
    formula, incident = encode(residual, len(root_neighbours), independence,
                               min(map(int.bit_count, adj)), sum(map(int.bit_count, adj)) // 2, full)
    assumptions = [lit if (adj[neighbour] >> vertex) & 1 else -lit
                   for neighbour, column in zip(root_neighbours, incident)
                   for vertex, lit in zip(exterior, column)]
    with Cadical195(bootstrap_with=formula.clauses) as solver:
        assert solver.solve(assumptions=assumptions)
    return len(formula.clauses)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalogue', type=Path)
    parser.add_argument('--controls', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--root', type=int, default=6)
    parser.add_argument('--alpha', type=int, default=9)
    parser.add_argument('--min-degree', type=int, default=6)
    parser.add_argument('--edges', type=int, default=166)
    parser.add_argument('--any-edges', action='store_true')
    parser.add_argument('--relaxed', action='store_true')
    args = parser.parse_args()
    if args.controls:
        complement = graph.parse_matrix(args.controls.read_text().splitlines())
        exoo = [nbrs ^ ((1 << 39) - 1) ^ (1 << vertex) for vertex, nbrs in enumerate(complement)]
        c35 = [sum(1 << ((vertex + step) % 35) for step in (1, -1, 7, -7, 11, -11, 16, -16))
               for vertex in range(35)]
        for label, adj, independence, root in (('C35', c35, 8, 0), ('Exoo saturated', saturated(exoo), 9,
                                                min(range(39), key=lambda vertex: exoo[vertex].bit_count()))):
            assert graph.triangle_free(adj) and graph.alpha(adj) == independence
            clauses = control(adj, root, independence, not args.relaxed)
            print(f'{label}: root degree {adj[root].bit_count()}, {clauses} clauses; actual completion SAT')
        order22 = Path(__file__).resolve().parents[3] / 'gluing/val/r3_7_22.g6'
        tested = 0
        for row in order22.read_text().splitlines():
            adj = graph.parse_graph6(row)
            if all(degree.bit_count() == 6 for degree in adj):
                for root in range(22):
                    control(adj, root, 6, not args.relaxed)
                    tested += 1
        assert tested == 220
        print(f'(3,7,22): all {tested} rooted 6-regular completions SAT with actual witnesses')
    if args.catalogue:
        assert args.out is not None
        for index, line in enumerate(args.catalogue.read_text().splitlines(), 1):
            adj = graph.parse_graph6(line)
            formula, _ = encode(adj, args.root, args.alpha, args.min_degree,
                                None if args.any_edges else args.edges, not args.relaxed)
            formula.write(args.out / f'{index:04d}.cnf')
            print(f'{index}: {len(adj)} vertices, {sum(map(int.bit_count, adj)) // 2} edges; '
                  f'{formula.last} variables, {len(formula.clauses)} clauses', flush=True)


if __name__ == '__main__':
    main()
