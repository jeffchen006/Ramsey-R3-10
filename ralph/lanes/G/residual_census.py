#!/usr/bin/env python3
"""Grow a small graph catalogue by edge additions and exact vertex rewiring.

The result need not be complete; compare validated canonical counts to a
trusted complete census before using it as a cover.
"""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path
import subprocess
import time

from check_rows import graph, members


def masks(adj, pool, high, low, chosen=0, size=0):
    if size >= low:
        yield chosen, size
    if size < high:
        while pool and pool.bit_count() + size >= low:
            bit = pool & -pool
            pool ^= bit
            yield from masks(adj, pool & ~adj[bit.bit_length()-1], high, low, chosen | bit, size + 1)


def additions(adj, degrees, alpha):
    for first, second in combinations(range(len(adj)), 2):
        if max(degrees[first], degrees[second]) >= alpha or adj[first] >> second & 1 or adj[first] & adj[second]:
            continue
        changed = adj.copy()
        changed[first] |= 1 << second
        changed[second] |= 1 << first
        yield graph.to_graph6(changed)


def edge_swaps(adj, degrees, alpha):
    for first, second in combinations(range(len(adj)), 2):
        if not adj[first] >> second & 1:
            continue
        changed = adj.copy()
        changed[first] ^= 1 << second
        changed[second] ^= 1 << first
        pool = ((1 << len(adj)) - 1) & ~(adj[first] | adj[second])
        witnesses = masks(changed, pool, alpha - 1, alpha - 1)
        try:
            common = next(witnesses)[0]
        except StopIteration:
            continue  # Deletion reaches lower level; additions from there suffice.
        for witness, _ in witnesses:
            common &= witness
            if not common:
                break
        common |= (1 << first) | (1 << second)
        reduced_degrees = degrees.copy()
        reduced_degrees[first] -= 1
        reduced_degrees[second] -= 1
        for add_first, add_second in combinations(members(common), 2):
            if ((add_first, add_second) == (first, second)
                    or max(reduced_degrees[add_first], reduced_degrees[add_second]) >= alpha
                    or changed[add_first] & changed[add_second]):
                continue
            changed[add_first] ^= 1 << add_second
            changed[add_second] ^= 1 << add_first
            yield graph.to_graph6(changed)
            changed[add_first] ^= 1 << add_second
            changed[add_second] ^= 1 << add_first


def rewires(adj, degrees, alpha, minimum, maximum):
    order = len(adj)
    allv = (1 << order) - 1
    full = sum(degrees) // 2
    independent = [mask for mask, _ in masks(adj, allv, alpha, alpha)]
    nwords = (len(independent) + 7) // 8
    vertex_hits = [bytearray(nwords) for _ in adj]
    for index, mask in enumerate(independent):
        for vertex in members(mask):
            vertex_hits[vertex][index // 8] |= 1 << (index % 8)
    hits = [int.from_bytes(data, 'little') for data in vertex_hits]
    goals = (1 << len(independent)) - 1
    saturated = sum(1 << vertex for vertex, degree in enumerate(degrees) if degree == alpha)
    smallest = max(0, minimum - full + min(degrees))
    largest = min(alpha, maximum - full + max(degrees))
    if smallest > largest:
        return

    def search(allowed, mask, size, hit):
        if size >= smallest:
            missed = goals ^ hit
            if not missed:
                roots = allv ^ mask
            else:
                roots = independent[(missed & -missed).bit_length() - 1] & ~mask
            sat = saturated & mask
            for root in members(roots):
                edges = full + size - degrees[root]
                if (not minimum <= edges <= maximum or adj[root] == mask or sat & ~adj[root]
                        or missed & ~hits[root]):
                    continue
                changed = adj.copy()
                changed[root] = mask
                for other in members(adj[root] ^ mask):
                    changed[other] ^= 1 << root
                yield graph.to_graph6(changed)
        if size < largest:
            while allowed and allowed.bit_count() + size >= smallest:
                bit = allowed & -allowed
                allowed ^= bit
                vertex = bit.bit_length() - 1
                yield from search(allowed & ~adj[vertex], mask | bit, size + 1, hit | hits[vertex])

    yield from search(allv, 0, 0, 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputs', type=Path, nargs='+')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--canon', type=Path, required=True)
    parser.add_argument('--min', type=int, required=True)
    parser.add_argument('--max', type=int, required=True)
    parser.add_argument('--alpha', type=int, default=8)
    parser.add_argument('--steps', type=int, default=10)
    parser.add_argument('--aim', type=int)
    parser.add_argument('--swap-only', action='store_true')
    args = parser.parse_args()

    def canonical(lines):
        result = subprocess.run([str(args.canon.resolve()), '-q'], input=''.join(row+'\n' for row in sorted(lines)),
                                capture_output=True, check=True, text=True)
        return set(result.stdout.splitlines())

    seen = canonical(set(row for path in args.inputs for row in path.read_text().splitlines()))
    frontier = seen.copy()
    start = time.process_time()
    for step in range(args.steps):
        new = set()
        for row in sorted(frontier):
            adj = graph.parse_graph6(row)
            degrees = list(map(int.bit_count, adj))
            count = sum(degrees) // 2
            if count < args.max:
                new.update(additions(adj, degrees, args.alpha))
            new.update(edge_swaps(adj, degrees, args.alpha))
            if not args.swap_only:
                new.update(rewires(adj, degrees, args.alpha, args.min, args.max))
        frontier = canonical(new) - seen
        seen.update(frontier)
        args.out.write_text(''.join(row + '\n' for row in sorted(seen)))
        counts = Counter(sum(map(int.bit_count, graph.parse_graph6(row))) // 2 for row in seen)
        print(f'{step+1}: raw {len(new)}, new {len(frontier)}, counts {sorted(counts.items())}; '
              f'cumulative Python CPU {time.process_time() - start:.3f}s', flush=True)
        if not frontier or (args.aim is not None and len(seen) >= args.aim):
            break


if __name__ == '__main__':
    main()
