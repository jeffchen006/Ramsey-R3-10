#!/usr/bin/env python3
"""A degree-capacity relaxation for the remaining 32-fixed crowns."""

import argparse
from collections import Counter
from itertools import combinations_with_replacement, product
from pathlib import Path

from involution_cores import graph
from involution_sat import from_graph6, witnesses


def passes(adj, capacity, full, small, size):
    if min(capacity) < full:
        return 'mandatory'
    zero_options = [0] + [1 << vertex for vertex in range(len(adj))]
    zero_options.extend((1 << left) | (1 << right) for left in range(len(adj))
                        for right in range(left + 1, len(adj)) if adj[left] & (1 << right))
    demand = full * max(0, len(adj) - size)
    if sum(min(full, cap - full) for cap in capacity) < demand:
        return 'full-only'
    for zero_sets in combinations_with_replacement(zero_options, small):
        spare = tuple(cap - full - sum(not (mask & (1 << vertex)) for mask in zero_sets)
                      for vertex, cap in enumerate(capacity))
        if min(spare) >= 0 and sum(min(full, cap) for cap in spare) >= demand:
            return 'pass'
    return 'combined'


def covered(neighborhood, mask):
    result = 0
    for vertex, row in enumerate(neighborhood):
        if mask & (1 << vertex):
            result |= row
    return result


def direct(adj, full, small, size):
    options = []
    independent = [mask for length in range(1, len(adj) + 1)
                   for mask in witnesses(adj, (1 << len(adj)) - 1, length)]
    for amount in (size,) * full + (size - 1,) * small:
        rows = set()
        for neighborhood in product(range(1 << amount), repeat=len(adj)):
            if any(neighborhood[left] & neighborhood[right] for left in range(len(adj))
                   for right in range(left + 1, len(adj)) if adj[left] & (1 << right)):
                continue
            if any(mask.bit_count() + amount - covered(neighborhood, mask).bit_count() > size
                   for mask in independent):
                continue
            rows.add(tuple(mask.bit_count() for mask in neighborhood))
        options.append(rows)
    return {tuple(sum(row[vertex] for row in rows) for vertex in range(len(adj)))
            for rows in product(*options)}


def calibrate():
    matching_core = graph(2, ())
    path = graph(3, ((0, 1), (1, 2)))
    assert (1, 1) in direct(matching_core, 1, 0, 2)
    assert passes(matching_core, (1, 1), 1, 0, 2) == 'pass'
    assert not any(max(row) <= 1 for row in direct(path, 1, 0, 2))
    assert passes(path, (1, 1, 1), 1, 0, 2) == 'full-only'
    confirmed = 0
    for adj in (graph(3, ()), graph(3, ((0, 1),)), path):
        for size in (2, 3):
            for full, small in ((1, 0), (1, 1), (2, 0)):
                for degree in direct(adj, full, small, size):
                    assert passes(adj, degree, full, small, size) == 'pass'
                    confirmed += 1
    print(f'CAL exact small attachment CSP: {confirmed} positive degree vectors, all pass; explicit negative')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--full', type=int, choices=(2, 3, 4))
    parser.add_argument('--cores', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.control:
        calibrate()
        return
    histogram = Counter()
    with args.output.open('w', encoding='ascii') as output:
        for row in args.cores.read_text(encoding='ascii').splitlines():
            adj = from_graph6(row)
            assert len(adj) == 12 - args.full
            if next(witnesses(adj, (1 << len(adj)) - 1, 6), None) is not None:
                histogram['alpha'] += 1
                continue
            degrees = tuple(degree.bit_count() for degree in adj)
            capacities = tuple(min(9, (28 - degree) // 3) - degree for degree in degrees)
            verdict = passes(adj, capacities, args.full, 4 - args.full, 6)
            histogram[verdict] += 1
            if verdict == 'pass':
                print(row, file=output)
    print(f'T={args.full} {dict(histogram)}')


if __name__ == '__main__':
    main()
