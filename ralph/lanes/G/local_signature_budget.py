#!/usr/bin/env python3
"""Small induced anchor-window edge bounds without MTF constraints."""

from argparse import ArgumentParser
from itertools import combinations
from pathlib import Path

from pysat.solvers import Cadical195

from equality_template import Problem, graph
from half_template import encode_graph
from root_glue import independent


def instance(anchors, private, signatures, maximum):
    problem = Problem(anchors, private, signatures)
    problem.structure(False)
    fixed = [sum(1 << other for other in range(problem.order) if vertex != other and problem.edgeof(vertex, other) == 1)
             for vertex in range(problem.order)]
    possible = ((1 << problem.order) - 1) ^ 1
    for witness in independent(fixed, possible, problem.alpha + 1, problem.alpha + 1):
        problem.add(problem.edge[pair] for pair in combinations(witness, 2))
    problem.bound((edge for (left, _), edge in problem.edge.items() if left >= problem.first), 0, maximum)
    return problem


def solve(problem, output):
    with Cadical195(bootstrap_with=problem.formula.clauses) as solver:
        solver.conf_budget(500000)
        result = solver.solve_limited()
        if result:
            adj = [neighbours >> 1 for neighbours in problem.adjacency(solver.get_model())[1:]]
            assert graph.alpha(adj) <= problem.alpha and graph.triangle_free(adj)
            if output is not None:
                output.write_text(encode_graph(adj) + '\n')
        return result, solver.accum_stats()['conflicts']


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--pairs', type=int, choices=range(4))
    parser.add_argument('--cap', type=int)
    parser.add_argument('--cnf', type=Path)
    parser.add_argument('--graph', type=Path)
    args = parser.parse_args()
    if args.control:
        signatures = ((0, 1), (0, 3), (1, 2), (2, 3))
        assert solve(instance(4, 1, signatures, 10), None)[0] is True
        assert solve(instance(4, 1, signatures, 7), None)[0] is False
        print('C13 minus root: e(H)<=10 SAT; e(H)<=7 UNSAT')
        return
    problem = instance(3, 4, tuple(combinations(range(3), 2))[:args.pairs], args.cap)
    if args.cnf:
        problem.formula.write(args.cnf)
    print(args.pairs, args.cap, problem.formula.last, len(problem.formula.clauses), solve(problem, args.graph), flush=True)


if __name__ == '__main__':
    main()
