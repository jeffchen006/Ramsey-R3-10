#!/usr/bin/env python3
"""Bounded pilot on the exact mixed path/leaf and noncross-d8 window."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations, islice, product
from pathlib import Path
from time import process_time

from canon_strip import validate
from check_root_cover import graph, vertices
from mixed_strip_cover import choices
from root_glue import independent
from strip_completion import Completion, solve


def instance(line, path_mask, mixed_mask, case, hole_left, hole_right, hole_peer, eager):
    adj = graph.parse_graph6(line)
    assert len(adj) == 27
    survived = validate(adj, min(path_mask, mixed_mask), max(path_mask, mixed_mask))
    roots = (27, 28)
    pivots = (29, 30)
    active = tuple(tuple(vertices(mask)) for mask in (path_mask, mixed_mask))
    stars, = [(left, right) for left, right in product(*active) if adj[left] >> right & 1]
    sides = tuple((*anchors, pivot) for anchors, pivot in zip(active, pivots, strict=True))
    common = tuple(range(31, 35))
    exclusive = ((35, 36), (37, 38, 39))
    deleted_x = (*common, *exclusive[0], *exclusive[1])
    exterior = (*survived, *deleted_x)
    hole = (hole_left, hole_right)
    occupied = {tuple(vertices(adj[vertex] & mixed_mask)) for vertex in survived
                if (adj[vertex] & mixed_mask).bit_count() == 2}
    assert (case, *hole, hole_peer) in set(choices(active[1], stars[1], occupied))
    fixed = {(left, right): bool(adj[left] >> right & 1) for left, right in combinations(range(27), 2)}
    for index, (root, pivot, side) in enumerate(zip(roots, pivots, sides, strict=True)):
        for other in range(40):
            if other != root:
                fixed[tuple(sorted((root, other)))] = other in roots or other in side
            if other != pivot and other not in roots:
                fixed[tuple(sorted((pivot, other)))] = other in common or other in exclusive[index]
        wanted = Counter({(anchor,): 4 for anchor in active[index]})
        wanted.update(pair for pair in combinations(active[index], 2) if index == 0 or pair != hole)
        seen = Counter(tuple(anchor for anchor in active[index] if adj[vertex] >> anchor & 1) for vertex in survived)
        assert all(count <= wanted[part] for part, count in seen.items())
        for vertex, part in zip(exclusive[1-index], sorted((wanted-seen).elements()), strict=True):
            for anchor in active[index]:
                fixed[anchor, vertex] = anchor in part
    for left, right in combinations(deleted_x, 2):
        if left not in exclusive[0] or right not in exclusive[1]:
            fixed[left, right] = False
    present = [0] * 40
    for (left, right), value in fixed.items():
        if value:
            present[left] |= 1 << right
            present[right] |= 1 << left
    for left, right in combinations(range(40), 2):
        if present[left] & present[right] and (left, right) not in fixed:
            fixed[left, right] = False

    problem = Completion(40, fixed)
    problem.triangles()
    problem.maximal()
    doubles_by_vertex = {vertex: [] for vertex in exterior}
    for index, side in enumerate(sides):
        supports = {vertex: {anchor: problem.edgeof(vertex, anchor) for anchor in side} for vertex in exterior}
        for incident in supports.values():
            problem.bound(incident.values(), 1, 2)
        for anchor in side:
            singles = [problem.and_all(lit if other == anchor else -lit for other, lit in incident.items())
                       for incident in supports.values()]
            problem.bound(singles, 4, 4)
        path_options = []
        for left, right in combinations(side, 2):
            doubles = [problem.and2(incident[left], incident[right]) for incident in supports.values()]
            for vertex, literal in zip(supports, doubles, strict=True):
                doubles_by_vertex[vertex].append(literal)
            if index:
                count = int((left, right) not in (hole, (hole_peer, pivots[1])))
                problem.bound(doubles, count, count)
            elif right == pivots[0] and left != stars[0]:
                problem.bound(doubles, 0, 1)
                path_options.extend(doubles)
            else:
                count = int(right != pivots[0])
                problem.bound(doubles, count, count)
        if not index:
            problem.bound(path_options, 2, 2)
    low_degrees = []
    for vertex in exterior:
        selector = problem.exact_degree(vertex, (7, 9))[7]
        for double in doubles_by_vertex[vertex]:
            problem.add((-selector, -double))
        low_degrees.append(selector)
    problem.bound(low_degrees, 6, 6)
    if eager:
        for count in (7, 6):
            for chosen in islice(independent(adj, (1 << len(adj)) - 1, count, count), eager):
                for index, vertices_in_side in enumerate(exclusive):
                    for selected in combinations(vertices_in_side, 9-count):
                        problem.add(problem.independent_clause((*chosen, *selected, pivots[1-index])))
    return problem


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('keys', type=Path)
    parser.add_argument('--conflicts', type=int, default=20000)
    parser.add_argument('--eager', type=int, default=10000)
    args = parser.parse_args()
    start = process_time()
    for row in args.keys.read_text().splitlines():
        row_id, first, second, case, hole_left, hole_right, hole_peer, line = row.split()
        problem = instance(line, int(first), int(second), case, int(hole_left), int(hole_right), int(hole_peer), args.eager)
        outcome, statistics, cuts = solve(problem, 9, args.conflicts)
        print(row_id, first, second, case, hole_left, hole_right, hole_peer, outcome,
              statistics['conflicts'], statistics['models'], len(cuts), f'{process_time()-start:.5f}', flush=True)


if __name__ == '__main__':
    main()
