#!/usr/bin/env python3
"""One degree-two noncross anchor: complete the window and strips together."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations, product
from pathlib import Path
from time import process_time

from check_root_cover import graph, vertices
from mixed_full_cover import choices as full_choices
from mixed_strip_cover import choices
from root_glue import independent
from strip_completion import Completion, solve


def part(neighbors, side):
    return tuple(anchor for anchor in side if neighbors >> anchor & 1)


def pin_window(adj, small, large):
    core = len(adj)
    restored = core
    extra = (core + 1, core + 2)
    anchors = ((*small, restored), large)
    exterior = tuple(vertex for vertex in range(core) if vertex not in (*small, *large))
    fixed = {(left, right): bool(adj[left] >> right & 1) for left, right in combinations(range(core), 2)}
    fixed.update({(left, restored): False for left in range(core)})
    fixed.update({(restored, right): True for right in extra})
    fixed[extra] = False
    return fixed, anchors, exterior, extra


def preclude_triangles(fixed, order):
    present = [0] * order
    for (left, right), value in fixed.items():
        if value:
            present[left] |= 1 << right
            present[right] |= 1 << left
    for left, right in combinations(range(order), 2):
        if present[left] & present[right]:
            assert not fixed.get((left, right), False)
            fixed[left, right] = False


def support_constraints(problem, outside, side, singles, exact=False):
    support = {vertex: {anchor: problem.edgeof(vertex, anchor) for anchor in side} for vertex in outside}
    for incident in support.values():
        problem.bound(incident.values(), 1, 2)
    doubled = {vertex: [] for vertex in outside}
    for signature, (lower, upper) in singles.items():
        if len(signature) == 1:
            anchor, = signature
            literals = [problem.and_all(lit if other == anchor else -lit for other, lit in row.items())
                        for row in support.values()]
        else:
            left, right = signature
            literals = [problem.and2(row[left], row[right]) for row in support.values()]
            for vertex, literal in zip(outside, literals, strict=True):
                doubled[vertex].append(literal)
        problem.bound(literals, lower if exact else 0, upper)
    return doubled


def independent_core(adj, size):
    return tuple(independent(adj, (1 << len(adj)) - 1, size, size))


def window_cuts(problem, extra, core_sets):
    for chosen in core_sets:
        problem.add(problem.independent_clause((*chosen, *extra)))


def neighborhood_cuts(problem, core_sets, core_size, centers, alpha):
    neighborhoods = []
    for center in centers:
        shell = tuple(vertex for vertex in range(core_size, problem.order)
                      if vertex != center and problem.edgeof(center, vertex) == 1)
        neighborhoods.append(shell)
    for chosen, shell in product(core_sets, sorted(set(neighborhoods))):
        lower = len(shell) + len(chosen) - alpha
        if lower > 0:
            covered = [-problem.and_all(-problem.edgeof(anchor, vertex) for anchor in chosen) for vertex in shell]
            problem.bound(covered, lower, len(shell))


def weak_window(adj, small, large, singles, alpha):
    fixed, anchors, outside, extra = pin_window(adj, small, large)
    order = len(adj) + 3
    preclude_triangles(fixed, order)
    problem = Completion(order, fixed)
    problem.triangles()
    for side in anchors:
        bounds = {(anchor,): (0, singles) for anchor in side}
        bounds.update({pair: (0, 1) for pair in combinations(side, 2)})
        support_constraints(problem, (*outside, *extra), side, bounds)
    assert graph.alpha(adj) < alpha
    window_cuts(problem, extra, independent_core(adj, alpha - 1))
    return problem, extra


def sort_contacts(problem, labels, contacts):
    for earlier, later in zip(labels, labels[1:]):
        prefix = 1
        for contact in contacts:
            left = problem.edgeof(earlier, contact)
            right = problem.edgeof(later, contact)
            if left == right:
                continue
            problem.add((-prefix, -left, right))
            equal = problem.and2(-problem.and2(left, -right), -problem.and2(-left, right))
            prefix = problem.and2(prefix, equal)


def roles(adj, small, large, degree):
    _, anchors, outside, _ = pin_window(adj, small, large)
    for orientation in range(2):
        path, mixed = anchors[orientation], anchors[1 - orientation]
        path_star, mixed_star = next((left, right) for left, right in product(path, mixed) if
                                     left < len(adj) and right < len(adj) and adj[left] >> right & 1)
        seen = Counter(part(adj[vertex], mixed) for vertex in outside)
        occupied = {signature for signature in seen if len(signature) == 2}
        for shape, first, second, peer, *other in (choices if degree == 8 else full_choices)(
                mixed, mixed_star, occupied):
            hole = (first, second)
            peer_hole = (peer, *other) if other else (peer, 27)
            yield orientation, path, mixed, path_star, mixed_star, shape, hole, peer_hole


def attach_template(problem, sides, pivots, outside, path_star, holes):
    profiles = {}
    for index, side in enumerate(sides):
        pivot = pivots[index]
        bounds = {(anchor,): (4, 4) for anchor in side}
        for pair in combinations(side, 2):
            if index:
                count = int(pair not in holes)
                bounds[pair] = (count, count)
            elif pivot not in pair:
                bounds[pair] = (1, 1)
            elif path_star in pair:
                bounds[pair] = (0, 0)
            else:
                bounds[pair] = (0, 1)
        profiles[index] = support_constraints(problem, outside, side, bounds, exact=True)
    return profiles


def fixed_shell(adj, small, large, degree, role):
    fixed, _, old_exterior, extra = pin_window(adj, small, large)
    orientation, path, mixed, path_star, _, _, hole, peer_hole = role
    core = len(adj)
    order = core + 3
    assert order == 24 and degree in (8, 9)
    roots = (order, order + 1)
    pivots = (order + 2, order + 3)
    shared = degree - 7
    sides = tuple((*anchors, pivot) for anchors, pivot in zip((path, mixed), pivots, strict=True))
    common = tuple(range(order + 4, order + 4 + shared))
    start = order + 4 + shared
    exclusive = (tuple(range(start, start + 6 - shared)), tuple(range(start + 6 - shared, 40)))
    assert len(exclusive[1]) == 6
    deleted = (*common, *exclusive[0], *exclusive[1])
    for index, (root, pivot, side) in enumerate(zip(roots, pivots, sides, strict=True)):
        for other in range(40):
            if other != root:
                fixed[tuple(sorted((root, other)))] = other in roots or other in side
            if other != pivot and other not in roots:
                fixed[tuple(sorted((pivot, other)))] = other in common or other in exclusive[index]
        restored_side = orientation == index
        if restored_side:
            wanted = Counter({(anchor,): 4 for anchor in side if anchor < core})
            wanted.update(pair for pair in combinations((anchor for anchor in side if anchor < core), 2)
                          if index == 0 or pair not in (hole, peer_hole))
            seen = Counter(part(adj[vertex], side) for vertex in old_exterior)
            assert all(0 < count <= wanted[signature] for signature, count in seen.items())
            remaining = list((wanted - seen).elements())
            assert len(remaining) <= 1
            for number, vertex in enumerate(exclusive[1 - index]):
                fixed[core, vertex] = number >= len(remaining)
            if remaining:
                for anchor in side:
                    fixed[anchor, exclusive[1 - index][0]] = anchor in remaining[0]
    for left, right in combinations(deleted, 2):
        if left not in exclusive[0] or right not in exclusive[1]:
            fixed[left, right] = False
    return fixed, path, mixed, path_star, sides, pivots, exclusive, old_exterior, extra, deleted


def instance(adj, small, large, degree, role, core_sets, *, eager=False, neighborhood=False, sorted_slots=False):
    (fixed, path, mixed, path_star, sides, pivots, exclusive, old_exterior, extra, deleted) = fixed_shell(
        adj, small, large, degree, role)
    hole, peer_hole = role[-2:]
    outside = (*old_exterior, *extra, *deleted)
    preclude_triangles(fixed, 40)
    problem = Completion(40, fixed)
    problem.triangles()
    problem.maximal()
    if sorted_slots:
        for index, (active, group) in enumerate(zip((path, mixed), reversed(exclusive), strict=True)):
            already_pinned = (role[0] == index and not fixed[21, group[0]])
            sort_contacts(problem, group[int(already_pinned):], active)
        sort_contacts(problem, extra, tuple(range(21)))
    profiles = attach_template(problem, sides, pivots, outside, path_star, (hole, peer_hole))
    degree_seven = []
    for vertex in outside:
        selector = problem.exact_degree(vertex, (7, 9))[7]
        degree_seven.append(selector)
        for side in profiles.values():
            for doubled in side[vertex]:
                problem.add((-selector, -doubled))
    problem.bound(degree_seven, 6, 6)
    window_cuts(problem, extra, core_sets)
    if neighborhood:
        for vertex in range(24):
            problem.bound((problem.edgeof(vertex, other) for other in range(24) if vertex != other), 2, 7)
        neighborhood_cuts(problem, core_sets, 21, (21, 24, 25, *pivots), 9)
    if eager:
        for chosen in core_sets:
            for index, group in enumerate(exclusive):
                for trio in combinations(group, 3):
                    problem.add(problem.independent_clause((*chosen, *trio, pivots[1 - index])))
    return problem


def select_rows(source, start, stop, count):
    rows = source.read_text().splitlines()[start:stop]
    if count:
        assert 0 < count <= len(rows)
        rows = [rows[index * len(rows) // count] for index in range(count)]
    return rows


def unpack(row):
    row_id, first, second, encoded = row.split()
    return row_id, graph.parse_graph6(encoded), tuple(vertices(int(first))), tuple(vertices(int(second)))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--stop', type=int)
    parser.add_argument('--count', type=int)
    parser.add_argument('--degree', type=int, choices=(8, 9), required=True)
    parser.add_argument('--conflicts', type=int, default=2000)
    parser.add_argument('--eager', action='store_true')
    parser.add_argument('--neighborhood', action='store_true')
    parser.add_argument('--sorted-slots', action='store_true')
    parser.add_argument('--count-only', action='store_true')
    args = parser.parse_args()
    start = process_time()
    for row in select_rows(args.source, args.start, args.stop, args.count):
        row_id, adj, small, large = unpack(row)
        if args.count_only:
            role_count = Counter((role[0], role[-3]) for role in roles(adj, small, large, args.degree))
            print(row_id, *row.split()[1:3], sum(role_count.values()), sorted(role_count.items()), flush=True)
            continue
        core_sets = independent_core(adj, 6)
        for role in roles(adj, small, large, args.degree):
            begin = process_time()
            problem = instance(adj, small, large, args.degree, role, core_sets, eager=args.eager,
                               neighborhood=args.neighborhood, sorted_slots=args.sorted_slots)
            built = process_time()
            status, stats, cuts = solve(problem, 9, args.conflicts)
            print(row_id, *row.split()[1:3], args.degree, role[0], *role[-3:],
                  status, stats['conflicts'], stats['models'], len(cuts), len(problem.formula.clauses),
                  f'{built-begin:.5f}', f'{process_time()-built:.5f}', f'{process_time()-start:.5f}', flush=True)


if __name__ == '__main__':
    main()
