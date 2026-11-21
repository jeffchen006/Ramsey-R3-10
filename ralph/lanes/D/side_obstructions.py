#!/usr/bin/env python3
"""Exact forbidden neighborhood-support multisets on up to four coordinates."""

import argparse
from collections import Counter
from itertools import combinations, permutations
from pathlib import Path
import json
import time


def bits(mask):
    while mask:
        leading = mask & -mask
        yield leading.bit_length() - 1
        mask ^= leading


def setup(width, masks):
    root = width + len(masks)
    adj = [1 << root] * width + list(masks) + [(1 << width) - 1]
    for vertex, mask in enumerate(masks, width):
        for neighbor in bits(mask):
            adj[neighbor] |= 1 << vertex
    edges = [(left, right) for left, right in combinations(range(width, root), 2)
             if not (masks[left - width] & masks[right - width])]
    return root, adj, edges


def local_completion(width, masks):
    root, adj, edges = setup(width, masks)
    if any((adj[left] & adj[right]).bit_count() > 3 for left, right in combinations(range(root + 1), 2)):
        return False
    witnesses = set()
    for indep in combinations(range(root), width + 1):
        packed = sum(1 << vertex for vertex in indep)
        if any(adj[vertex] & packed for vertex in indep):
            continue
        clause = sum(1 << index for index, (left, right) in enumerate(edges)
                     if packed >> left & packed >> right & 1)
        if not clause:
            return False
        witnesses.add(clause)
    required = []
    for clause in sorted(witnesses, key=lambda mask: (mask.bit_count(), mask)):
        if not any(previous & clause == previous for previous in required):
            required.append(clause)

    def search(pending):
        if not pending:
            return True
        choices = None
        for clause in pending:
            if choices is not None and clause.bit_count() >= len(choices):
                continue
            admissible = []
            for index in bits(clause):
                left, right = edges[index]
                if adj[left] & adj[right]:
                    continue
                if any((adj[left] & adj[vertex]).bit_count() >= 3 for vertex in bits(adj[right])):
                    continue
                if any((adj[right] & adj[vertex]).bit_count() >= 3 for vertex in bits(adj[left])):
                    continue
                admissible.append(index)
            if not admissible:
                return False
            if choices is None or len(admissible) < len(choices):
                choices = admissible
        for index in choices:
            left, right = edges[index]
            adj[left] ^= 1 << right
            adj[right] ^= 1 << left
            feasible = search([clause for clause in pending if not (clause >> index & 1)])
            adj[left] ^= 1 << right
            adj[right] ^= 1 << left
            if feasible:
                return True
        return False

    return search(required)


def base_patterns(width, masks):
    if any(masks.count(1 << vertex) > 1 for vertex in range(width)):
        return False
    return all(sum(mask >> left & mask >> right & 1 for mask in masks) <= 2
               for left, right in combinations(range(width), 2))


def catalogue(width):
    allowed = [mask for mask in range(1, 1 << width) if mask.bit_count() <= 3]
    feasible = {()}
    failed = set()
    counts = []
    while feasible:
        expanded = {tuple(sorted(masks + (mask,))) for masks in feasible for mask in allowed}
        next_feasible = set()
        new_failed = 0
        for masks in sorted(expanded):
            if not base_patterns(width, masks):
                continue
            if any(masks[:idx] + masks[idx + 1:] not in feasible for idx in range(len(masks))):
                continue
            if local_completion(width, masks):
                next_feasible.add(masks)
            else:
                failed.add(masks)
                new_failed += 1
        counts.append((len(next_feasible), new_failed))
        feasible = next_feasible
    return sorted(failed), counts


def brute(width, masks):
    root, base, options = setup(width, masks)
    indep_sets = [tuple(combinations(group, 2)) for group in combinations(range(root), width + 1)]
    for options_word in range(1 << len(options)):
        adj = base[:]
        for index, (left, right) in enumerate(options):
            if options_word >> index & 1:
                adj[left] |= 1 << right
                adj[right] |= 1 << left
        if any(adj[left] >> right & 1 and adj[left] & adj[right] or (adj[left] & adj[right]).bit_count() > 3
               for left, right in combinations(range(root + 1), 2)):
            continue
        if all(any(adj[left] >> right & 1 for left, right in group) for group in indep_sets):
            return True
    return False


def representative(width, masks):
    return min(tuple(sorted(sum(1 << perm[coord] for coord in bits(mask)) for mask in masks))
               for perm in permutations(range(width)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--max-width', type=int, default=4, choices=(2, 3, 4))
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    start = time.process_time()
    reports = {}
    for width in range(2, args.max_width + 1):
        failed, counts = catalogue(width)
        representatives = {representative(width, masks) for masks in failed}
        print(f'T={width} (feasible,new bad) by size={counts} obstructions={len(failed)} '
              f'by_size={sorted(Counter(map(len, failed)).items())} types={len(representatives)} '
              f'generated_cpu={time.process_time()-start:.3f}', flush=True)
        for masks in sorted(representatives):
            assert not brute(width, masks)
            assert all(local_completion(width, masks[:idx] + masks[idx + 1:]) for idx in range(len(masks)))
        reports[str(width)] = failed
        print(f'T={width} verified_cpu={time.process_time()-start:.3f}', flush=True)
    if args.verify:
        assert json.loads(args.output.read_text()) == json.loads(json.dumps(reports))
    else:
        args.output.write_text(json.dumps(reports, separators=(',', ':')) + '\n')


if __name__ == '__main__':
    main()
