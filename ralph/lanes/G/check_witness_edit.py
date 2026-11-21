#!/usr/bin/env python3
"""Exact small labelled control for the cached edge-edit enumerator."""

from itertools import combinations
from pathlib import Path
import subprocess
import sys

from check_root_cover import graph


def edges(rows):
    return frozenset((left, right) for left, right in combinations(range(len(rows)), 2)
                     if rows[left] & (1 << right))


def direct(order, edge_set, alpha, floor, remove_count, add_count):
    universe = set(combinations(range(order), 2))
    triples = [set(combinations(tips, 2)) for tips in combinations(range(order), 3)]
    forbidden = [set(combinations(tips, 2)) for tips in combinations(range(order), alpha + 1)]
    for removed in combinations(sorted(edge_set), remove_count):
        base = edge_set.difference(removed)
        for added in combinations(sorted(universe - edge_set), add_count):
            out = base.union(added)
            if any(triangle <= out for triangle in triples) or any(not (independent & out) for independent in forbidden):
                continue
            degree = [0] * order
            for left, right in out:
                degree[left] += 1
                degree[right] += 1
            if min(degree) >= floor:
                yield out


def main():
    binary = Path(sys.argv[1]).resolve()
    lines = Path(sys.argv[2]).read_text().splitlines()
    for source in lines:
        rows = graph.parse_graph6(source)
        assert len(rows) == 8 and graph.alpha(rows) == 3
        for floor in (0, 2):
            for remove_count in (1, 2, 3):
                for add_count in ((1, 2, 3, 4) if remove_count == 3 else (1, 2, 3)):
                    call = subprocess.run([binary, '3', str(floor), str(remove_count), str(add_count)],
                                          input=source + '\n', check=True, capture_output=True, text=True)
                    output = [edges(graph.parse_graph6(line)) for line in call.stdout.splitlines()]
                    expected = set(direct(len(rows), edges(rows), 3, floor, remove_count, add_count))
                    assert len(output) == len(set(output)) and set(output) == expected
                    print(f'{source} floor={floor} {remove_count}->{add_count}: exact {len(expected)}')


if __name__ == '__main__':
    main()
