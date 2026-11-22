#!/usr/bin/env python3
"""Literal two-neighbour graph addback, matched against the SAT projection."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations, product
from pathlib import Path
from time import process_time

from pysat.solvers import Cadical195

from check_root_cover import graph, vertices
from pinned_anchor_window import independent_core, neighborhood_cuts, select_rows, sort_contacts, unpack, weak_window
from strip_completion import Completion


def union_masks(parts):
    return sum(1 << vertex for vertex in parts)


def expanded(adj, contacts):
    restored = len(adj)
    added = (restored + 1, restored + 2)
    return [neighbors | sum(1 << vertex for vertex, hits in zip(added, contacts) if hits >> index & 1)
            for index, neighbors in enumerate(adj)] + [union_masks(added),
                                                        *((1 << restored) | mask for mask in contacts)]


def literal_options(adj, small, large, singles, alpha):
    old = len(adj)
    restored = 1 << old
    small_mask, large_mask = union_masks(small), union_masks(large)
    outside_mask = ((1 << old) - 1) ^ small_mask ^ large_mask
    sides = (small_mask | restored, large_mask)
    seen = [Counter(adj[vertex] & side for vertex in vertices(outside_mask)) for side in sides]
    one_support = [[restored, *(restored | (1 << anchor) for anchor in small)],
                   [union_masks(anchors) for width in (1, 2) for anchors in combinations(large, width)]]

    def compatible_sets(candidates, taken=0):
        yield taken
        while candidates:
            bit = candidates & -candidates
            candidates ^= bit
            yield from compatible_sets(candidates & ~adj[bit.bit_length() - 1], taken | bit)

    required_sets = independent_core(adj, alpha - 1)
    hit = [0] * old
    for index, chosen in enumerate(required_sets):
        for vertex in chosen:
            hit[vertex] |= 1 << index
    everything = (1 << len(required_sets)) - 1
    candidates = []
    for support in product(*one_support):
        room = tuple((singles if mask.bit_count() == 1 else 1) - count[mask]
                     for mask, count in zip(support, seen))
        if min(room) < 1:
            continue
        together = (support[0] | support[1]) ^ restored
        forbid = 0
        for vertex in vertices(together):
            forbid |= adj[vertex]
        if forbid & together:
            continue
        group = []
        for adjacencies in compatible_sets(outside_mask & ~forbid, together):
            covers = 0
            for vertex in vertices(adjacencies):
                covers |= hit[vertex]
            group.append((adjacencies, covers))
        candidates.append((support, room, group))
    for index, (support, room, group) in enumerate(candidates):
        for second, _, other_group in candidates[index:]:
            if any(first == other and available < 2 for first, other, available in zip(support, second, room)):
                continue
            for first_index, (first_mask, coverage) in enumerate(group):
                for second_mask, other_coverage in other_group[first_index if support == second else 0:]:
                    if (coverage | other_coverage) == everything:
                        yield tuple(sorted((first_mask, second_mask)))


def sat_options(adj, small, large, singles, alpha, sorted_slots=False):
    problem, extra = weak_window(adj, small, large, singles, alpha)
    if sorted_slots:
        sort_contacts(problem, extra, tuple(range(len(adj))))
    edge_variables = {variable for variable in problem.edge.values() if variable > 1}
    with Cadical195(bootstrap_with=problem.formula.clauses) as solver:
        while solver.solve():
            model = solver.get_model()
            solved = problem.adjacency(model)
            yield tuple(sorted(solved[vertex] & ((1 << len(adj)) - 1) for vertex in extra))
            solver.add_clause([-literal for literal in model if abs(literal) in edge_variables])


def control(source, singles):
    totals = Counter()
    examples = {}
    for row in source.read_text().splitlines():
        row_id, adj, small, large = unpack(row)
        alpha = graph.alpha(adj) + 1
        literal = set(literal_options(adj, small, large, singles, alpha))
        actual = set(sat_options(adj, small, large, singles, alpha))
        assert literal == actual, row_id
        assert literal == set(sat_options(adj, small, large, singles, alpha, sorted_slots=True)), row_id
        for contacts in literal:
            addback = expanded(adj, contacts)
            assert graph.triangle_free(addback) and graph.alpha(addback) <= alpha
            examples.setdefault('positive', graph.to_graph6(addback))
        totals['marks'] += 1
        totals['positive_marks'] += bool(literal)
        totals['unordered_addbacks'] += len(literal)
    print('literal = SAT', singles, dict(totals), examples)
    return totals


def neighborhood_control(encoded):
    adj = graph.parse_graph6(encoded)
    order = len(adj)
    alpha = graph.alpha(adj)
    for partition in (order // 2, order - 2):
        fixed = {(left, right): bool(adj[left] >> right & 1) for left, right in combinations(range(order), 2)}
        capacity = graph.alpha([neighbors & ((1 << partition) - 1) for neighbors in adj[:partition]])
        core_sets = independent_core([neighbors & ((1 << partition) - 1) for neighbors in adj[:partition]], capacity)
        problem = Completion(order, fixed)
        neighborhood_cuts(problem, core_sets, partition, tuple(range(order)), alpha)
        assert all(problem.formula.clauses)


def swap_control(encoded):
    adj = graph.parse_graph6(encoded)
    cases = Counter()
    for center, first, second in combinations(range(len(adj)), 3):
        if adj[center] >> first & 1 or adj[center] >> second & 1 or adj[first] >> second & 1:
            continue
        for pivot, alternate in ((first, second), (second, first)):
            center_neighbors, pivot_neighbors, alternate_neighbors = (adj[vertex] for vertex in
                                                                      (center, pivot, alternate))
            overlaps = ((center_neighbors & pivot_neighbors).bit_count(),
                        (center_neighbors & alternate_neighbors).bit_count())
            shared = (pivot_neighbors & alternate_neighbors).bit_count()
            triple = (center_neighbors & pivot_neighbors & alternate_neighbors).bit_count()
            alternate_retained = (alternate_neighbors & ~(center_neighbors | pivot_neighbors)).bit_count()
            pivot_retained = (pivot_neighbors & ~(center_neighbors | alternate_neighbors)).bit_count()
            assert overlaps[1] == alternate_neighbors.bit_count() - shared - alternate_retained + triple
            assert overlaps[0] == pivot_neighbors.bit_count() - shared - pivot_retained + triple
            cases[triple != 0] += 1
    return cases


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--count', type=int, default=4)
    parser.add_argument('--neighborhood-control', type=Path)
    args = parser.parse_args()
    if args.neighborhood_control:
        rows = args.neighborhood_control.read_text().splitlines()
        swap_cases = Counter()
        for line in rows:
            neighborhood_control(line)
            swap_cases.update(swap_control(line))
        star = Completion(5, {(left, right): left == 0 for left, right in combinations(range(5), 2)})
        neighborhood_cuts(star, ((1,),), 2, (0,), 3)
        assert () in star.formula.clauses
        print('neighborhood hits hold on', len(rows), 'known graphs; tighter star impossible')
        print('swap intersection identities on independent triples:', dict(sorted(swap_cases.items())))
        return
    if args.control:
        assert not control(args.source, 2)['positive_marks']
        assert control(args.source, 3)['positive_marks']
        return
    for row in select_rows(args.source, 0, None, args.count):
        row_id, adj, small, large = unpack(row)
        start = process_time()
        count = sum(1 for _ in literal_options(adj, small, large, 4, 7))
        print(row_id, *row.split()[1:3], count, f'{process_time()-start:.6f}', flush=True)


if __name__ == '__main__':
    main()
