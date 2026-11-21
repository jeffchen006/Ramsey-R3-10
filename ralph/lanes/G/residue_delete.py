#!/usr/bin/env python3
"""Generate tagged induced residues by hitting every forbidden independent set."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys
from time import process_time

from check_root_cover import induced, vertices, graph


def exact_independent(adj, size):
    def visit(allowed, selected, needed):
        if not needed:
            yield selected
        else:
            while allowed.bit_count() >= needed:
                bit = allowed & -allowed
                allowed ^= bit
                yield from visit(allowed & ~adj[bit.bit_length() - 1], selected | bit, needed - 1)

    yield from visit((1 << len(adj)) - 1, 0, size)


def deletions(adj, target, alpha, lo, hi):
    order = len(adj)
    universe = (1 << order) - 1
    remaining = order - target
    edges_initial = sum(map(int.bit_count, adj)) // 2
    witnesses = tuple(exact_independent(adj, alpha + 1))
    words = [bytearray((len(witnesses) + 7) // 8) for _ in adj]
    for index, witness in enumerate(witnesses):
        for vertex in vertices(witness):
            words[vertex][index // 8] |= 1 << (index % 8)
    hit = [int.from_bytes(word, 'little') for word in words]

    def search(allowed, deleted, missing, count, edges):
        if not count:
            if not missing and lo <= edges <= hi:
                yield deleted, edges
            return
        if allowed.bit_count() < count or edges < lo:
            return
        remaining_mask = universe ^ deleted
        if edges - hi > count * max_degrees:
            return
        choices = witnesses[(missing & -missing).bit_length() - 1] & allowed if missing else allowed
        while choices:
            bit = choices & -choices
            choices ^= bit
            allowed ^= bit
            vertex = bit.bit_length() - 1
            yield from search(allowed, deleted | bit, missing & ~hit[vertex], count - 1,
                              edges - (adj[vertex] & remaining_mask).bit_count())

    max_degrees = max(map(int.bit_count, adj))
    yield from search(universe, 0, (1 << len(witnesses)) - 1, remaining, edges_initial)


def brute(adj, target, alpha, lo, hi):
    universe = (1 << len(adj)) - 1
    for deleted in combinations(range(len(adj)), len(adj) - target):
        mask = sum(1 << vertex for vertex in deleted)
        rows = induced(adj, universe ^ mask)
        edges = sum(map(int.bit_count, rows)) // 2
        if lo <= edges <= hi and graph.alpha(rows) <= alpha:
            yield mask, edges


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('seeds', type=Path)
    parser.add_argument('target', type=int)
    parser.add_argument('alpha', type=int)
    parser.add_argument('lo', type=int)
    parser.add_argument('hi', type=int)
    parser.add_argument('--brute', action='store_true')
    args = parser.parse_args()
    started = process_time()
    grand = Counter()
    for index, line in enumerate(args.seeds.read_text().splitlines(), 1):
        adj = graph.parse_graph6(line)
        assert len(adj) >= args.target and graph.triangle_free(adj)
        universe = (1 << len(adj)) - 1
        result = list(deletions(adj, args.target, args.alpha, args.lo, args.hi))
        if args.brute:
            assert len(result) == len(set(result)) and set(result) == set(brute(adj, args.target, args.alpha, args.lo, args.hi)), index
        stats = Counter()
        for mask, edges in result:
            print(index, hex(mask), edges, graph.to_graph6(induced(adj, universe ^ mask)), sep='\t')
            stats[edges] += 1
        grand.update(stats)
        print(f'{index} {sorted(stats.items())}', file=sys.stderr, flush=True)
    print(f'Total {sorted(grand.items())}; CPU={process_time() - started:.3f}s', file=sys.stderr)


if __name__ == '__main__':
    main()
