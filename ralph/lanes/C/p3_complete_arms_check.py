"""Calibrate the complete-arm antineighbour argument on smaller graphs."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path

from kernel_projection import bits, decode
from p3_high_f import NO_HOLE, classify
from p3_round4_index import has_independent


def independence(graph, vertices):
    return next(size for size in range(vertices.bit_count(), -1, -1)
                if has_independent(graph, vertices, size))


def touch(graph, vertices):
    result = 0
    for vertex in bits(vertices):
        result |= graph[vertex]
    return result


def inspect(graph, degree):
    all_vertices = (1 << len(graph)) - 1
    assert all(row.bit_count() <= degree for row in graph)
    assert all(not graph[first] & graph[second] for first, second in combinations(range(len(graph)), 2)
               if graph[first] >> second & 1)
    assert not has_independent(graph, all_vertices, degree + 1)
    counts = Counter()
    for triple in combinations(range(len(graph)), 3):
        if any(graph[first] >> second & 1 for first, second in combinations(triple, 2)):
            continue
        if any(graph[root].bit_count() != degree for root in triple):
            continue
        counts['independent_triples'] += 1
        for middle in triple:
            left, right = (root for root in triple if root != middle)
            left_nb, centre_nb, right_nb = graph[left], graph[middle], graph[right]
            common = left_nb & right_nb
            if common & ~centre_nb:
                continue
            wing_left = left_nb & ~centre_nb
            wing_right = right_nb & ~centre_nb
            if not (wing_left and wing_right and common):
                continue
            counts['partitioned'] += 1
            if not all(graph[vertex] & (centre_nb & ~left_nb) == (centre_nb & ~left_nb)
                       for vertex in bits(wing_left)):
                continue
            if not all(graph[vertex] & (centre_nb & ~right_nb) == (centre_nb & ~right_nb)
                       for vertex in bits(wing_right)):
                continue
            roots = sum(1 << root for root in triple)
            exterior = all_vertices & ~(left_nb | centre_nb | right_nb | roots)
            deficient = exterior & ~touch(graph, common)
            wings = wing_left | wing_right
            assert not touch(graph, deficient) & (common | wings)
            assert deficient.bit_count() >= exterior.bit_count() - (degree - 3) * common.bit_count()
            assert independence(graph, deficient) + independence(graph, wings) + common.bit_count() <= degree
            wing_edges = sum((graph[vertex] & wing_right).bit_count() for vertex in bits(wing_left))
            counts['complete_arms'] += 1
            counts[f'complete_arms_b{wing_edges}_D{deficient.bit_count()}'] += 1
    return counts


def synthetic():
    for wing_edges, neighbours in ((0, (2,)), (1, (4, 5))):
        graph = classify(4, 3, 2, (wing_edges, NO_HOLE, NO_HOLE))
        exterior = len(graph)
        graph.append(sum(1 << vertex for vertex in neighbours))
        for vertex in neighbours:
            graph[vertex] |= 1 << exterior
        counts = inspect(graph, 4)
        assert counts[f'complete_arms_b{wing_edges}_D{wing_edges}'] >= 1
        for vertex in neighbours:
            graph[vertex] ^= 1 << exterior
        graph[exterior] = 0
        assert has_independent(graph, (1 << len(graph)) - 1, 5)
        print('PASS max-degree-four planted b', wing_edges, 'and alpha corruption', dict(counts))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogues', nargs='+', type=Path)
    args = parser.parse_args()
    synthetic()
    circulant = [sum(1 << ((vertex + sign * step) % 35) for sign in (-1, 1) for step in (1, 7, 11, 16))
                 for vertex in range(35)]
    print('PASS C35', dict(inspect(circulant, 8)))
    for catalogue in args.catalogues:
        counts = Counter()
        for line in catalogue.read_text().splitlines():
            counts += inspect(decode(line), 6)
        print('PASS', catalogue, dict(counts))


if __name__ == '__main__':
    main()
