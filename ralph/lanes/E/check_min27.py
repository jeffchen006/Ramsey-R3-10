#!/usr/bin/env python3
"""Look for the order-32 fixed set equality pattern in the four min-edge graphs."""
from itertools import combinations
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
from check_graph import alpha, parse_graph6, triangle_free


def pattern_count(graph, degree):
    eligible = [vertex for vertex, row in enumerate(graph) if row.bit_count() == degree]
    edges = [(left, right) for left, right in combinations(eligible, 2) if graph[left] >> right & 1]
    matchings = subsets = patterns = 0
    for pair, other in combinations(edges, 2):
        ends = pair + other
        if len(set(ends)) != 4 or any(graph[left] >> right & 1 for left in pair for right in other):
            continue
        matchings += 1
        nonneighbors = [vertex for vertex in range(len(graph)) if vertex not in ends and
                        not any(graph[end] >> vertex & 1 for end in ends)]
        for core in combinations(nonneighbors, 8):
            subsets += 1
            if all(any(graph[left] >> right & 1 for left, right in combinations(quad, 2))
                   for quad in combinations(core, 4)):
                patterns += 1
    return matchings, subsets, patterns


def isolate_partitions(graph):
    degree_seven = [vertex for vertex, row in enumerate(graph) if row.bit_count() == 7]
    patterns = partitions = 0
    for ends in combinations(degree_seven, 3):
        edges = [(left, right) for left, right in combinations(ends, 2) if graph[left] >> right & 1]
        if len(edges) != 1:
            continue
        pair = edges[0]
        isolate = next(vertex for vertex in ends if vertex not in pair)
        nonneighbors = [vertex for vertex in range(len(graph)) if vertex not in ends and
                        not any(graph[end] >> vertex & 1 for end in ends)]
        for core in combinations(nonneighbors, 8):
            if not all(any(graph[left] >> right & 1 for left, right in combinations(quad, 2))
                       for quad in combinations(core, 4)):
                continue
            patterns += 1
            rest = [vertex for vertex in range(len(graph)) if vertex not in core and vertex not in ends]
            full = sum(1 << vertex for vertex in rest)
            groups = {5: set(), 6: set()}
            for width in (5, 6):
                for subset in combinations(rest, width):
                    mask = sum(1 << vertex for vertex in subset)
                    if ((graph[isolate] & mask).bit_count() in (2, 3)
                            and all((graph[vertex] & mask).bit_count() == 2 for vertex in pair)
                            and all(not (graph[vertex] & mask) for vertex in subset)):
                        groups[width].add(mask)
            partitions += sum(1 for first, second in combinations(sorted(groups[5]), 2)
                              if not first & second and (full ^ first ^ second) in groups[6])
    return patterns, partitions


def main():
    wagner = [sum(1 << ((vertex + step) % 8) for step in (1, 4, 7)) for vertex in range(8)]
    positive = wagner + [1 << 9, 1 << 8, 1 << 11, 1 << 10]
    negative = [row for row in positive[:-1]]
    negative[10] = 0
    if (not triangle_free(positive) or alpha(positive) != 5 or
            pattern_count(positive, 1) != (1, 1, 1) or pattern_count(negative, 1)[2]):
        sys.exit('positive/negative controls failed')
    print('Wagner + 2K2 positive control: (1 matching, 1 candidate core, 1 match); deletion control negative')
    graph = wagner + [1 << 9, 1 << 8] + [0] * 17
    for group, isolate_degree in zip((range(11,16), range(16,21), range(21,27)), (2, 2, 3)):
        for origin, targets in ((8, group[:2]), (9, group[2:4]), (10, group[:isolate_degree])):
            for vertex in targets:
                graph[origin] |= 1 << vertex
                graph[vertex] |= 1 << origin
    if not triangle_free(graph) or not isolate_partitions(graph)[1]:
        sys.exit('synthetic partition control failed')
    graph[8] ^= 1 << 11
    graph[11] ^= 1 << 8
    if isolate_partitions(graph)[1]:
        sys.exit('synthetic deletion control failed')
    print('Synthetic isolate-partition control passes; edge-deletion control fails as expected')
    graphs = Path(sys.argv[1]).read_text().splitlines()
    if len(set(graphs)) != 4 or len(graphs) != 4:
        sys.exit('expected four distinct graph6 representatives')
    for index, line in enumerate(graphs, 1):
        graph = parse_graph6(line)
        if (len(graph) != 27 or sum(row.bit_count() for row in graph) != 170
                or not triangle_free(graph) or alpha(graph) != 7):
            sys.exit(f'bad representative #{index}')
        matchings, subsets, patterns = pattern_count(graph, 7)
        print(f'H#{index}: induced 2K2={matchings}, anticomplete 8-sets={subsets}, passing alpha test={patterns}')
        if patterns:
            sys.exit('necessary pattern found')
        isolate_patterns, partitions = isolate_partitions(graph)
        print(f'H#{index}: induced K2+K1 with anticomplete alpha<=3 core={isolate_patterns}, partitions={partitions}')
        if partitions:
            sys.exit('isolate partition found')
    print('RESULT: no equality pattern in any minimum graph')


if __name__ == '__main__':
    main()
