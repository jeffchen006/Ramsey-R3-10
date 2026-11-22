#!/usr/bin/env python3
"""Independent semantic checks; no SAT, source generation, or LRAT replay."""

from collections import Counter
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from check_graph import parse_graph6


def adjacency(encoded):
    rows = parse_graph6(encoded)
    return [{index for index in range(len(rows)) if mask >> index & 1} for mask in rows]


def oriented_paths(graph, root, pivot):
    side_a, side_b = graph[root] - {pivot}, graph[pivot] - {root}
    paths = [(start,) for start in side_a]
    for depth in range(5):
        next_side = side_b if depth % 2 == 0 else side_a
        paths = [(*path, neighbor) for path in paths
                 for neighbor in ((graph[path[-1]] & next_side) - set(path))]
    return paths


def check_small_reroot(file):
    summary = Counter()
    for encoded in file.read_text().splitlines():
        graph = adjacency(encoded)
        assert len(graph) == 22 and {len(neighbors) for neighbors in graph} == {6}
        if any(len(first & second) > 3 for first, second in combinations(graph, 2)):
            continue
        for root, hood in enumerate(graph):
            masks = {vertex: graph[vertex] & hood for vertex in set(range(22)) - hood - {root}}
            triples = [(vertex, mask) for vertex, mask in masks.items() if len(mask) == 3]
            for (first, triple_first), (second, triple_second) in combinations(triples, 2):
                shared = triple_first & triple_second
                if len(shared) != 2:
                    continue
                left, = triple_first - shared
                right, = triple_second - shared
                for pivot in shared:
                    bridge, = shared - {pivot}
                    paths = oriented_paths(graph, root, pivot)
                    profile = all(len(graph[path[0]] & graph[path[4]]) == 3 for path in paths)
                    for start, end, start_witness, end_witness in (
                            (left, right, first, second), (right, left, second, first)):
                        common = graph[pivot] & graph[end]
                        if len(common) != 3:
                            continue
                        fresh, = common - {root, end_witness}
                        assert (start, start_witness, bridge, end_witness, end, fresh) in paths
                        high = len(graph[start] & graph[end]) == 3
                        assert not profile or high
                        summary[profile, high] += 1
    assert summary[True, True] > 0 and summary[False, False] > 0
    print('C22 cap-three controls (local profile, conclusion):', sorted(summary.items()))


def check_four_profiles(file):
    profiles = file.read_text().splitlines()
    assert len(profiles) == 2434
    path_edges = ((1, 7), (7, 2), (2, 5), (5, 3), (3, 6))
    for row in (2298, 2386, 2424, 2431):
        masks = dict(tuple(map(int, item.split(':'))) for item in profiles[row].split())
        assert sum(masks.values()) == 32
        graph = [set() for _ in range(40)]
        edges = [(0, 4), (0, 5), (0, 6), (0, 7), (4, 1), (4, 2), (4, 3), *path_edges]
        outside = 8
        for mask, copies in sorted(masks.items()):
            for _ in range(copies):
                edges.extend((anchor, outside) for anchor in range(8) if mask >> anchor & 1)
                outside += 1
        for first, second in edges:
            graph[first].add(second)
            graph[second].add(first)
        assert all(len(neighbors) == 9 for neighbors in graph[:8])
        paths = oriented_paths(graph, 4, 0) + oriented_paths(graph, 0, 4)
        assert len(paths) == 2
        for path in paths:
            common = graph[path[0]] & graph[path[4]]
            assert len(common) == 3
            assert any(vertex >= 8 for vertex in common)
        print('D frozen profile, (path, first/fifth codegree):', row,
              [(path, len(graph[path[0]] & graph[path[4]])) for path in paths])


def bits(mask, order):
    return {vertex for vertex in range(order) if mask >> vertex & 1}


def signature_counts(graph, side, exterior):
    return Counter(tuple(sorted(graph[vertex] & side)) for vertex in exterior)


def mixed_roles(graph, first_mask, second_mask):
    order = len(graph)
    masks = first_mask, second_mask
    sides = tuple(bits(mask, order) for mask in masks)
    assert len(sides[0]) == len(sides[1]) == 4 and sides[0].isdisjoint(sides[1])
    assert all(not (graph[vertex] & side) for side in sides for vertex in side)
    first_star, second_star = next(iter((left, right) for left in sides[0] for right in graph[left] & sides[1]))
    assert sum(len(graph[vertex] & sides[1]) for vertex in sides[0]) == 1
    exterior = set(range(order)) - sides[0] - sides[1]
    supports = [signature_counts(graph, side, exterior) for side in sides]
    for counts in supports:
        assert all(1 <= len(part) <= 2 and count <= (4 if len(part) == 1 else 1)
                   for part, count in counts.items())
    assert min(map(len, graph)) == len(graph[-1]) == 3 and max(map(len, graph)) <= 7
    if sum(map(len, graph)) > 174:
        return
    stars = first_star, second_star
    for index, side in enumerate(sides):
        pivot = order
        signature_pairs = tuple(combinations(sorted(side | {pivot}), 2))
        for holes in combinations(signature_pairs, 2):
            with_pivot = [pair for pair in holes if pivot in pair]
            if len(with_pivot) != 1:
                continue
            incident, = with_pivot
            hole, = set(holes) - {incident}
            if supports[index][hole]:
                continue
            cross = stars[index]
            shared = set(hole) & set(incident)
            if (shared and shared != {cross}) or (not shared and cross not in (*hole, *incident)):
                continue
            wants = Counter({(anchor,): 4 for anchor in side})
            wants.update(pair for pair in combinations(sorted(side), 2) if pair != hole)
            assert not supports[index] - wants and sum((wants - supports[index]).values()) == 3
            other = sides[1-index]
            wants_other = Counter({(anchor,): 4 for anchor in other})
            wants_other.update(combinations(sorted(other), 2))
            assert not supports[1-index] - wants_other
            assert sum((wants_other - supports[1-index]).values()) == 4
            yield index, (masks[1-index], masks[index], 'middle' if shared else 'matching',
                          *hole, incident[0])


def check_mixed(marks, roles):
    counts = Counter()
    expected = set()
    for row, mask_a, mask_b, encoded in map(str.split, marks.read_text().splitlines()):
        graph = adjacency(encoded)
        for index, role in mixed_roles(graph, int(mask_a), int(mask_b)):
            entry = (row, *map(str, role), encoded)
            assert entry not in expected
            expected.add(entry)
            counts[index, role[2]] += 1
    reported = [tuple(line.split()) for line in roles.read_text().splitlines()]
    assert len(reported) == len(expected) == 7166 and set(reported) == expected
    assert counts == {(0, 'matching'): 3336, (1, 'matching'): 2102,
                      (0, 'middle'): 857, (1, 'middle'): 871}
    print('Mixed j=3 ordered roles, (mixed-side index, shape):', sorted(counts.items()))


def check_full_mixed(marks, roles, receipts):
    expected = set()
    legal_shapes = Counter()
    counts = Counter()
    for row, left, right, encoded in map(str.split, marks.read_text().splitlines()):
        graph = adjacency(encoded)
        masks = int(left), int(right)
        sides = tuple(bits(mask, 27) for mask in masks)
        cross, = [(first, second) for first in sides[0] for second in (graph[first] & sides[1])]
        exterior = set(range(27)).difference(*sides)
        assert len(graph) == 27 and len(exterior) == 19
        for index, side in enumerate(sides):
            supports = signature_counts(graph, side, exterior)
            other = sides[1-index]
            supports_other = signature_counts(graph, other, exterior)
            wanted_other = Counter({(anchor,): 4 for anchor in other})
            wanted_other.update(combinations(sorted(other), 2))
            assert not supports_other - wanted_other
            assert sum((wanted_other - supports_other).values()) == 3
            for first, second in combinations(combinations(sorted(side), 2), 2):
                shared = set(first) & set(second)
                star = cross[index]
                if not shared and star in (*first, *second):
                    shape = 'full-matching'
                elif shared == {star}:
                    shape = 'full-middle'
                else:
                    continue
                legal_shapes[shape] += 1
                if supports[first] or supports[second]:
                    continue
                wanted = Counter({(anchor,): 4 for anchor in side})
                wanted.update(pair for pair in combinations(sorted(side), 2) if pair not in (first, second))
                assert not supports - wanted and sum((wanted - supports).values()) == 1
                entry = (row, str(masks[1-index]), str(masks[index]), shape, *map(str, (*first, *second)), encoded)
                assert entry not in expected
                expected.add(entry)
                counts[index, shape] += 1
    reported = [tuple(line.split()) for line in roles.read_text().splitlines()]
    assert expected == set(reported) and len(expected) == len(reported) == 162
    receipt_keys = [line.split('\t', 1)[0] for line in receipts.read_text().splitlines()]
    assert {'_'.join(entry[:-1]) for entry in expected} == set(receipt_keys) and len(receipt_keys) == 162
    assert set(shape for _, shape in counts) == {'full-matching'} and legal_shapes['full-middle'] > 0
    print('Mixed d9 j=5 legal shapes before occupancy:', sorted(legal_shapes.items()))
    print('Mixed d9 j=5 ordered roles and receipt IDs:', sorted(counts.items()))


if __name__ == '__main__':
    check_small_reroot(ROOT / 'duo/reg6_22.g6')
    check_four_profiles(ROOT / 'scratch/D/punct8/path.tsv')
    check_mixed(ROOT / 'scratch/G/round7/lowdegree26.canon.keys', ROOT / 'scratch/A/strip9/mixed.j3.keys')
    check_full_mixed(ROOT / 'scratch/G/round7/pair27.keys', ROOT / 'scratch/G/round9/mixedfull.keys',
                     ROOT / 'scratch/G/round9/mixedfull.bound/certificates.tsv')
