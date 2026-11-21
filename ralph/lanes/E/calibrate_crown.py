#!/usr/bin/env python3
"""Compare every labeled 3-vertex anchor with a direct full-graph oracle."""
from itertools import combinations, permutations
from pathlib import Path
import random
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
from check_graph import brute_alpha, parse_graph6, to_graph6, triangle_free


def edge(graph, left, right):
    graph[left] |= 1 << right
    graph[right] |= 1 << left


def is_control(graph):
    swapped = (0, 1, 2, 3, 5, 4, 7, 6, 9, 8)
    return (all(row.bit_count() == 3 for row in graph) and triangle_free(graph)
            and brute_alpha(graph) == 4
            and all((graph[left] >> right & 1) == (graph[swapped[left]] >> swapped[right] & 1)
                    for left, right in combinations(range(10), 2)))


def oracle(anchor):
    for first, second in permutations(range(3), 2):
        for link in range(8):
            graph = anchor + [0] * 7
            for vertex in range(3):
                if link >> vertex & 1:
                    edge(graph, 3, vertex)
            for left, right in combinations(range(3), 2):
                edge(graph, 4 + 2 * left, 5 + 2 * right)
                edge(graph, 5 + 2 * left, 4 + 2 * right)
            for pair, fixed in enumerate((3, first, second)):
                edge(graph, fixed, 4 + 2 * pair)
                edge(graph, fixed, 5 + 2 * pair)
            if is_control(graph):
                return True
    return False


def window_test(binary):
    rng = random.Random(40232)
    anchors = []
    for cycle in (5, 7):
        for spice in (0, 4, 9, 15):
            relabel = rng.sample(range(15), 15)
            graph = [0] * 15
            links = [(vertex, (vertex + 1) % cycle) for vertex in range(cycle)]
            links += [(vertex, vertex + 1) for vertex in range(cycle, 11, 2)]
            for left, right in links:
                edge(graph, relabel[left], relabel[right])
            options = [link for link in combinations(range(15), 2) if max(link) >= 11]
            rng.shuffle(options)
            for left, right in options[:spice]:
                left, right = relabel[left], relabel[right]
                if not graph[left] & graph[right]:
                    edge(graph, left, right)
            anchors.append(graph)
    expected = set()
    for index, graph in enumerate(anchors, 1):
        for vertices in combinations(range(15), 11):
            mask = sum(1 << vertex for vertex in vertices)
            degrees = [(graph[vertex] & mask).bit_count() for vertex in vertices]
            if 0 in degrees:
                continue
            induced = [sum(1 << i for i, other in enumerate(vertices) if graph[vertex] >> other & 1)
                       for vertex in vertices]
            if brute_alpha(induced) > 5:
                continue
            for nonseven in (0, (1 << 0) | (1 << 3) | (1 << 12)):
                cost = sum(degree >= 2 or (nonseven >> vertex & 1)
                           for vertex, degree in zip(vertices, degrees))
                expected.update((index, budget, nonseven, mask) for budget in (5, 7, 8) if cost <= budget)
    text = '\n'.join(map(to_graph6, anchors)) + '\n'
    out = subprocess.run([binary, 'window-control'], input=text, text=True, capture_output=True, check=True)
    got = set()
    for line in out.stdout.splitlines():
        if line.startswith('control '):
            index = int(line.split()[1])
        else:
            row = (index, *map(int, line.split()))
            assert row not in got
            got.add(row)
    assert got == expected and got
    print(f'W-first: all {len(anchors)}*1365 labeled windows checked by brute force; {len(got)} qualifying rows match.')


def main(binary):
    anchors = []
    for bits in range(1, 7):
        anchor = [0] * 3
        for index, (left, right) in enumerate(combinations(range(3), 2)):
            if bits >> index & 1:
                edge(anchor, left, right)
        anchors.append(anchor)
    text = '\n'.join(map(to_graph6, anchors)) + '\n'
    out = subprocess.run([binary, 'petersen'], input=text, text=True, capture_output=True, check=True)
    statuses = []
    for line in out.stdout.splitlines():
        if line.startswith('witness '):
            graph = parse_graph6(line.split()[1])
            assert [row & 7 for row in graph[:3]] == anchors[len(statuses) - 1] and is_control(graph)
        else:
            statuses.append(line.endswith(' SAT'))
    assert statuses == [oracle(anchor) for anchor in anchors] and sum(statuses) == 3
    bad = subprocess.run([binary, 'petersen'], input='Bw\n', text=True, capture_output=True)
    assert bad.returncode == 1 and 'triangle' in bad.stderr
    print(out.stdout, end='')
    print('All 6 labeled anchors match the direct oracle: 3 Petersen extensions, 3 empty. Triangle rejected.')
    window_test(binary)


if __name__ == '__main__':
    main(sys.argv[1])
