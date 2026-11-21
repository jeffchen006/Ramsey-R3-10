#!/usr/bin/env python3
"""Independent exhaustive order-12 check and production witness verifier."""

import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, permutations

import networkx as nx


def bits(mask):
    return {vertex for vertex in range(mask.bit_length()) if mask >> vertex & 1}


@lru_cache(maxsize=64)
def graph_data(graph6):
    graph = nx.from_graph6_bytes(graph6.encode('ascii'))
    neighbors = {vertex: set(graph[vertex]) for vertex in graph}
    return graph, neighbors


def setup(graph6, group_masks):
    graph, neighbors = graph_data(graph6)
    groups = [bits(mask) for mask in group_masks]
    group = {vertex: own for own, members in enumerate(groups) for vertex in members}
    degree = {vertex: 8 - len(neighbors[vertex]) for vertex in graph}
    budgets = {(left, right): 4 - len(neighbors[left] & neighbors[right]) - (group[left] == group[right])
               for left, right in combinations(graph, 2)}
    return graph, neighbors, groups, degree, budgets


def matching_types(graph, groups):
    first, second, third = map(sorted, groups)

    def matchings(left, right):
        for ordering in permutations(right):
            edges = tuple(zip(left, ordering))
            if all(graph.has_edge(*edge) for edge in edges):
                yield edges

    types = set()
    for match_ab in matchings(first, second):
        for match_ac in matchings(first, third):
            for match_bc in matchings(second, third):
                cover = nx.Graph((*match_ab, *match_ac, *match_bc))
                types.add(1 if nx.is_connected(cover) else 2)
    return sum(types)


def check_witness(graph6, group_masks, witness):
    graph, neighbors, groups, degree, budgets = setup(graph6, group_masks)
    bound = len(groups[0])
    states = list(map(bits, witness))
    assert len(states) == 3 and all(state <= set(graph) for state in states)
    for state in states:
        assert all(not graph.has_edge(*edge) for edge in combinations(state, 2))
        assert all(len(state & part) <= 3 for part in groups)
        assert all(len(state & neighbors[vertex]) <= 4 for vertex in graph)
    assert all(sum(vertex in state for state in states) <= degree[vertex] for vertex in graph)
    assert all(sum(left in state and right in state for state in states) <= bound_pair
               for (left, right), bound_pair in budgets.items())
    for amount in (2, 3):
        for selected in combinations(states, amount):
            if amount == 2:
                assert len(selected[0] & selected[1]) <= 3
            residual = set(graph) - set.union(*selected)
            assert not any(all(not graph.has_edge(*edge) for edge in combinations(group, 2))
                           for group in combinations(residual, bound + 2 - amount))


def exhaustive_control(graph6, group_masks):
    graph, neighbors, groups, degree, budgets = setup(graph6, group_masks)
    encode = lambda vertices: sum(1 << vertex for vertex in vertices)
    independent = {amount: [] for amount in range(5)}
    for amount, family in independent.items():
        for group in combinations(graph, amount):
            if all(not graph.has_edge(*edge) for edge in combinations(group, 2)):
                family.append(group)
    assert independent[4] and not any(all(not graph.has_edge(*edge) for edge in combinations(group, 2))
                                     for group in combinations(graph, 5))
    candidates = []
    for family in independent.values():
        for group in family:
            state = set(group)
            if (any(degree[vertex] < 1 for vertex in group)
                    or any(budgets[edge] < 1 for edge in combinations(group, 2))
                    or any(len(state & part) > 3 for part in groups)
                    or any(len(state & neighbors[vertex]) > 4 for vertex in graph)):
                continue
            candidates.append(encode(group))
    independence = {amount: [encode(group) for group in independent[amount]] for amount in (3, 4)}
    over_two = [encode(edge) for edge, bound_pair in budgets.items() if bound_pair < 2]
    over_three = [encode(edge) for edge, bound_pair in budgets.items() if bound_pair < 3]
    over_two.extend(encode((vertex,)) for vertex in graph if degree[vertex] < 2)
    over_three.extend(encode((vertex,)) for vertex in graph if degree[vertex] < 3)
    allowed_pairs = set()
    for left, right in combinations_with_replacement(candidates, 2):
        overlap = left & right
        if (overlap.bit_count() <= 3 and not any(mask & overlap == mask for mask in over_two)
                and all(mask & (left | right) for mask in independence[4])):
            allowed_pairs.add((left, right))
    count = 0
    for first, second, third in combinations_with_replacement(candidates, 3):
        if ((first, second) not in allowed_pairs or (first, third) not in allowed_pairs
                or (second, third) not in allowed_pairs):
            continue
        if any(mask & first & second & third == mask for mask in over_three):
            continue
        if all(mask & (first | second | third) for mask in independence[3]):
            count += 1
    return len(candidates), count, matching_types(graph, groups)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('result')
    parser.add_argument('--exhaustive-control', action='store_true')
    args = parser.parse_args()
    seen = set()
    counts = Counter()
    with open(args.source) as sources, open(args.result) as results:
        for source, result in zip(sources, results, strict=True):
            index, first, second, third, graph6 = source.split()
            key = tuple(map(int, (index, first, second, third)))
            assert key not in seen
            seen.add(key)
            row = tuple(map(int, result.split()))
            assert len(row) == 12 and row[:4] == key
            state, count, checked, num_candidates, matching = row[4:9]
            assert state in (-1, 0, 1) and matching in (1, 2, 3)
            assert checked >= count >= 0
            assert state != 0 or count == 0
            assert state != 1 or count > 0
            if count:
                check_witness(graph6, key[1:], row[9:])
            if args.exhaustive_control:
                assert state != -1
                assert (num_candidates, count, matching) == exhaustive_control(graph6, key[1:]), row
            counts[state] += 1
    print(f'PASS records={len(seen)} viable={counts[1]} rejected={counts[0]} capped={counts[-1]}'
          f' exhaustive={args.exhaustive_control}')


if __name__ == '__main__':
    main()
