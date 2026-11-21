#!/usr/bin/env python3
"""Exhaustive direct small control and tagged output verifier for joint_replace."""

import argparse
from collections import defaultdict
from itertools import combinations, combinations_with_replacement, permutations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
import check_graph as graph


def normalize(rows, marked):
    retained = ~sum(1 << vertex for vertex in marked)
    return min((tuple(rows[vertex] & retained for vertex in perm),
                tuple(bool(rows[first] & (1 << second)) for first, second in combinations(perm, 2)))
               for perm in permutations(marked))


def direct(seed, marked, alpha, lo, hi, min_deg):
    """Brute-force all pairs of exterior vertex subsets; check the resulting graph."""
    order = len(seed)
    fixed = sorted(set(range(order)) - set(marked))
    choices = [sum(1 << vertex for vertex in selected)
               for size in range(alpha + 1) for selected in combinations(fixed, size)]
    retained = ~sum(1 << vertex for vertex in marked)
    base = [row & retained if vertex in fixed else 0 for vertex, row in enumerate(seed)]
    edges = sum(map(int.bit_count, base)) // 2
    eligible = [mask for mask in choices if all(not (mask & seed[vertex]) for vertex in fixed if mask & (1 << vertex))]
    internal = tuple(combinations(marked, 2))
    for attachments in combinations_with_replacement(eligible, len(marked)):
        crossing = sum(map(int.bit_count, attachments))
        for shape in range(1 << len(internal)):
            if not lo <= edges + crossing + shape.bit_count() <= hi:
                continue
            rows = base.copy()
            for root, mask in zip(marked, attachments):
                rows[root] = mask
                for vertex in fixed:
                    if mask & (1 << vertex):
                        rows[vertex] |= 1 << root
            for pos, (first, second) in enumerate(internal):
                if shape & (1 << pos):
                    rows[first] |= 1 << second
                    rows[second] |= 1 << first
            if min(map(int.bit_count, rows)) >= min_deg and graph.triangle_free(rows) and graph.alpha(rows) <= alpha:
                yield normalize(rows, marked)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('seeds', type=Path)
    parser.add_argument('tagged', type=Path)
    parser.add_argument('alpha', type=int)
    parser.add_argument('lo', type=int)
    parser.add_argument('hi', type=int)
    parser.add_argument('min_deg', type=int)
    parser.add_argument('--brute', action='store_true')
    parser.add_argument('--triple', action='store_true')
    args = parser.parse_args()
    seeds = [graph.parse_graph6(line) for line in args.seeds.read_text().splitlines()]
    observed = defaultdict(set)
    checked = 0
    size = 3 if args.triple else 2
    with args.tagged.open() as stream:
        for raw in stream:
            source, *marked, encoded = raw.rstrip('\n').split('\t')
            source, marked = int(source), tuple(map(int, marked))
            rows = graph.parse_graph6(encoded)
            seed = seeds[source - 1]
            assert len(rows) == len(seed) and 0 < source <= len(seeds) and len(marked) == size
            assert tuple(sorted(set(marked))) == marked and 0 <= marked[0] <= marked[-1] < len(rows)
            retained = ~sum(1 << vertex for vertex in marked)
            assert all(not ((x ^ y) & retained) for v, (x, y) in enumerate(zip(rows, seed)) if retained & (1 << v))
            degrees = list(map(int.bit_count, rows))
            assert args.lo <= sum(degrees) // 2 <= args.hi and min(degrees) >= args.min_deg
            assert graph.triangle_free(rows) and graph.alpha(rows) <= args.alpha
            if args.brute:
                result = normalize(rows, marked)
                key = (source, marked)
                observed[key].add(result)
            checked += 1
    print(f'{checked} valid tagged outputs')
    if args.brute:
        count = 0
        for source, seed in enumerate(seeds, 1):
            for marked in combinations(range(len(seed)), size):
                expected = set(direct(seed, marked, args.alpha, args.lo, args.hi, args.min_deg))
                assert expected == observed[source, marked], (source, marked)
                count += 1
        print(f'Small exact equality: {count} tagged base graphs')


if __name__ == '__main__':
    main()
