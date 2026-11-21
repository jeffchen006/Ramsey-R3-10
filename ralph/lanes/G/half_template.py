#!/usr/bin/env python3
"""Bounded solver for marked e120 halves; no claimed full e120 census."""

from argparse import ArgumentParser
from itertools import combinations
from pathlib import Path
from time import process_time

from equality_template import Problem, graph
from root_glue import independent
from signature_rows import lower_edges


def shape(width, private, missing, edge_count, minimum, maximum):
    pairs = tuple(pair for pair in combinations(range(width), 2) if pair not in missing)
    problem = Problem(width, private, pairs)
    problem.structure(False)
    problem.local_edges(edge_count + width, prove_total=True)
    for vertex in range(1, problem.order):
        problem.bound((problem.edgeof(vertex, other) for other in range(1, problem.order) if other != vertex), minimum, maximum)
    for length in range(1, width + 1):
        for subset in combinations(range(width), length):
            mask = sum(1 << index for index in subset)
            vertices = [vertex for vertex in range(problem.first, problem.order) if not problem.supports[vertex] & ~mask]
            full = lower_edges(length + private, length + len(vertices))
            if full is None:
                problem.add(())
            else:
                problem.bound((problem.edgeof(left, right) for left, right in combinations(vertices, 2)),
                              full - sum(problem.supports[vertex].bit_count() for vertex in vertices),
                              len(vertices) * (len(vertices) - 1) // 2)
    return problem


def seed_alpha(problem, split):
    fixed = [sum(1 << other for other in range(problem.order) if vertex != other and problem.edgeof(vertex, other) == 1)
             for vertex in range(problem.order)]
    for count in range(0 if split == problem.anchors else problem.anchors - split, problem.anchors + 1):
        for anchors in combinations(range(1, problem.first), count):
            # The full alpha test is lazy; these are the windows using many mark vertices.
            if not anchors and split == problem.anchors:
                continue
            universe = ((1 << problem.order) - 1) & ~((1 << problem.first) - 1)
            for anchor in anchors:
                universe &= ~fixed[anchor]
            target = problem.alpha + 1 - count
            for witness in independent(fixed, universe, target, target):
                problem.add(problem.edge[pair] for pair in combinations(witness, 2))


def control():
    problem = shape(3, 1, ((0, 1),), 10, 1, 4)
    result, stats = problem.solve(611, 500, 5000, 64, omit_root=True)
    assert result == 'FULL_SAT', (result, stats)
    print('marked C13 n8 half SAT at 10 edges')
    problem = shape(3, 1, ((0, 1),), 5, 1, 4)
    result, stats = problem.solve(611, 500, 5000, 64, omit_root=True)
    assert result == 'UNSAT', (result, stats)
    print('marked C13 n8 half UNSAT at 5 edges')


def encode_graph(adj):
    order = len(adj)
    bits = [adj[right] >> left & 1 for right in range(order) for left in range(right)]
    bits.extend([0] * (-len(bits) % 6))
    return chr(63 + order) + ''.join(chr(63 + sum(bit << (5 - offset) for offset, bit in enumerate(bits[index:index + 6])))
                                    for index in range(0, len(bits), 6))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--shape', choices=('path', 'matching'))
    parser.add_argument('--conflicts', type=int, default=50000)
    parser.add_argument('--batch', type=int, default=128)
    parser.add_argument('--local', type=int, default=3)
    parser.add_argument('--seed', type=int, default=611)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--cross-role', choices=('center', 'leaf', 'matched'))
    args = parser.parse_args()
    if args.control:
        control()
        return
    start = process_time()
    missing = ((0, 1), (0, 2)) if args.shape == 'path' else ((0, 1), (2, 3))
    problem = shape(5, 4, missing, 120, 6, 8)
    assert problem.order == 34 and problem.alpha == 8
    if args.cross_role is not None:
        assert (args.cross_role == 'matched') == (args.shape == 'matching')
        cross_anchor = 2 if args.cross_role == 'leaf' else 1
        for anchor in range(1, problem.first):
            if anchor == cross_anchor:
                continue
            inside = [vertex for vertex in range(problem.first, problem.order) if problem.edgeof(anchor, vertex) == 1]
            for vertex in range(problem.first, problem.order):
                if vertex not in inside:
                    problem.add(problem.edgeof(vertex, other) for other in inside)
    seed_alpha(problem, args.local)
    print('built', problem.formula.last, len(problem.formula.clauses), f'cpu={process_time()-start:.3f}', flush=True)
    result, stats = problem.solve(args.seed, 10000, args.conflicts, args.batch, omit_root=True)
    print(result, stats, f'cpu={process_time()-start:.3f}', flush=True)
    if result == 'FULL_SAT':
        adj = [neighbours >> 1 for neighbours in problem.solution[1:]]
        assert len(adj) == 33 and graph.alpha(adj) == 8 and graph.triangle_free(adj)
        assert sum(map(int.bit_count, adj)) == 240
        if args.output:
            args.output.write_text(encode_graph(adj) + '\n')
        print(encode_graph(adj))


if __name__ == '__main__':
    main()
