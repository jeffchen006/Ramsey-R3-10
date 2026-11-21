#!/usr/bin/env python3
"""Independent hereditary census for triangle-free W with alpha at most 3."""
from itertools import combinations, permutations
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from calibrate_crown_exact import edge, parse_graph6, triangle_free


def pairs(order):
    return tuple((left, right) for right in range(order) for left in range(right))


def edges(graph):
    return tuple((left, right) for left, right in pairs(len(graph)) if (graph[left] >> right) & 1)


def alpha_at_most_three(graph):
    return all(any((graph[left] >> right) & 1 for left, right in combinations(four, 2))
               for four in combinations(range(len(graph)), 4))


def orbit(graph, index):
    support = edges(graph)
    return {sum(index[image[left]][image[right]] for left, right in support)
            for image in permutations(range(len(graph)))}


def verify(folder):
    parents = [[]]
    for order in range(1, 9):
        index = [[0] * order for _ in range(order)]
        for shift, (left, right) in enumerate(pairs(order)):
            index[left][right] = index[right][left] = 1 << shift
        catalogue = []
        labelled = set()
        if order >= 4:
            path = folder / f'crown_w{order}.rows.tsv'
            for row, line in enumerate(path.read_text().splitlines(), 1):
                number, text = line.split()
                assert int(number) == row
                graph = parse_graph6(text)
                assert len(graph) == order and triangle_free(graph) and alpha_at_most_three(graph)
                images = orbit(graph, index)
                assert not labelled.intersection(images), (order, row, text)
                labelled.update(images)
                catalogue.append(graph)
        extensions = 0
        for parent in parents:
            for neighborhood in range(1 << (order - 1)):
                graph = parent.copy() + [0]
                for vertex in range(order - 1):
                    if (neighborhood >> vertex) & 1:
                        edge(graph, vertex, order - 1)
                if not (triangle_free(graph) and alpha_at_most_three(graph)):
                    continue
                extensions += 1
                mask = sum(index[left][right] for left, right in edges(graph))
                if mask not in labelled:
                    assert order < 4, (order, graph)
                    catalogue.append(graph)
                    labelled.update(orbit(graph, index))
        print(f'W={order}: {len(catalogue)} representatives, {len(labelled)} labelled graphs, '
              f'{extensions} permitted single-vertex extensions', flush=True)
        parents = catalogue


if __name__ == '__main__':
    verify(Path(sys.argv[1]))
