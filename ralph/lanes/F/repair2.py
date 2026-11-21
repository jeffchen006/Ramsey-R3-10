#!/usr/bin/env python3
"""Choose a small vertex transversal of all bad sets and repair it by SAT."""

import argparse
from itertools import combinations
from pathlib import Path
from random import Random
from pysat.solvers import Cadical195
from orbit_extend import independent, independent_sets, parse_graph6, to_graph6, vertices


def residual(graph, dropped):
    keep = [index for index in range(len(graph)) if not (dropped >> index & 1)]
    return [sum(1 << position for position, right in enumerate(keep) if graph[left] >> right & 1)
            for left in keep]


def triangles(graph):
    for right, neighbors in enumerate(graph):
        for middle in vertices(neighbors & ((1 << right) - 1)):
            for left in vertices(neighbors & graph[middle] & ((1 << middle) - 1)):
                yield (1 << left) | (1 << middle) | (1 << right)


def extend_holes(base, forbidden, holes):
    size = len(base)
    new_edges = {pair: holes * size + index for index, pair in enumerate(combinations(range(holes), 2), 1)}
    degrees = [mask.bit_count() for mask in base]
    if any(degree >= forbidden for degree in degrees):
        return None
    clauses = []
    for offsets in combinations(range(holes), 3):
        clauses.append([-new_edges[pair] for pair in combinations(offsets, 2)])
    for left, neighbors in enumerate(base):
        incident = [offset * size + left + 1 for offset in range(holes)]
        for right in vertices(neighbors & ((1 << left) - 1)):
            for offset, variable in enumerate(incident):
                clauses.append([-variable, -offset * size - right - 1])
        for (first, second), variable in new_edges.items():
            clauses.append([-variable, -incident[first], -incident[second]])
        for forbidden_incidence in combinations(incident, forbidden - degrees[left]):
            clauses.append([-variable for variable in forbidden_incidence])
    movable = sum(1 << pos for pos, degree in enumerate(degrees) if degree < forbidden - 1)
    all_base = (1 << size) - 1
    for count in range(1, holes + 1):
        uncovered = set(mask & movable for mask in independent_sets(base, all_base, forbidden - count))
        if count == 1 and 0 in uncovered:
            return None
        for offsets in combinations(range(holes), count):
            inner = [new_edges[pair] for pair in combinations(offsets, 2)]
            for mask in uncovered:
                clauses.append(inner + [offset * size + pos + 1 for offset in offsets for pos in vertices(mask)])
    with Cadical195(bootstrap_with=clauses) as solver:
        if not solver.solve():
            return None
        model = {literal for literal in solver.get_model() if literal > 0}
    output = base + [0] * holes
    for offset in range(holes):
        for pos in range(size):
            if size * offset + pos + 1 in model:
                output[pos] |= 1 << (size + offset)
                output[size + offset] |= 1 << pos
    for (first, second), variable in new_edges.items():
        if variable in model:
            output[size + first] |= 1 << (size + second)
            output[size + second] |= 1 << (size + first)
    if (any(not independent(mask, output) for mask in output) or
            next(independent_sets(output, (1 << len(output)) - 1, forbidden), None) is not None):
        raise RuntimeError('bad repaired graph')
    return output


def main():
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument('--k', type=int, default=10)
    arg.add_argument('--holes', type=int, choices=(2, 3, 4), default=2)
    arg.add_argument('--max-pairs', type=int, default=80, help='maximum repairs per input')
    arg.add_argument('--shuffle', type=int, help='randomize candidate order with this seed')
    arg.add_argument('--need-bad', action='store_true')
    arg.add_argument('--out', type=Path, required=True)
    arg.add_argument('paths', type=Path, nargs='+')
    args = arg.parse_args()
    known = set()
    for path in args.paths:
        graph6 = path.read_text().strip()
        if graph6 in known:
            continue
        known.add(graph6)
        graph = parse_graph6(graph6)
        bad_sets = list(independent_sets(graph, (1 << len(graph)) - 1, args.k))
        bad_triangles = list(triangles(graph))
        if args.need_bad and not (bad_sets or bad_triangles):
            print(f'{path} skipped: already valid', flush=True)
            continue
        subsets = (sum(1 << index for index in subset) for subset in combinations(range(len(graph)), args.holes))
        covers = [candidate for candidate in subsets if all(mask & candidate for mask in bad_sets + bad_triangles)]
        if args.shuffle is not None:
            Random(args.shuffle).shuffle(covers)
        print(f'{path} bad={len(bad_sets)} triangles={len(bad_triangles)} transversals={len(covers)}', flush=True)
        for count, cover in enumerate(covers[:args.max_pairs], 1):
            result = extend_holes(residual(graph, cover), args.k, args.holes)
            if result is None:
                continue
            with args.out.open('a') as stream:
                stream.write(to_graph6(result) + '\n')
            print(f'{path} repaired using {list(vertices(cover))} after {count} tests', flush=True)
            break
        else:
            print(f'{path} no repair in {min(len(covers), args.max_pairs)} tests', flush=True)


if __name__ == '__main__':
    main()
