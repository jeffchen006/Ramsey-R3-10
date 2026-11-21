#!/usr/bin/env python3
"""Independent subset replay of the 12-vertex balanced-class calibration."""

from itertools import combinations
from pathlib import Path
import sys

import networkx as nx


def masks(group):
    return sum(1 << vertex for vertex in group)


def check(catalogue, output):
    rows = output.read_text().splitlines()
    reported = {tuple(map(int, row.split('\t')[:4])) for row in rows}
    expected = set()
    balanced = 0
    for index, line in enumerate(catalogue.read_bytes().splitlines()):
        graph = nx.from_graph6_bytes(line)
        assert len(graph) == 12
        universe = set(graph)

        def independent(group):
            return all(not graph.has_edge(first, second) for first, second in combinations(group, 2))

        assert not any(independent(group) for group in combinations(universe, 5))
        has_partition = False
        for points in combinations(universe - {0}, 3):
            first = {0, *points}
            if not independent(first):
                continue
            rest = universe - first
            pivot = min(rest)
            for choices in combinations(rest - {pivot}, 3):
                second = {pivot, *choices}
                third = rest - second
                if not (independent(second) and independent(third)):
                    continue
                has_partition = True
                if max(dict(graph.degree).values()) > 8:
                    continue
                if any(len(set(graph[left]) & set(graph[right])) > 4 for left, right in combinations(universe, 2)):
                    continue
                if any(len(set(graph[left]) & set(graph[right])) > 3 for group in (first, second, third)
                       for left, right in combinations(group, 2)):
                    continue
                expected.add((index, masks(first), masks(second), masks(third)))
        balanced += has_partition
    assert expected == reported and len(expected) == len(rows) == 30 and balanced == 11
    print(f'PASS exact partitions: {len(expected)} viable partitions; {balanced} balanced graphs')


if __name__ == '__main__':
    check(*map(Path, sys.argv[1:]))
