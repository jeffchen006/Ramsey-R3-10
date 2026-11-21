#!/usr/bin/env python3
"""Direct combination enumeration for the strip scanner's smaller controls."""

from collections import Counter
from itertools import combinations
from pathlib import Path
from subprocess import run
import sys


def decode(line):
    neighbor = [set() for _ in range(ord(line[0]) - 63)]
    edges = ((left, right) for right in range(len(neighbor)) for left in range(right))
    bits = (int(bit) for char in line[1:] for bit in f'{ord(char)-63:06b}')
    for (left, right), bit in zip(edges, bits):
        if bit:
            neighbor[left].add(right)
            neighbor[right].add(left)
    return neighbor


def brute(line, width, privates, paired):
    neighbor = decode(line)
    vertices = set(range(len(neighbor)))

    def independent(anchors):
        return all(right not in neighbor[left] for left, right in combinations(anchors, 2))

    def support(anchors, exterior):
        counts = Counter(tuple(sorted(anchors & neighbor[vertex])) for vertex in exterior)
        return all((len(part) == 1 and count <= privates) or (len(part) == 2 and count == 1)
                   for part, count in counts.items())

    def mask(anchors):
        return sum(1 << vertex for vertex in anchors)

    answer = set()
    for first_tuple in combinations(vertices, width):
        first = set(first_tuple)
        if not independent(first):
            continue
        if not paired:
            if support(first, vertices - first):
                answer.add((mask(first), 0))
            continue
        for second_tuple in combinations(vertices - first, width):
            second = set(second_tuple)
            if not independent(second) or mask(first) >= mask(second):
                continue
            if sum(len(neighbor[vertex] & second) for vertex in first) != 1:
                continue
            exterior = vertices - first - second
            if support(first, exterior) and support(second, exterior):
                answer.add((mask(first), mask(second)))
    return answer


def control(binary, lines, width, privates, deleted, paired):
    command = [binary, 'pair' if paired else 'single', str(width), str(privates), str(deleted)]
    result = run(command, input='\n'.join(lines) + '\n', text=True, check=True, capture_output=True)
    expected = [(index, first, second) for index, line in enumerate(lines, 1)
                for first, second in brute(line, width, privates, paired)]
    actual = []
    for record in result.stdout.splitlines():
        index, first, second, line = record.split()
        assert lines[int(index) - 1] == line
        actual.append((int(index), int(first), int(second)))
    assert sorted(expected) == sorted(actual)
    print(result.stderr.strip(), 'independent positive rows', len({row for row, _, _ in expected}))
    return len({row for row, _, _ in expected})


def check_analogue(loci):
    for line, independence in loci:
        neighbor = decode(line)
        maximum = []

        def subsets(pool, chosen):
            if len(chosen) + len(pool) < independence:
                return
            if len(chosen) == independence:
                maximum.append(set(chosen))
                assert not pool
                return
            while pool and len(chosen) + len(pool) >= independence:
                vertex = pool.pop()
                subsets(pool - neighbor[vertex], chosen + [vertex])

        subsets(set(range(len(neighbor))), [])
        assert maximum
        for anchors in maximum:
            singleton = Counter(next(iter(neighbor[vertex] & anchors))
                                for vertex in range(len(neighbor)) if len(neighbor[vertex] & anchors) == 1)
            assert max(singleton.values(), default=0) <= 1
        print('max-independent private analogue:', len(neighbor), 'vertices,', len(maximum), 'maximum sets')


if __name__ == '__main__':
    binary, file, *analogues = sys.argv[1:]
    graphs = Path(file).read_text().splitlines()
    assert 0 < control(binary, graphs, 2, 2, 1, True) < len(graphs)
    assert 0 < control(binary, graphs, 3, 1, 1, False) < len(graphs)
    if analogues:
        check_analogue((Path(path).read_text().splitlines()[0], int(bound))
                       for path, bound in zip(analogues[::2], analogues[1::2], strict=True))
