#!/usr/bin/env python3
from collections import Counter
from itertools import combinations, combinations_with_replacement
import subprocess
import sys

from cal_pair_repartition import edge_set
from critical_root_cards import encode
from critical_witness import parse_graph6


def direct(rows, bound, minimum, size):
    order = len(rows)
    edges = edge_set(rows)
    triangles = [set(combinations(group, 2)) for group in combinations(range(order+2), 3)]
    independent = [set(combinations(group, 2)) for group in combinations(range(order+2), bound+1)]
    attachments = [combo for length in range(minimum, bound+1)
                   for combo in combinations(range(order), length)]
    for first, second in combinations_with_replacement(attachments, 2):
        if len(edges)+len(first)+len(second) != size:
            continue
        candidate = edges | {(vertex, order) for vertex in first} | {(vertex, order+1) for vertex in second}
        if any(sum(vertex in edge for edge in candidate) < minimum for vertex in range(order+2)):
            continue
        if any(triangle <= candidate for triangle in triangles):
            continue
        private = [support & candidate for support in independent]
        if any(not support for support in private):
            continue
        if set().union(*(support for support in private if len(support) == 1)) == candidate:
            yield frozenset(candidate)


def incidence(order, edges):
    return [sum(1 << other for other in range(order) if tuple(sorted((vertex, other))) in edges)
            for vertex in range(order)]


def main():
    builder, lift = sys.argv[1:]
    small_hosts = subprocess.run(['timeout', '10s', '../../opt/bin/geng', '-q', '-t', '8'],
                                 text=True, capture_output=True, check=True)
    controls = [row for row in small_hosts.stdout.splitlines()
                if all(any(set(edge) <= set(group) for edge in edge_set(parse_graph6(row)))
                       for group in combinations(range(8), 4))]
    assert len(controls) == 3
    unique = set()
    for control in controls:
        host = parse_graph6(control)
        expected = Counter()
        for left, right in combinations(range(8), 2):
            if host[left] & (1 << right):
                continue
            keep = sorted(set(range(8)) - {left, right})
            edges = {(tail, head) for tail, head in combinations(range(6), 2)
                     if host[keep[tail]] & (1 << keep[head])}
            expected[encode(incidence(6, edges))] += 1
        actual = subprocess.run(['timeout', '5s', builder, '0', '20'], input=control+'\n',
                                text=True, capture_output=True, check=True)
        assert Counter(actual.stdout.splitlines()) == expected
        unique |= set(expected)
    comparisons, positives = 0, 0

    def normalized(graph):
        swapped = frozenset(tuple(sorted(13-vertex if vertex >= 6 else vertex for vertex in edge))
                            for edge in graph)
        return min(tuple(sorted(graph)), tuple(sorted(swapped)))

    for row in sorted(unique):
        stem = parse_graph6(row)
        for size in (10, 11, 12):
            for minimum in (0, 2, 3):
                expected = {frozenset(candidate) for candidate in direct(stem, 3, minimum, size)}
                actual = subprocess.run(['timeout', '5s', lift, '3', str(minimum), str(size)],
                                        input=row+'\n', text=True, capture_output=True, check=True)
                observed = [normalized(edge_set(parse_graph6(candidate))) for candidate in actual.stdout.splitlines()]
                standardized = set(observed)
                assert len(standardized) == len(observed)
                other = {normalized(graph) for graph in expected}
                assert standardized == other, (row, size, minimum, standardized ^ other)
                comparisons += 1
                positives += len(standardized)
    assert comparisons and positives
    print(f'PASS labelled deletion for 3 exact hosts; {comparisons} lift comparisons, {positives} outputs')


if __name__ == '__main__':
    main()
