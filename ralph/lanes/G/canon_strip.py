#!/usr/bin/env python3
"""Collapse marked cores modulo ordinary isomorphism and side exchange."""

from argparse import ArgumentParser
from pathlib import Path

import pynauty
from check_root_cover import graph, vertices


def validate(adj, first, second):
    assert first.bit_count() == second.bit_count() == 4 and first < second and not first & second
    assert not any(adj[vertex] & side for side in (first, second) for vertex in vertices(side))
    assert sum((adj[vertex] & second).bit_count() for vertex in vertices(first)) == 1
    universe = (1 << len(adj)) - 1
    exterior = tuple(vertices(universe ^ first ^ second))
    for side in (first, second):
        signature = {}
        for vertex in exterior:
            support = adj[vertex] & side
            length = support.bit_count()
            signature[support] = signature.get(support, 0) + 1
            assert length in (1, 2) and signature[support] <= (4 if length == 1 else 1)
    assert graph.triangle_free(adj) and graph.alpha(adj) == 7
    return exterior


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('keys', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    reps = {}
    with args.output.open('w') as out, args.keys.open() as source:
        for line in source:
            _, first_text, second_text, encoded = line.split()
            first, second = int(first_text), int(second_text)
            adj = graph.parse_graph6(encoded)
            exterior = validate(adj, first, second)
            ordinary = {vertex: list(vertices(neighbors)) for vertex, neighbors in enumerate(adj)}
            colors = (set(vertices(first)), set(vertices(second)), set(exterior))
            key = min(pynauty.certificate(pynauty.Graph(len(adj), adjacency_dict=ordinary, vertex_coloring=partition))
                      for partition in (list(colors), [colors[1], colors[0], colors[2]]))
            reps.setdefault(key, line)
        out.writelines(reps.values())
    print(f'{len(reps)} side-swap-coloured keys')


if __name__ == '__main__':
    main()
