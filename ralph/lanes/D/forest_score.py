#!/usr/bin/env python3
"""Check the square/P3 score identity and score the complete tight catalogue."""

from collections import Counter, defaultdict
from itertools import combinations, combinations_with_replacement
from pathlib import Path
import sys

from kernel_projection import bits, decode
from max_root import catalogue, count_edges
from q22_root import exact_square_counts

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
from check_graph import brute_alpha, triangle_free


def components(graph, vertices):
    while vertices:
        todo = vertices & -vertices
        connected = todo
        while todo:
            bit = todo & -todo
            todo ^= bit
            found = graph[bit.bit_length() - 1] & vertices & ~connected
            connected |= found
            todo |= found
        yield connected
        vertices ^= connected


def square_score(graph):
    order = len(graph)
    assert triangle_free(graph)
    hist = Counter()
    monochrome = 0
    for first, second in combinations(range(order), 2):
        if graph[first] >> second & 1:
            continue
        common = tuple(bits(graph[first] & graph[second]))
        assert len(common) in (2, 3)
        hist[len(common)] += 1
        if len(common) == 3:
            mono_pairs = {(graph[left] & graph[right]).bit_count() for left, right in combinations(common, 2)}
            monochrome += len(mono_pairs) == 1
    q22 = exact_square_counts(graph)
    total = 0
    for (first, second), squares in q22.items():
        kernel = (graph[first] ^ (1 << second)) | (graph[second] ^ (1 << first))
        parts = list(components(graph, kernel))
        assert squares == sum(part.bit_count() == 2 for part in parts)
        total += squares + sum(part.bit_count() == 3 for part in parts)
    assert total == 2 * (hist[2] - hist[3] + monochrome)
    return hist[2], hist[3], monochrome, total


def circulant(order, steps):
    return [sum(1 << ((coord + step) % order) for step in steps) for coord in range(order)]


def controls(directory):
    graphs = [circulant(20, (-6, -5, -2, 2, 5, 6))]
    for path in sorted(directory.glob('eager-*.g6')):
        for line in path.read_text().splitlines():
            graph = decode(line)
            if all((graph[first] & graph[second]).bit_count() == 2 for first, second in combinations(range(16), 2)
                   if not graph[first] >> second & 1):
                graphs.append(graph)
    assert len(graphs) == 2
    for graph in graphs:
        assert brute_alpha(graph) == graph[0].bit_count()
        print(f'PASS graph order={len(graph)} n2,n3,monochrome,sumS={square_score(graph)}')


def tight_census():
    stats = defaultdict(list)
    excluded = defaultdict(list)
    direct_sizes = {sizes for sizes in combinations_with_replacement(range(2, 11), 4)
                    if sum(sizes) == 16 and sum(size // 2 for size in sizes) >= 7}
    for index, code in enumerate(catalogue(40, 9)):
        graph = decode(code)
        if count_edges(graph) != 12:
            continue
        if any(not row for row in graph):
            excluded['isolate'].append(index)
            continue
        parts = list(components(graph, (1 << len(graph)) - 1))
        sizes = sorted(part.bit_count() for part in parts)
        if any(all((graph[coord] & part).bit_count() == 2 for coord in bits(part)) for part in parts):
            excluded['cycle'].append(index)
            continue
        assert len(sizes) == 4 and sum(size % 2 for size in sizes) <= 2
        direct_sizes.remove(tuple(sizes))
        isolated = sizes.count(2)
        p3 = sizes.count(3)
        stats[isolated + p3].append(index)
        sides = (sum(part.bit_count() == 3 and (part & 255).bit_count() == 1 for part in parts),
                 sum(part.bit_count() == 3 and (part & 255).bit_count() == 2 for part in parts))
        assert max(sides) <= 1
        print(f'{index}: iso={isolated} p3={p3} sides={sides} score={isolated + p3} sizes={sizes} key={code}')
    assert len(excluded['isolate']) == 19 and excluded['cycle'] == [19, 20, 22]
    assert not direct_sizes
    assert dict(stats) == {0: [34], 1: [30, 31, 33], 2: [24, 25, 26, 28, 29, 32], 3: [21, 23, 27]}
    print(f'PASS all 13 forest keys and independent path-size enumeration: {dict(sorted(stats.items()))}')


if __name__ == '__main__':
    controls(Path(sys.argv[1]))
    tight_census()
