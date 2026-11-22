"""Small Ramsey catalogue controls for the two round-11 Lean interfaces."""

from collections import Counter
from functools import cache
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def graph6_small(record):
    order = record[0] - 63
    assert 0 < order < 63
    neibs = [0] * order
    index = 0
    for right in range(1, order):
        for left in range(right):
            bit = ((record[index // 6 + 1] - 63) >> (5 - index % 6)) & 1
            neibs[left] |= bit << right
            neibs[right] |= bit << left
            index += 1
    return neibs


def indices(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def graph_controls(order, expected_alpha, expected_count):
    path = ROOT / f"scratch/H/lit/r11-r3{expected_alpha + 1}_{order}.g6"
    graphs = path.read_bytes().splitlines()
    assert len(set(graphs)) == len(graphs) == expected_count
    count = Counter()
    maximum = 0
    for record in graphs:
        neibs = graph6_small(record)
        assert len(neibs) == order
        assert all(not (neibs[vertex] & neibs[other])
                   for vertex in range(order) for other in indices(neibs[vertex]))

        @cache
        def alpha(vertices):
            if not vertices:
                return 0
            vertex = (vertices & -vertices).bit_length() - 1
            remainder = vertices ^ (1 << vertex)
            return max(alpha(remainder), 1 + alpha(remainder & ~neibs[vertex]))

        assert alpha((1 << order) - 1) == expected_alpha
        alpha.cache_clear()
        bound = 3 * expected_alpha - 4
        for anchors in combinations(range(order), 3):
            mark = sum(1 << vertex for vertex in anchors)
            if any(neibs[vertex] & mark for vertex in anchors):
                continue
            covered = 0
            for vertex in anchors:
                covered |= neibs[vertex]
            for cross in anchors:
                for endpoint in indices(neibs[cross]):
                    exterior = covered & ~(1 << endpoint)
                    exterior_size = exterior.bit_count()
                    assert exterior_size <= bound
                    maximum = max(maximum, exterior_size)
                    count["marked"] += 1
                    count["tight"] += exterior_size == bound
                    count["restore_endpoint_violations"] += covered.bit_count() > bound
                    for side in (vertex for vertex in anchors if vertex != cross):
                        off = exterior & ~neibs[cross]
                        with_side = off & neibs[side]
                        without_side = off & ~neibs[side]
                        assert with_side.bit_count() + 1 <= expected_alpha
                        assert without_side.bit_count() + 2 <= expected_alpha
                        assert off.bit_count() + 3 <= 2 * expected_alpha
                        count["oriented_splits"] += 1
    assert count["marked"] > 0 and count["oriented_splits"] == 2 * count["marked"]
    assert count["restore_endpoint_violations"] == count["tight"]
    print(f"order={order} alpha={expected_alpha} hosts={len(graphs)} max={maximum} {dict(count)}")


def pair_controls(order):
    pairs = [((1 << left) | (1 << right)) for left, right in combinations(range(order), 2)]
    count = Counter()
    for selected in range(1 << len(pairs)):
        family = [pairs[index] for index in indices(selected)]
        if not family:
            count["empty"] += 1
        elif any(not (edge & other) for edge, other in combinations(family, 2)):
            count["disjoint"] += 1
        elif any(all(edge & (1 << vertex) for edge in family) for vertex in range(order)):
            count["hub"] += 1
        else:
            support = 0
            for edge in family:
                support |= edge
            assert len(family) == support.bit_count() == 3
            count["triangle"] += 1
    expected_triangles = len(list(combinations(range(order), 3)))
    assert count["triangle"] == expected_triangles
    expected_hubs = sum(len(list(combinations(range(order - 1), degree))) * order
                        for degree in range(2, order)) + len(pairs)
    assert count["hub"] == expected_hubs
    print(f"order={order} all_families={1 << len(pairs)} {dict(count)}")


if __name__ == "__main__":
    graph_controls(13, 4, 1)
    graph_controls(17, 5, 7)
    graph_controls(22, 6, 191)
    for order in range(7):
        pair_controls(order)
