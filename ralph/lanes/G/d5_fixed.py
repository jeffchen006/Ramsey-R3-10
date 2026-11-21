#!/usr/bin/env python3
"""Exact fixed-core neighbourhood gluing, without any MTF assumption."""

from argparse import ArgumentParser
from itertools import combinations
from pathlib import Path

from check_root_cover import graph, induced, vertices
from root_glue import Formula, independent


def encode(adj, alpha, degree, minimum, maximum_edges):
    assert graph.triangle_free(adj) and graph.alpha(adj) < alpha
    order = len(adj)
    columns = [list(range(1 + order * index, 1 + order * (index + 1)))
               for index in range(degree)]
    instance = Formula(order * degree)
    for column in columns:
        for vertex, neighbours in enumerate(adj):
            for other in vertices(neighbours):
                if vertex < other:
                    instance.add((-column[vertex], -column[other]))
        instance.bound(column, minimum - 1, alpha - 1)
    for vertex, neighbours in enumerate(adj):
        degree_in_core = neighbours.bit_count()
        instance.bound([column[vertex] for column in columns],
                       max(0, minimum - degree_in_core), alpha - degree_in_core)
    instance.bound(sum(columns, []), 0, maximum_edges - degree - sum(map(int.bit_count, adj)) // 2)

    for number in range(2, degree + 1):
        size = alpha + 1 - number
        pieces = list(combinations(columns, number))
        for indep in independent(adj, (1 << order) - 1, size, size):
            for subset in pieces:
                instance.add(column[vertex] for column in subset for vertex in indep)
    for first, second in zip(columns, columns[1:]):
        prefix = []
        for left, right in zip(first, second):
            instance.add((*prefix, -left, right))
            equal = instance.new()
            instance.add((-left, -right, equal))
            instance.add((left, right, equal))
            instance.add((-left, right, -equal))
            instance.add((left, -right, -equal))
            prefix.append(-equal)
    return instance


def control(inputs):
    from pysat.solvers import Cadical195

    seen = set()
    for line in inputs.read_text().splitlines():
        adj = graph.parse_graph6(line)
        count = sum(map(int.bit_count, adj)) // 2
        for root, neighbours in enumerate(adj):
            if neighbours.bit_count() != 5:
                continue
            mask = ((1 << len(adj)) - 1) & ~(1 << root | neighbours)
            exterior = tuple(vertices(mask))
            columns = sorted(tuple(bool(adj[vertex] & (1 << other)) for other in exterior)
                             for vertex in vertices(neighbours))
            residual = induced(adj, mask)
            seen.add((len(adj), root))
            cnf = encode(residual, 6, 5, 5, count)
            assignment = [number if entry else -number for number, entry in
                          enumerate(sum((list(column) for column in columns), []), 1)]
            with Cadical195(bootstrap_with=cnf.clauses) as solver:
                assert solver.solve(assumptions=assignment)
    assert len(seen) >= 5
    print(f'{len(seen)} distinct control root positions retain SAT with all actual edges fixed')


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('inputs', type=Path)
    parser.add_argument('output', type=Path, nargs='?')
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--edges', type=int, default=121)
    args = parser.parse_args()
    if args.control:
        control(args.inputs)
        return
    args.output.mkdir(exist_ok=True, parents=True)
    for number, line in enumerate(args.inputs.read_text().splitlines(), 1):
        adj = graph.parse_graph6(line)
        assert len(adj) == 27
        identifier = args.output / f'{number:04d}'
        encode(adj, 8, 5, 5, args.edges).write(identifier.with_suffix('.cnf'))
        identifier.with_suffix('.g6').write_text(line + '\n')


if __name__ == '__main__':
    main()
