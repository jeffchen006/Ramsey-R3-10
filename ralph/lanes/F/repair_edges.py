#!/usr/bin/env python3
"""Release triangle edges, then seek a Ramsey graph containing the fixed backbone."""

import argparse
from itertools import combinations
from pathlib import Path
from random import Random

from pysat.solvers import Cadical195
from orbit_extend import independent_sets, parse_graph6, to_graph6, vertices
from repair2 import triangles


def complete(backbone, forbidden):
    order = len(backbone)
    all_vertices = (1 << order) - 1
    if any(mask.bit_count() >= forbidden for mask in backbone):
        return None, 0
    possible = backbone.copy()
    variables = {}
    for left, right in combinations(range(order), 2):
        if not (backbone[left] >> right & 1) and not (backbone[left] & backbone[right]):
            variables[left, right] = len(variables) + 1
            possible[left] |= 1 << right
            possible[right] |= 1 << left
    clauses = set()
    for triangle in triangles(possible):
        clauses.add(tuple(-variables[pair] for pair in combinations(vertices(triangle), 2) if pair in variables))
    for bad in independent_sets(backbone, all_vertices, forbidden):
        options = tuple(variables[pair] for pair in combinations(vertices(bad), 2) if pair in variables)
        if not options:
            return None, len(variables)
        clauses.add(options)
    with Cadical195(bootstrap_with=list(clauses)) as solver:
        if not solver.solve():
            return None, len(variables)
        model = {literal for literal in solver.get_model() if literal > 0}
    for (left, right), variable in variables.items():
        if variable in model:
            backbone[left] |= 1 << right
            backbone[right] |= 1 << left
    if (next(triangles(backbone), None) is not None or
            next(independent_sets(backbone, all_vertices, forbidden), None) is not None):
        raise RuntimeError('invalid repair')
    return backbone, len(variables)


def main():
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument('--k', type=int, default=10)
    arg.add_argument('--release', type=int, nargs='+', default=[0, 3, 8])
    arg.add_argument('--reps', type=int, default=10)
    arg.add_argument('--seed', type=int, default=1121)
    arg.add_argument('--out', type=Path, required=True)
    arg.add_argument('paths', type=Path, nargs='+')
    args = arg.parse_args()
    random = Random(args.seed)
    for path in args.paths:
        graph = parse_graph6(path.read_text().strip())
        triangle_edges = {pair for triangle in triangles(graph) for pair in combinations(vertices(triangle), 2)}
        other_edges = [(left, right) for left, right in combinations(range(len(graph)), 2)
                       if graph[left] >> right & 1 and (left, right) not in triangle_edges]
        for budget in args.release:
            for trial in range(args.reps if budget else 1):
                backbone = graph.copy()
                for left, right in list(triangle_edges) + random.sample(other_edges, budget):
                    backbone[left] &= ~(1 << right)
                    backbone[right] &= ~(1 << left)
                model, var_count = complete(backbone, args.k)
                print(f'{path} released={len(triangle_edges) + budget} iteration={trial} '
                      f'vars={var_count} model={bool(model)}', flush=True)
                if model:
                    with args.out.open('a') as stream:
                        stream.write(to_graph6(model) + '\n')
                    break
            else:
                continue
            break


if __name__ == '__main__':
    main()
