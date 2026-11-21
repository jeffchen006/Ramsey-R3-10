#!/usr/bin/env python3
"""Independently test all root-local cap decisions on the order-20 control."""

from itertools import combinations
from pathlib import Path
import sys
from types import SimpleNamespace

from kernel_projection import bits
from q22_root import append_q22, check_pair_formula, exact_square_counts, isolated_edges

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
from check_graph import brute_alpha, triangle_free


def sparse_control():
    order, degree = 20, 6
    graph = [sum(1 << ((vertex + step) % order) for step in (-6, -5, -2, 2, 5, 6)) for vertex in range(order)]
    assert triangle_free(graph) and brute_alpha(graph) == degree
    cdeg = {(first, second): (graph[first] & graph[second]).bit_count()
            for first, second in combinations(range(order), 2) if not graph[first] >> second & 1}
    assert set(cdeg.values()) == {2, 3}
    edges = {(first, second): 0 for first, second in combinations(range(order), 2) if graph[first] >> second & 1}
    for block in combinations(range(order), 4):
        local = list(combinations(block, 2))
        diagonal = [pair for pair in local if pair in cdeg]
        if len(diagonal) == 2 and not set(diagonal[0]) & set(diagonal[1]) and all(cdeg[pair] == 2 for pair in diagonal):
            for pair in local:
                if pair not in cdeg:
                    edges[pair] += 1
    assert edges == exact_square_counts(graph)

    feedback = [0, 0]
    for first, second in edges:
        left = tuple(bits(graph[first] ^ (1 << second)))
        right = tuple(bits(graph[second] ^ (1 << first)))
        boundary = left + right
        outside = set(range(order)) - set(boundary) - {first, second}
        kernel = [sum((graph[vertex] >> other & 1) << index for index, other in enumerate(boundary))
                  for vertex in boundary]
        signatures = [sum((graph[vertex] >> other & 1) << index for index, other in enumerate(boundary))
                      for vertex in outside]
        assert len(set(signatures)) == len(outside)
        assert isolated_edges(kernel) == edges[first, second]
        true_cap = max(edges[tuple(sorted((root, anchor)))] for root, anchors in ((first, left), (second, right))
                       for anchor in anchors)
        for cap in range(max(edges.values()) + 1):
            model = SimpleNamespace(p={mask: col for col, mask in enumerate(signatures)}, rows=[])
            append_q22(model, kernel, degree, cap)
            passed = all(sum(coeff for _, coeff in terms) <= rhs for terms, rhs, _ in model.rows)
            assert passed == (cap >= true_cap), (first, second, cap, true_cap)
            feedback[passed] += 1
    return len(edges), feedback


if __name__ == '__main__':
    check_pair_formula()
    edges, (rejected, kept) = sparse_control()
    print(f'PASS exact local pair rows and {edges} mixed-codegree C20 roots: '
          f'{kept} retained / {rejected} rejected cap decisions agree with direct square census')
