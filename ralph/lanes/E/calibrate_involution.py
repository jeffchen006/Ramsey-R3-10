#!/usr/bin/env python3
"""Small exact controls for the large-fixed-set argument."""
from itertools import combinations, product
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
from check_graph import brute_alpha, triangle_free


def induced(graph, vertices):
    vertices = sorted(vertices)
    return [sum(1 << index for index, right in enumerate(vertices) if graph[left] >> right & 1)
            for left in vertices]


def edges(graph):
    return sum(row.bit_count() for row in graph) // 2


def main():
    vertices = list(map(frozenset, combinations(range(5), 2)))
    graph = [sum(1 << index for index, right in enumerate(vertices) if not left & right)
             for left in vertices]
    perm = [vertices.index(frozenset(1-item if item < 2 else item for item in vertex)) for vertex in vertices]
    fixed = {item for item, image in enumerate(perm) if item == image}
    pairs = [(item, image) for item, image in enumerate(perm) if item < image]
    assert triangle_free(graph) and brute_alpha(graph) == 4
    assert len(fixed) == 4 and len(pairs) == 3
    assert all(graph[left] >> right & 1 == graph[perm[left]] >> perm[right] & 1
               for left, right in combinations(range(10), 2))
    moved = set(range(10)) - fixed
    assert all(row.bit_count() == 2 for row in induced(graph, moved))
    groups = [{item for item in fixed if graph[left] >> item & 1} for left, _ in pairs]
    assert [len(group) for group in groups] == [1, 1, 1]
    outside = fixed.difference(*groups)
    subgraphs = [induced(graph, fixed - group) for group in groups]
    assert all(brute_alpha(subgraph) == 2 and triangle_free(subgraph) for subgraph in subgraphs)
    fixed_edges = edges(induced(graph, fixed))
    fixed_degrees = sum(sum(graph[item] >> other & 1 for other in fixed) for item in outside)
    assert sum(map(edges, subgraphs)) == fixed_edges + fixed_degrees == 6
    assert edges(graph) == fixed_edges + 6 + 6 == 15
    print('Petersen: triangle-free, alpha=4; k=3 f=4; e_F=3, sum d_F(W)=3, sum e(H_i)=6')

    for count in range(3, 7):
        matchings = list(combinations(range(count), 2))
        good = 0
        for pattern in product(range(2), repeat=len(matchings)):
            graph = [0] * (2 * count)
            for (left, right), sign in zip(matchings, pattern):
                for bit in range(2):
                    first, second = 2*left + bit, 2*right + (bit ^ sign)
                    graph[first] |= 1 << second
                    graph[second] |= 1 << first
            if triangle_free(graph):
                phase = [0] + [1 ^ pattern[index] for index in range(count - 1)]
                assert all(sign ^ phase[left] ^ phase[right] == 1
                           for (left, right), sign in zip(matchings, pattern))
                assert brute_alpha(graph) == count
                good += 1
        assert good == 2**(count - 1)
        print(f'k={count}: {good}/{2**len(matchings)} triangle-free phase patterns, all crown')


if __name__ == '__main__':
    main()
