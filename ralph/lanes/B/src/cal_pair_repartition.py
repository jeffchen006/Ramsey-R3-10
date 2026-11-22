#!/usr/bin/env python3
from collections import Counter
from itertools import combinations, product
import subprocess
import sys

from critical_witness import parse_graph6


def edge_set(graph):
    return frozenset((tail, head) for tail, head in combinations(range(len(graph)), 2)
                     if graph[tail] & (1 << head))


def oracle(graph, alpha, increment, expand):
    vertices = set(range(len(graph)))
    edges = edge_set(graph)
    triangles = [set(combinations(group, 2)) for group in combinations(sorted(vertices), 3)]
    independent = [set(combinations(group, 2)) for group in combinations(sorted(vertices), alpha+1)]
    result = Counter()
    for left, right in combinations(sorted(vertices), 2):
        if (left, right) in edges:
            continue
        pair = {left, right}
        stem = {edge for edge in edges if pair.isdisjoint(edge)}
        old_union = {next(vertex for vertex in edge if vertex not in pair)
                     for edge in edges if not pair.isdisjoint(edge)}
        unions = [old_union]
        if expand:
            unions.extend(old_union | {vertex} for vertex in vertices - pair - old_union)
        for union in unions:
            for colors in product((1, 2, 3), repeat=len(union)):
                if len(stem) + len(union) + colors.count(3) != len(edges) + increment:
                    continue
                candidate = set(stem)
                for vertex, color in zip(sorted(union), colors):
                    for mask, root in ((1, left), (2, right)):
                        if color & mask:
                            candidate.add(tuple(sorted((vertex, root))))
                if any(triangle <= candidate for triangle in triangles):
                    continue
                private = [support & candidate for support in independent]
                if any(not support for support in private):
                    continue
                if set().union(*(support for support in private if len(support) == 1)) == candidate:
                    result[frozenset(candidate)] += 1
    return result


def main():
    generator = sys.argv[1] if len(sys.argv) > 1 else 'build/pair_repartition'
    geng = subprocess.run(['timeout', '10s', '../../opt/bin/geng', '-q', '-t', '8'],
                          text=True, capture_output=True, check=True)
    controls = [row for row in geng.stdout.splitlines()
                if all(any(set(edge) <= set(group) for edge in edge_set(parse_graph6(row)))
                       for group in combinations(range(8), 4))]
    assert len(controls) == 3, len(controls)
    total = 0
    for row in controls:
        for increment, expand in product(range(2), repeat=2):
            run = subprocess.run(['timeout', '5s', generator, '3', str(increment), str(expand)],
                                 input=row+'\n', text=True, capture_output=True, check=True)
            actual = Counter(edge_set(parse_graph6(candidate)) for candidate in run.stdout.splitlines())
            expected = oracle(parse_graph6(row), 3, increment, expand)
            assert actual == expected, (row, increment, expand, actual-expected, expected-actual)
            total += actual.total()
    assert total > 0
    print(f'PASS all 3 order-8 (3,4) classes x 4 policies; {total} labeled emissions matched')


if __name__ == '__main__':
    main()
