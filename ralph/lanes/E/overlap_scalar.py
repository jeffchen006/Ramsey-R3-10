#!/usr/bin/env python3
"""Audit the f=28 overlap bound by split-first and root-first enumeration."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path


def decode(line):
    order = ord(line[0]) - 63
    encoded = ''.join(f'{ord(character) - 63:06b}' for character in line[1:])
    assert len(encoded) == ((order * (order - 1) // 2 + 5) // 6) * 6
    edges = [(left, right) for right in range(order) for left in range(right)]
    assert not any(character == '1' for character in encoded[len(edges):])
    adj = [set() for _ in range(order)]
    for (left, right), character in zip(edges, encoded):
        if character == '1':
            adj[left].add(right)
            adj[right].add(left)
    return adj


def independent(adj, vertices):
    return all(right not in adj[left] for left, right in combinations(vertices, 2))


def split_first(adj, part_size):
    universe = set(range(len(adj)))
    independent_sets = [set(part) for part in combinations(range(len(adj)), part_size) if independent(adj, part)]
    histogram = Counter()
    for first, second in combinations(independent_sets, 2):
        if first & second:
            continue
        block = first | second
        for root in universe - block:
            if adj[root] & block:
                continue
            core = universe - block - {root}
            internal = sum(len(adj[vertex] & core) for vertex in core)
            cross = sum(len(adj[vertex] & block) for vertex in core)
            root_degree = len(adj[root] & core)
            histogram[internal + 2 * cross + 4 * root_degree] += 1
    return histogram


def balanced_splits(adj, block, part_size):
    choices = Counter({0: 1})
    unseen = set(block)
    color = {}
    while unseen:
        source = unseen.pop()
        color[source] = 0
        pending = [source]
        sizes = [1, 0]
        while pending:
            vertex = pending.pop()
            for neighbor in adj[vertex].intersection(block):
                if neighbor in color:
                    if color[neighbor] == color[vertex]:
                        return 0
                else:
                    color[neighbor] = 1 - color[vertex]
                    sizes[color[neighbor]] += 1
                    unseen.remove(neighbor)
                    pending.append(neighbor)
        extended = Counter()
        for used, multiplicity in choices.items():
            for size in sizes:
                if used + size <= part_size:
                    extended[used + size] += multiplicity
        choices = extended
    assert choices[part_size] % 2 == 0
    return choices[part_size] // 2


def root_first(adj, part_size):
    universe = set(range(len(adj)))
    edge_count = sum(map(len, adj)) // 2
    histogram = Counter()
    for root, neighborhood in enumerate(adj):
        for vertices in combinations(sorted(universe - neighborhood - {root}), 2 * part_size):
            block = set(vertices)
            multiplicity = balanced_splits(adj, block, part_size)
            if not multiplicity:
                continue
            block_edges = sum(len(adj[vertex] & block) for vertex in block) // 2
            histogram[2 * (edge_count - block_edges + len(neighborhood))] += multiplicity
    return histogram


def calibrate():
    cycle = [{(vertex + 1) % 5, (vertex - 1) % 5} for vertex in range(5)]
    assert split_first(cycle, 1) == root_first(cycle, 1) == {12: 5}
    pairs = tuple(map(set, combinations(range(5), 2)))
    petersen = [{other for other, rhs in enumerate(pairs) if not lhs & rhs} for lhs in pairs]
    observed = split_first(petersen, 2)
    assert observed == root_first(petersen, 2) == {30: 60, 32: 120}
    print(f'CAL C5 rows=5 min=12; Petersen rows={sum(observed.values())} distribution={sorted(observed.items())}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    args = parser.parse_args()
    calibrate()
    lines = args.catalogue.read_text(encoding='ascii').splitlines()
    assert len(lines) == len(set(lines)) == 7
    lowest = float('inf')
    total = 0
    for number, line in enumerate(lines, 1):
        adj = decode(line)
        assert len(adj) == 17
        assert not any(adj[left] & adj[right] for left in range(len(adj)) for right in adj[left])
        assert not any(independent(adj, chosen) for chosen in combinations(range(len(adj)), 6))
        split = split_first(adj, 4)
        assert split == root_first(adj, 4)
        rows = sum(split.values())
        minimum = min(split)
        lowest = min(lowest, minimum)
        total += rows
        print(f'GRAPH {number} e={sum(map(len, adj)) // 2} layouts={rows} min={minimum} histogram={sorted(split.items())}')
    assert total == 7057 and lowest == 66
    print(f'PASS {total} layouts, minimum {lowest} > 62')


if __name__ == '__main__':
    main()
