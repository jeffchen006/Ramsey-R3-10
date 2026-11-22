#!/usr/bin/env python3
"""Project the complete order-27 marked source, only for extendible windows."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path

from audit_floor_covers import require
from audit_path_leaf import vertices
from audit_strip_extensions import colored_key, independent, mark, validate_graph
from residue_bundle import parse_graph6


def projected(adj, removed):
    kept = tuple(vertex for vertex in range(len(adj)) if vertex not in removed)
    relabel = {vertex: index for index, vertex in enumerate(kept)}
    cut = sum(1 << vertex for vertex in removed)
    reduced = tuple(sum(1 << relabel[peer] for peer in vertices(adj[vertex] & ~cut)) for vertex in kept)
    return reduced, relabel


def legal_mark(adj, sides, private):
    first, second = [sum(1 << vertex for vertex in side) for side in sides]
    if first & second or any(adj[vertex] & mask for mask, side in zip((first, second), sides) for vertex in side):
        return False
    if sum((adj[vertex] & second).bit_count() for vertex in sides[0]) != 1:
        return False
    outside = tuple(vertices(((1 << len(adj))-1) ^ first ^ second))
    for mask in (first, second):
        contact = Counter(adj[vertex] & mask for vertex in outside)
        if any(not 1 <= hit.bit_count() <= 2 or count > (private if hit.bit_count() == 1 else 1)
               for hit, count in contact.items()):
            return False
    return True


def mark_small(adj, alpha):
    if next(independent(adj, alpha+1), None) is not None:
        return
    pairs = tuple(independent(adj, 2))
    for first, second in combinations(pairs, 2):
        if legal_mark(adj, (first, second), 2):
            yield first, second


def extend_small(adj, sides, alpha):
    observed = tuple(sum(1 << vertex for vertex in item) for item in independent(adj, alpha))
    order = len(adj)
    for size in range(2, alpha+1):
        for support in independent(adj, size):
            mask = sum(1 << vertex for vertex in support)
            if not all(mask & other for other in observed):
                continue
            extension = tuple(ns | (1 << order) if mask >> vertex & 1 else ns for vertex, ns in enumerate(adj)) + (mask,)
            if legal_mark(extension, sides, 2):
                return True
    return False


def control(lower, upper):
    positives, misses, downward = set(), set(), set()
    require(len(lower.read_text().splitlines()) == 107 and len(upper.read_text().splitlines()) == 410,
            'unexpected order-seven or order-eight census count')
    for row in lower.read_text().splitlines():
        adj = tuple(parse_graph6(row))
        for sides in mark_small(adj, 4):
            target = positives if extend_small(adj, sides, 4) else misses
            target.add(colored_key(adj, sides))
    for row in upper.read_text().splitlines():
        adj = tuple(parse_graph6(row))
        for sides in mark_small(adj, 4):
            exterior = set(range(len(adj))) - set().union(*map(set, sides))
            for vertex in exterior:
                reduced, relabel = projected(adj, (vertex,))
                downward.add(colored_key(reduced, tuple(tuple(relabel[anchor] for anchor in side) for side in sides)))
    require(downward == positives and not (downward & misses), 'marked projection disagrees with direct addback')
    require(positives and misses, 'both smaller projection controls are required')
    print(f'smaller exact control: {len(positives)} extension-positive marks, {len(misses)} negatives', flush=True)


def study(keys, lower, deleted, out):
    targets = {}
    for row in lower.read_text().splitlines():
        _, first, second, encoded = row.split()
        adj = validate_graph(encoded)
        sides, _, _ = mark(adj, int(first), int(second))
        key = colored_key(adj, sides)
        require(key not in targets, 'target list repeated a marked orbit')
        targets[key] = row
    coverage = Counter()
    hit = set()
    all_projected = set()
    for row in keys.read_text().splitlines():
        _, first, second, encoded = row.split()
        adj = validate_graph(encoded)
        sides, _, _ = mark(adj, int(first), int(second))
        exterior = tuple(vertices(((1 << len(adj))-1) ^ int(first) ^ int(second)))
        for removed in combinations(exterior, deleted):
            reduced, relabel = projected(adj, removed)
            local_sides = tuple(tuple(relabel[anchor] for anchor in side) for side in sides)
            lower_degree = min(neighbors.bit_count() for neighbors in reduced)
            key = colored_key(reduced, local_sides)
            if key not in all_projected:
                all_projected.add(key)
                coverage[lower_degree] += 1
            if key in targets:
                hit.add(key)
    out.write_text(''.join(f'{targets[key]}\n' for key in sorted(hit)))
    print(f'deleted={deleted} {len(all_projected)} projection orbits by degree={dict(sorted(coverage.items()))}; '
          f'{len(hit)} of {len(targets)} independent lower orbits hit', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('small_lower', type=Path)
    parser.add_argument('small_upper', type=Path)
    parser.add_argument('--study', nargs=4)
    args = parser.parse_args()
    control(args.small_lower, args.small_upper)
    if args.study:
        keys, lower, deleted, output = args.study
        study(Path(keys), Path(lower), int(deleted), Path(output))


if __name__ == '__main__':
    main()
