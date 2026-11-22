#!/usr/bin/env python3
"""Measure two nonadjacent-root antineighbourhood orders in marked windows."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations
from pathlib import Path

from audit_equality_templates import graph6
from audit_strip_extensions import independent, mark, validate_graph
from residue_bundle import parse_graph6, triangle_free


def residue(graph, first, second):
    return ((1 << len(graph))-1) & ~((1 << first) | (1 << second) | graph[first] | graph[second])


def exhaustive_pairs(graph):
    for first, second in combinations(range(len(graph)), 2):
        if not (graph[first] >> second & 1):
            yield first, second, residue(graph, first, second)


def calibrate(path):
    graph = parse_graph6(path.read_text().splitlines()[0])
    assert len(graph) == 13 and triangle_free(graph)
    assert next(independent(graph, 4), None) is not None and next(independent(graph, 5), None) is None
    count = 0
    for first, second, mask in exhaustive_pairs(graph):
        check = {exterior for exterior in range(len(graph)) if exterior not in (first, second)
                 and not (graph[exterior] >> first & 1) and not (graph[exterior] >> second & 1)}
        assert mask == sum(1 << vertex for vertex in check)
        assert next(independent(graph, 3, mask), None) is None
        count += 1
    print('C13 pair controls:', count, flush=True)


def profile(path):
    maxima = {key: Counter() for key in ('any', 'min_root', 'same_side', 'at_least_one_mark')}
    candidates = {key: Counter() for key in maxima}
    for line in path.read_text().splitlines():
        _, first, second, encoded = line.split()
        graph = validate_graph(encoded)
        masks = (int(first), int(second))
        mark(graph, *masks)
        degree = min(neighbors.bit_count() for neighbors in graph)
        best = dict.fromkeys(maxima, 0)
        for left, right, mask in exhaustive_pairs(graph):
            roots = (1 << left) | (1 << right)
            types = ['any']
            if min(graph[left].bit_count(), graph[right].bit_count()) == degree:
                types.append('min_root')
            if (masks[0] | masks[1]) & roots:
                types.append('at_least_one_mark')
            if any(side & roots == roots for side in masks):
                types.append('same_side')
            order = mask.bit_count()
            for kind in types:
                candidates[kind][degree, order] += 1
                best[kind] = max(best[kind], order)
            if order >= 16:
                assert next(independent(graph, 6, mask), None) is None
        for kind, order in best.items():
            maxima[kind][degree, order] += 1
    print(path.name, flush=True)
    for kind in maxima:
        frequency = sorted((key, count) for key, count in candidates[kind].items() if key[1] >= 15)
        print(kind, 'maxima (delta, order)', sorted(maxima[kind].items()), 'candidate pairs >=15', frequency, flush=True)


def chosen_parents(path, output):
    successful, missing = 0, 0
    with output.open('w') as stream:
        for line in path.read_text().splitlines():
            _, _, _, encoded = line.split()
            graph = validate_graph(encoded)
            assert len(graph) == 26 and min(neighbors.bit_count() for neighbors in graph) == 4
            for first, second, mask in exhaustive_pairs(graph):
                if mask.bit_count() < 16 or min(graph[first].bit_count(), graph[second].bit_count()) != 4:
                    continue
                root = first if graph[first].bit_count() == 4 else second
                parent = [vertex for vertex in range(26) if vertex != root and not (graph[root] >> vertex & 1)]
                assert len(parent) == 21
                pairs = [(left, right) for left, right in combinations(range(21), 2)
                         if graph[parent[left]] >> parent[right] & 1]
                print(graph6(21, pairs).decode('ascii'), file=stream)
                successful += 1
                break
            else:
                missing += 1
    print('degree-four-root parent picks:', successful, 'outside this source:', missing, flush=True)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('control', type=Path)
    parser.add_argument('inputs', type=Path, nargs='+')
    parser.add_argument('--parents', type=Path)
    args = parser.parse_args()
    calibrate(args.control)
    for path in args.inputs:
        profile(path)
    if args.parents:
        assert len(args.inputs) == 1
        chosen_parents(args.inputs[0], args.parents)
