"""Small boundary-only cover for the isolated e80 pair with a degree-three anchor."""

import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, permutations, product
from pathlib import Path

from kernel_projection import bits
from p2_anchor import build_boundary, controls
from p3_round4_index import has_independent
from path_three_top import connect


def maps(wing_size):
    wing = wing_size - 1
    left = list(range(2, 2 + wing))
    right = list(range(2 + wing, 2 + 2 * wing))
    for centre, a_side, b_side in product(permutations(range(2)), permutations(left), permutations(right)):
        yield (*centre, *a_side, *b_side)
        yield (*centre, *b_side, *a_side)


def symmetry_key(masks, wing_size):
    return min(tuple(sorted(sum(1 << mapping[vertex] for vertex in bits(mask)) for mask in masks))
               for mapping in maps(wing_size))


@lru_cache(maxsize=None)
def patterns(wing_size, column_total):
    outgoing = [mask for mask in range(1 << (2 * wing_size)) if mask.bit_count() >= 2
                and (not (mask >> 2 & ((1 << (wing_size-1))-1)) or not mask >> (wing_size + 1))]
    return sorted({symmetry_key(combo, wing_size) for combo in combinations_with_replacement(outgoing, wing_size)
                   if sum(mask.bit_count() for mask in combo) == column_total})


def boundary_of(masks, wing_size=3, cap=6):
    base = build_boundary(wing_size, cap, 0)
    centre = 2 * wing_size + cap - 2
    start = centre + 2
    sides = [centre, centre + 1, *range(1, wing_size), *range(wing_size + 1, 2 * wing_size)]
    for index, mask in enumerate(masks):
        vertex = start + index
        for other in sides:
            base[vertex] &= ~(1 << other)
            base[other] &= ~(1 << vertex)
        for target in bits(mask):
            connect(base, vertex, sides[target])
    return base


def filter_boundary(graph):
    order = len(graph)
    first, second, anchor = range(order-3, order)
    if any(mask.bit_count() < 3 for mask in graph):
        return 'deficit'
    forced = [set() for _ in graph]
    for left, right in combinations(range(order), 2):
        codegree = (graph[left] & graph[right]).bit_count()
        if codegree > 6:
            return 'codegree'
        if codegree == 6:
            if {left, right} != {first, second} and (left in (first, second) or right in (first, second)):
                return 'isolation'
            forced[left].add(right)
            forced[right].add(left)
        if right in (first, second, anchor) and not codegree and not graph[left] >> right & 1:
            return 'root-maximality'
    if any(len(row) > 2 for row in forced):
        return 'forced-J-degree'
    for first in range(order):
        for second in forced[first]:
            for third in forced[second] - {first}:
                if third in forced[first]:
                    return 'forced-J-triangle'
                if forced[third] - {first, second}:
                    return 'forced-J-P4'
    for size, limit in ((3, 6), (4, 5)):
        for side in combinations(range(order), size):
            common = (1 << order) - 1
            for vertex in side:
                common &= graph[vertex]
            if common.bit_count() >= limit:
                return 'biclique'
    if has_independent(graph, (1 << order) - 1, 10):
        return 'alpha'
    return 'pass'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dump', action='store_true')
    parser.add_argument('--control-census', type=Path)
    args = parser.parse_args()
    if args.control_census:
        checked = Counter()

        def observer(graph, centre, left, right, wing_neighbours, before, after):
            size = len(wing_neighbours)
            positions = centre + left + right
            masks = [sum(1 << slot for slot, other in enumerate(positions) if graph[vertex] >> other & 1)
                     for vertex in wing_neighbours]
            assert symmetry_key(masks, size) in patterns(size, size * 6 - before + after)
            checked[after] += 1

        controls(args.control_census, observer)
        assert sum(checked.values()) == 444
        print('PASS all 444 C21 anchors in independently observed layout orbits', dict(sorted(checked.items())))
    for edges in range(65, 59, -1):
        keys = patterns(3, edges - 53)
        counts = Counter(filter_boundary(boundary_of(key)) for key in keys)
        if edges == 65:
            assert len(keys) == 2 and counts == {'codegree': 1, 'pass': 1}
        print('edges', edges, 'orbits', len(keys), dict(counts))
        if args.dump:
            for ident, key in enumerate(keys):
                print('key', edges, ident, filter_boundary(boundary_of(key)), key)


if __name__ == '__main__':
    main()
