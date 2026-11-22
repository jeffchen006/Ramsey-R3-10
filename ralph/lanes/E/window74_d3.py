#!/usr/bin/env python3
"""Exact three-neighbor gluing from a closed-neighborhood deletion core."""

import argparse
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import subprocess

from involution_cores import bits, graph
from involution_sat import from_graph6, to_graph6


def independent_sets(rows, limit):
    bins = [[] for _ in range(limit + 1)]

    def extend(mask, allowed, size):
        bins[size].append(mask)
        if size < limit:
            while allowed:
                low = allowed & -allowed
                allowed ^= low
                extend(mask | low, allowed & ~rows[low.bit_length() - 1], size + 1)

    extend(0, (1 << len(rows)) - 1, 0)
    return tuple(tuple(sorted(bucket)) for bucket in bins)


def transpose(masks, order):
    incidence = [0] * order
    for index, mask in enumerate(masks):
        for vertex in bits(mask):
            incidence[vertex] |= 1 << index
    return tuple(incidence)


def meeting(incidence, mask):
    result = 0
    for vertex in bits(mask):
        result |= incidence[vertex]
    return result


def supports(rows, alpha, added, counts):
    independent = independent_sets(rows, alpha)
    assert not independent[alpha]
    required_pair, required_triple = independent[alpha - 1], independent[alpha - 2]
    pair_index = transpose(required_pair, len(rows))
    triple_index = transpose(required_triple, len(rows))
    pair_all, triple_all = (1 << len(bucket) for bucket in (required_pair, required_triple))
    domains = independent[:alpha]
    indexed = tuple(tuple((mask, (pair_all - 1) ^ meeting(pair_index, mask),
                           (triple_all - 1) ^ meeting(triple_index, mask)) for mask in domain)
                    for domain in domains)

    for third_size, third in enumerate(domains):
        if not third or not (third_size <= added <= 3 * third_size):
            continue
        third_incidence = transpose(third, len(rows))
        pair_hits = tuple(meeting(third_incidence, target) for target in required_pair)
        triple_hits = tuple(meeting(third_incidence, target) for target in required_triple)
        all_third = (1 << len(third)) - 1
        allowed_cache = {}

        def allowed(missed):
            if missed not in allowed_cache:
                result = all_third
                for index in bits(missed):
                    result &= pair_hits[index]
                    if not result:
                        break
                allowed_cache[missed] = result
            return allowed_cache[missed]

        for first_size, first in enumerate(indexed[:third_size + 1]):
            second_size = added - first_size - third_size
            if not first_size <= second_size <= third_size:
                continue
            second = indexed[second_size]
            for first_id, (left, missed_left, triple_left) in enumerate(first):
                allowed_left = allowed(missed_left)
                if not allowed_left:
                    continue
                offset = first_id if first_size == second_size else 0
                for second_id in range(offset, len(second)):
                    right, missed_right, triple_right = second[second_id]
                    counts['pairs examined'] += 1
                    if missed_left & missed_right:
                        continue
                    candidates = allowed_left & allowed(missed_right)
                    if second_size == third_size:
                        candidates &= -1 << second_id
                    if not candidates:
                        continue
                    counts['pairs with a pairwise-compatible third'] += 1
                    for index in bits(triple_left & triple_right):
                        candidates &= triple_hits[index]
                        if not candidates:
                            break
                    for index in bits(candidates):
                        yield left, right, third[index]


def glue(rows, columns):
    order = len(rows)
    assert len(columns) == 3
    edges = [(left, right) for left, right in combinations(range(order), 2) if rows[left] >> right & 1]
    edges.extend((order + index, order + 3) for index in range(3))
    edges.extend((vertex, order + index) for index, column in enumerate(columns) for vertex in bits(column))
    return graph(order + 4, edges)


def is_valid(rows, alpha):
    for vertex, row in enumerate(rows):
        if any(row & rows[neighbor] for neighbor in bits(row) if neighbor > vertex):
            return False
    return not independent_sets(rows, alpha + 1)[alpha + 1]


def canon(graphs, shortg):
    return set(subprocess.check_output([str(shortg), '-q'], input=''.join(sorted(graphs)), text=True).splitlines())


def calibrate(catalogue, shortg):
    known = {line + '\n' for line in catalogue.read_text(encoding='ascii').splitlines()}
    assert len(known) == len(canon(known, shortg)) == 3
    known_rooted = [line for line in known if 3 in map(int.bit_count, from_graph6(line.strip()))]
    counts = Counter()
    actual = set()
    core_order = 4
    possible = tuple(combinations(range(core_order), 2))
    for mask in range(1 << len(possible)):
        rows = graph(core_order, [possible[index] for index in bits(mask)])
        if not is_valid(rows, 2):
            continue
        brute = {depth: set() for depth in range(0, 3 * (3 - 1) + 1)}
        for columns in product(range(1 << core_order), repeat=3):
            if tuple(sorted(columns, key=lambda col: (col.bit_count(), col))) != columns:
                continue
            if is_valid(glue(rows, columns), 3):
                brute[sum(map(int.bit_count, columns))].add(columns)
        for depth, expected in brute.items():
            produced = set(supports(rows, 3, depth, counts))
            assert produced == expected, (mask, depth, produced ^ expected)
            actual.update(to_graph6(glue(rows, option)) + '\n' for option in produced)
        counts['brute parent comparisons'] += 1
    assert known_rooted and canon(known_rooted, shortg) == canon(actual, shortg)
    print('order-8 catalogue:', len(known), 'root-degree-three classes', len(known_rooted),
          'brute-checked equality', dict(counts), flush=True)


def census(catalogue, output, indices, target):
    keys = catalogue.read_text(encoding='ascii').splitlines()
    assert len(keys) == len(set(keys)) == 191
    indices = indices if indices else range(len(keys))
    counts = Counter()
    with output.open('x', encoding='ascii') as out:
        for index in indices:
            rows = tuple(from_graph6(keys[index]))
            assert len(rows) == 22 and is_valid(rows, 6)
            edges = sum(map(int.bit_count, rows)) // 2
            local = Counter()
            for columns in supports(rows, 7, target - edges - 3, local):
                lifted = glue(rows, columns)
                assert is_valid(lifted, 7) and sum(map(int.bit_count, lifted)) == 2 * target
                print(to_graph6(lifted), file=out)
                local['lifts'] += 1
            print(index, keys[index], 'edges', edges, 'result', dict(local), flush=True)
            counts.update(local)
            counts['parents'] += 1
    print('finished', dict(counts), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    control = commands.add_parser('calibrate')
    control.add_argument('catalogue', type=Path)
    control.add_argument('shortg', type=Path)
    exact = commands.add_parser('census')
    exact.add_argument('catalogue', type=Path)
    exact.add_argument('output', type=Path)
    exact.add_argument('--indices', type=int, nargs='+')
    exact.add_argument('--target', type=int, default=74)
    args = parser.parse_args()
    if args.command == 'calibrate':
        calibrate(args.catalogue, args.shortg)
    else:
        census(args.catalogue, args.output, args.indices, args.target)
