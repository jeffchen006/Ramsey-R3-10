#!/usr/bin/env python3
"""Compare the C16 maximum-root SAT output with explicit relabelling."""

import argparse
from collections import defaultdict
from itertools import combinations, permutations
from pathlib import Path
import sys

from catalogue_m3 import signature_of, swap
from max_root import catalogue, count_edges, edge_floor
from kernel_projection import bits, decode, encode

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
from check_graph import brute_alpha, triangle_free


def direct_squares(graph, first, second):
    return sum((graph[first] & graph[other]).bit_count() - 1
               for other in bits(graph[second]) if other != first)


def signed_square_replay(graph, boundary):
    signed = sum((1 if (first < boundary) == (second < boundary) else -1) * direct_squares(graph, first, second)
                 for first, second in combinations(range(len(graph)), 2) if graph[first] >> second & 1)
    inner_only = outer_only = alternating = 0
    for vertices in combinations(range(len(graph)), 4):
        if any(sum(graph[first] >> second & 1 for second in vertices) != 2 for first in vertices):
            continue
        inner = [vertex for vertex in vertices if vertex < boundary]
        if len(inner) == 4:
            inner_only += 1
        elif not inner:
            outer_only += 1
        elif len(inner) == 2 and not graph[inner[0]] >> inner[1] & 1:
            alternating += 1
    assert signed == 4 * (inner_only + outer_only - alternating)


def relabel(graph, order):
    position = {vertex: index for index, vertex in enumerate(order)}
    return [sum(1 << position[neighbor] for neighbor in bits(graph[vertex])) for vertex in order]


def census(order, degree, path):
    width = degree - 1
    keys = list(catalogue(order, degree))
    observed = set()
    for line in path.read_text().splitlines():
        kernel = decode(line)
        edge_count = count_edges(kernel)
        assert edge_count >= edge_floor(order, degree) and len(kernel) == 2 * width
        partners = {0: 0}
        for vertex in range(width):
            for occupied, count in list(partners.items()):
                for neighbor in bits(kernel[vertex] & ~occupied):
                    partners[occupied | (1 << neighbor)] = count + 1
        if max(partners.values()) < width - 1:
            continue
        if order < 6 * degree - 12 and any((first & second).bit_count() >= 2
                                          for first, second in combinations(kernel[:width], 2)):
            continue
        signature = signature_of(width, line)
        observed.add(min(signature, swap(signature)))
    assert observed == {signature_of(width, line) for line in keys}
    assert len(observed) == len(keys)
    print(f'PASS genbg census order={order} degree={degree} gives {len(keys)} root-swap keys')


def calibration(path, directory, variants):
    width, degree, order = 4, 5, 16
    existing = [decode(line) for line in path.read_text().splitlines()]
    controls = [graph for graph in existing if all(row.bit_count() == degree for row in graph)
                and all((graph[first] & graph[second]).bit_count() <= 3
                        for first, second in combinations(range(order), 2))]
    assert len(controls) == 5 and len(set(map(tuple, controls))) == 5
    keys = {tuple(decode(line)): index for index, line in enumerate(catalogue(order, degree))}
    expected = defaultdict(set)
    for graph in controls:
        assert triangle_free(graph) and brute_alpha(graph) == degree
        square_counts = {(first, second): direct_squares(graph, first, second)
                         for first, row in enumerate(graph) for second in bits(row) if second > first}
        maximum = max(square_counts.values())
        witnessed = 0
        for (left, right), squares in square_counts.items():
            if squares != maximum:
                continue
            for first, second in ((left, right), (right, left)):
                a_side = tuple(bits(graph[first] ^ (1 << second)))
                b_side = tuple(bits(graph[second] ^ (1 << first)))
                outside = set(range(order)) - set(a_side) - set(b_side) - {first, second}
                for a_order in permutations(a_side):
                    for b_order in permutations(b_side):
                        fixed = a_order + b_order
                        kernel = tuple(sum((graph[vertex] >> coord & 1) << index
                                           for index, coord in enumerate(fixed)) for vertex in fixed)
                        if kernel not in keys:
                            continue
                        outside_order = {vertex: tuple(graph[vertex] >> coord & 1 for coord in fixed)
                                         for vertex in outside}
                        assert len(set(outside_order.values())) == len(outside)
                        labelled = relabel(graph, fixed + (first, second)
                                           + tuple(sorted(outside, key=outside_order.__getitem__)))
                        expected[keys[kernel]].add(encode(labelled))
                        witnessed += 1
        assert witnessed
    for variant in variants:
        for index in range(len(keys)):
            prefix = directory / f'{variant}-{index}'
            assert 'exhausted ' in prefix.with_suffix('.log').read_text()
            actual = prefix.with_suffix('.g6').read_text().splitlines()
            assert len(actual) == len(set(actual)) and set(actual) == expected[index], (variant, index)
            for line in actual:
                graph = decode(line)
                assert triangle_free(graph) and brute_alpha(graph) == degree
                assert all(row.bit_count() == degree for row in graph)
                signed_square_replay(graph, 2 * degree)
        print(f'PASS {variant}: exact labelled sets for {len(keys)} kernels, '
              f'{sum(map(len, expected.values()))} outputs from five smaller classes')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='mode', required=True)
    cover = subs.add_parser('census')
    cover.add_argument('order', type=int)
    cover.add_argument('degree', type=int)
    cover.add_argument('path', type=Path)
    control = subs.add_parser('calibration')
    control.add_argument('path', type=Path)
    control.add_argument('directory', type=Path)
    control.add_argument('variants', nargs='+')
    args = parser.parse_args()
    if args.mode == 'census':
        census(args.order, args.degree, args.path)
    else:
        calibration(args.path, args.directory, args.variants)


if __name__ == '__main__':
    main()
