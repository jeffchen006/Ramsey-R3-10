#!/usr/bin/env python3
"""Necessary two-by-two side attachments for the R(7) template and a C22 control."""

import argparse
import json
import random
import time
from collections import defaultdict
from itertools import combinations, product
from pathlib import Path

import networkx as nx

from set_completion import independent, indices


def graph_from(path, index):
    return nx.from_graph6_bytes(path.read_bytes().splitlines()[index])


def side_filter(inner, degree, forbidden, cap, apply_r7, sample_count):
    masks = [sum(1 << peer for peer in inner[row]) for row in range(len(inner))]
    full = (1 << len(masks)) - 1
    by_size = defaultdict(list)
    for mask in independent(masks, full, max(degree - 3, forbidden - 3)):
        by_size[mask.bit_count()].append(mask)
    saturating_sets = by_size[forbidden - 3]
    coverage = []
    for candidate in by_size[degree - 3]:
        undominated = full ^ candidate
        for vertex in indices(candidate):
            undominated &= ~masks[vertex]
        misses = sum(1 << idx for idx, subset in enumerate(saturating_sets) if not candidate & subset)
        coverage.append((candidate, undominated, misses))
    choices = defaultdict(list)
    low_deficit = sum(1 << vertex for vertex, neighbors in enumerate(masks)
                      if degree - neighbors.bit_count() < 3)
    for (first, missing_first, fail_first), (second, missing_second, fail_second) in combinations(coverage, 2):
        joint = 3 + (first & second).bit_count()
        if joint > cap or fail_first & fail_second or first & second & low_deficit:
            continue
        union, demand = first | second, missing_first | missing_second
        if union & demand:
            continue
        if apply_r7 and joint == 7:
            if any((second & ~first) & ~masks[vertex] for vertex in indices(first & ~second)):
                continue
        choices[(union, demand)].append((first, second))
    print(json.dumps({'side_candidates': len(coverage), 'saturating_sets': len(saturating_sets),
                      'side_pairs': sum(map(len, choices.values())), 'side_types': len(choices)}), flush=True)
    size = (len(choices) + 7) // 8
    unions, demands = ([bytearray(size) for _ in masks] for _ in range(2))
    choice_keys = list(choices)
    for idx, (union, demand) in enumerate(choice_keys):
        byte, on = divmod(idx, 8)
        for vertex in indices(union):
            unions[vertex][byte] |= 1 << on
        for vertex in indices(demand):
            demands[vertex][byte] |= 1 << on
    unions, demands = [[int.from_bytes(row, 'little') for row in rows] for rows in (unions, demands)]
    supported = {}
    joint_types = 0
    sample = [None] * sample_count
    generator = random.Random(12321)
    all_types = (1 << len(choices)) - 1
    for union, demand in choice_keys:
        compatible = all_types
        for vertex in indices(demand):
            compatible &= unions[vertex]
        for vertex in indices(union):
            compatible &= ~unions[vertex]
        for vertex in indices(full ^ union):
            compatible &= ~demands[vertex]
        if compatible:
            supported[(union, demand)] = choices[(union, demand)]
            options = compatible.bit_count()
            joint_types += options
            for slot in range(sample_count):
                chance = generator.randrange(joint_types)
                if chance < options:
                    partner = next(index for order, index in enumerate(indices(compatible)) if order == chance)
                    sample[slot] = (generator.choice(choices[(union, demand)]),
                                    generator.choice(choices[choice_keys[partner]]))
    sets = sorted({mask for values in supported.values() for pair in values for mask in pair})
    print(json.dumps({'supported_types': len(supported), 'supported_side_pairs': sum(map(len, supported.values())),
                      'supported_sets': len(sets), 'ordered_joint_types': joint_types}), flush=True)
    return supported, sets, sample


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--index', type=int, default=0)
    parser.add_argument('--control', nargs=2, type=int)
    parser.add_argument('--degree', type=int, default=9)
    parser.add_argument('--k', type=int, default=10)
    parser.add_argument('--cap', type=int, default=7)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--samples', type=int, default=0)
    args = parser.parse_args()
    start = time.process_time()
    graph = graph_from(args.source, args.index)
    if args.control is not None:
        left, right = args.control
        adjacent_left, adjacent_right = set(graph[left]), set(graph[right])
        outer_left = sorted(adjacent_left - adjacent_right)
        outer_right = sorted(adjacent_right - adjacent_left)
        assert left not in adjacent_right
        assert len(outer_left) == len(outer_right) == 2
        assert all(graph.has_edge(first, second) for first, second in product(outer_left, outer_right))
        inner_set = sorted(set(graph) - adjacent_left - adjacent_right - {left, right})
        truth = [tuple(sorted(sum(1 << idx for idx, vertex in enumerate(inner_set) if graph.has_edge(outer, vertex))
                              for outer in vertices)) for vertices in (outer_left, outer_right)]
        graph = nx.convert_node_labels_to_integers(graph.subgraph(inner_set), ordering='sorted')
    supported, sets, sample = side_filter(graph, args.degree, args.k, args.cap,
                                          args.control is None, args.samples)
    if args.control is not None:
        all_supported = {pair for values in supported.values() for pair in values}
        if not set(truth) <= all_supported:
            raise AssertionError(f'known solution pruned: {truth}')
        print(f'PASS actual pair neighborhoods: {truth}', flush=True)
    if args.out is not None:
        args.out.write_text(json.dumps({'sets': sets, 'pairs': [pair for values in supported.values() for pair in values],
                                        'samples': sample}) + '\n')
    print(f'CPU {time.process_time()-start:.3f}', flush=True)


if __name__ == '__main__':
    main()
