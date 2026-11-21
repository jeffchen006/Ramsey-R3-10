"""Exact isolated-pair checks on the known regular 22-vertex census."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path

from kernel_projection import bits, decode
from path_four_factor import independent_sets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('census', type=Path)
    args = parser.parse_args()
    lines = args.census.read_text().splitlines()
    assert len(set(lines)) == len(lines) == 10
    counts, nonisolated_failures = Counter(), []
    for row, line in enumerate(lines):
        graph = decode(line)
        order, degree = len(graph), 6
        assert order == 22 and all(mask.bit_count() == degree for mask in graph)
        assert all(not graph[first] & graph[second] for first, second in combinations(range(order), 2)
                   if graph[first] >> second & 1)
        assert max(group.bit_count() for group in independent_sets(graph, (1 << order) - 1)) == degree
        codegrees = {(first, second): (graph[first] & graph[second]).bit_count()
                     for first, second in combinations(range(order), 2)}
        cap = max(codegrees.values())
        partners = Counter(vertex for pair, count in codegrees.items() if count == cap for vertex in pair)
        for (first, second), count in codegrees.items():
            if count != cap:
                continue
            shared = graph[first] & graph[second]
            wing_first, wing_second = graph[first] ^ shared, graph[second] ^ shared
            wing_size = degree - cap
            residue = ((1 << order) - 1) & ~(graph[first] | graph[second] | 1 << first | 1 << second)
            missing = [(left, right) for left in bits(wing_first) for right in bits(wing_second)
                       if not graph[left] >> right & 1]
            if len(missing) > 1:
                continue
            residue_degrees = {vertex: (graph[vertex] & residue).bit_count() for vertex in bits(residue)}
            if partners[first] != 1 or partners[second] != 1:
                if not missing and min(residue_degrees.values()) <= wing_size:
                    nonisolated_failures.append((row, first, second))
                continue
            low = {vertex for vertex, val in residue_degrees.items() if val == wing_size}
            off_common = {vertex for vertex in bits(residue) if not graph[vertex] & shared}
            for vertex, val in residue_degrees.items():
                assert (graph[vertex] & wing_first).bit_count() >= wing_size + 1 - val
                assert (graph[vertex] & wing_second).bit_count() >= wing_size + 1 - val
            if not missing:
                assert not low and not off_common and min(residue_degrees.values()) > wing_size
            else:
                left, right = missing[0]
                assert min(residue_degrees.values()) >= wing_size
                assert not low & off_common
                assert all(graph[left] >> vertex & graph[right] >> vertex & 1 for vertex in low | off_common)
                assert all((graph[vertex] & shared).bit_count() == cap - 2 for vertex in low)
                assert len(low) + len(off_common) <= cap
                assert (cap - 2) * len(low) <= cap * (degree - 1) - residue.bit_count()
            print('CONTROL', row, first, second, 'cap', cap, 'missing', len(missing),
                  'min-degree', min(residue_degrees.values()), 'D', len(low), 'U', len(off_common))
            counts[(cap, len(missing))] += 1
    assert counts == {(4, 0): 7, (4, 1): 4}
    print('all isolated pairs checked', dict(counts), 'nonisolated complete-wing negative examples', nonisolated_failures)


if __name__ == '__main__':
    main()
