"""Check the multiplicity row on physical graphs and distinguish the two premises."""

from collections import Counter
from itertools import combinations, combinations_with_replacement


def graph(vertices, edges):
    adjacent = {vertex: set() for vertex in vertices}
    for first, second in edges:
        assert first != second
        adjacent[first].add(second)
        adjacent[second].add(first)
    return adjacent


def independent_count(adjacent, size):
    return sum(
        all(second not in adjacent[first] for first, second in combinations(sites, 2))
        for sites in combinations(adjacent, size)
    )


def check_graph(adjacent):
    assert all(not (adjacent[first] & adjacent[second])
               for first in adjacent for second in adjacent[first])
    assert max(len(adjacent[first] & adjacent[second])
               for first, second in combinations(adjacent, 2)) <= 3


def pole_row(adjacent, left, right, middle, first, second):
    assert left != right and right not in adjacent[left]
    assert adjacent[left] & adjacent[right] == {middle}
    assert first != second and {first, second} <= adjacent[middle] - {left, right}
    assert second not in adjacent[first]
    wing_left = adjacent[left] - {middle}
    wing_right = adjacent[right] - {middle}
    untouched = set(adjacent) - ({left, right, middle} | adjacent[left] | adjacent[right] | adjacent[middle])
    assert not (wing_left & wing_right or wing_left & untouched or wing_right & untouched)
    shared = adjacent[first] & adjacent[second]
    counts = tuple(len(shared & subset) for subset in (wing_left, wing_right, untouched))
    assert sum(counts) + 1 == len(shared)
    assert (sum(counts) >= 1) == (shared != {middle})
    return counts


def positive_controls():
    seen = Counter()
    for size in (1, 2):
        for locations in combinations_with_replacement(range(3), size):
            left, right, middle, first, second = range(5)
            edges = [(site, middle) for site in (left, right, first, second)]
            for site, location in enumerate(locations, 5):
                edges.extend([(site, first), (site, second)])
                if location != 2:
                    edges.append((site, (left, right)[location]))
            adjacent = graph(range(5 + size), edges)
            check_graph(adjacent)
            row = pole_row(adjacent, left, right, middle, first, second)
            assert row == tuple(locations.count(location) for location in range(3))
            seen[sum(row)] += 1
    assert seen == {1: 3, 2: 6}
    print(f"positive physical controls: {dict(seen)} lower/upper tight rows")


def adverse_controls():
    vertices = tuple(map(frozenset, combinations(range(5), 2)))
    petersen_edges = [(left, right) for left, right in combinations(vertices, 2)
                      if not left & right]
    petersen = graph(vertices, petersen_edges)
    assert len(vertices) == 10 and len(petersen_edges) == 15
    assert (independent_count(petersen, 4), independent_count(petersen, 5)) == (5, 0)
    check_graph(petersen)
    assert all(len(petersen[left] & petersen[right]) == 1
               for left, right in combinations(vertices, 2) if right not in petersen[left])

    checked_middles = 0
    seen = Counter()
    for original_middle in vertices:
        blocks = {site: [(site, copy) for copy in range(1 + int(site in petersen[original_middle]))]
                  for site in vertices}
        adjacent = graph((copy for block in blocks.values() for copy in block),
                         ((first, second) for left, right in petersen_edges
                          for first in blocks[left] for second in blocks[right]))
        check_graph(adjacent)
        assert len(adjacent) == 13
        assert all(adjacent[left] & adjacent[right]
                   for left, right in combinations(adjacent, 2) if right not in adjacent[left])
        middle = (original_middle, 0)
        codegrees = [len(adjacent[middle] & adjacent[other])
                     for other in set(adjacent) - {middle} - adjacent[middle]]
        assert codegrees == [2] * 6
        checked_middles += 1
        for left, right in combinations(adjacent[middle], 2):
            if adjacent[left] & adjacent[right] != {middle}:
                continue
            for first, second in combinations(adjacent[middle] - {left, right}, 2):
                row = pole_row(adjacent, left, right, middle, first, second)
                assert sum(row) in (0, 2)
                seen[sum(row)] += 1
    assert checked_middles == 10 and seen == {0: 600, 2: 120}
    print(f"Petersen: order 10, e=15, alpha=4; {checked_middles} MTF cap-three blow-ups")
    print(f"{seen[0]} counterexamples to endpoint-only lower bound; {seen[2]} upper-tight rows")


if __name__ == "__main__":
    positive_controls()
    adverse_controls()
