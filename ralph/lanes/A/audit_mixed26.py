#!/usr/bin/env python3
"""Rebuild the mixed j=3 mark and check geometric addback controls."""

from collections import Counter
from itertools import combinations, product
from pathlib import Path
import argparse

from audit_strip_extensions import mark, mixed_roles, source_lower, validate_graph
from audit_path_leaf import vertices
from residue_bundle import triangle_free


def roles(side, star, supports):
    for hole in combinations(side, 2):
        if hole in supports:
            continue
        if star in hole:
            yield ('middle', *hole, star)
        for peer in set(side).difference(hole):
            if star in (*hole, peer):
                yield ('matching', *hole, peer)


def full_lists(sides, stars, shape, left, right, peer, path_leaf):
    pivot_a, pivot_b = 28, 29
    active = ((*sides[0], pivot_a), (*sides[1], pivot_b))
    absent = ({tuple(sorted((stars[0], pivot_a))), (path_leaf, pivot_a)},
              {(left, right), (peer, pivot_b)})
    assert path_leaf != stars[0]
    assert (shape == 'middle') == (peer == stars[1] and peer in (left, right))
    return tuple(Counter({(anchor,): 4 for anchor in side}) + Counter(
        pair for pair in combinations(side, 2) if pair not in holes)
                 for side, holes in zip(active, absent, strict=True))


def addback(adj, path, mixed, role, wrong_hole=None):
    sides, stars, counts = mark(adj, path, mixed)
    shape, left, right, peer = role
    if wrong_hole is not None:
        left, right = wrong_hole
    if counts[1][(left, right)]:
        raise ValueError('declared retained hole already occupied')
    path_leaf = next(anchor for anchor in sides[0] if anchor != stars[0])
    wanted = full_lists(sides, stars, shape, left, right, peer, path_leaf)
    result = list(adj) + [0] * (40-len(adj))
    common, a_only, b_only = range(30, 33), range(33, 36), range(36, 40)

    def edge(left, right):
        result[left] |= 1 << right
        result[right] |= 1 << left

    edge(26, 27)
    for index, (own_cut, other_cut) in enumerate(((a_only, b_only), (b_only, a_only))):
        pivot, root = 28 + index, 26 + index
        for member in (*sides[index], pivot):
            edge(root, member)
        retained_list = Counter({part: count for part, count in wanted[index].items() if pivot not in part})
        missing = retained_list - counts[index]
        assert not (counts[index] - wanted[index])
        for vertex, support in zip(other_cut, sorted(missing.elements()), strict=True):
            for anchor in support:
                edge(vertex, anchor)
        own_supports = sorted((part for part in wanted[index].elements() if pivot in part),
                              key=lambda part: (stars[index] not in part, part))
        for vertex, support in zip((*common, *own_cut), own_supports, strict=True):
            for anchor in support:
                edge(vertex, anchor)
    assert triangle_free(result)
    assert result[28].bit_count() == 7 and result[29].bit_count() == 8
    assert (result[28] & result[29]).bit_count() == 3
    keep = ((1 << 40)-1) & ~(result[28] | result[29] | (1 << 28) | (1 << 29))
    assert keep == (1 << 26)-1
    assert [neighbors & keep for neighbors in result[:26]] == list(adj)
    exterior = set(range(26)).difference(*sides) | set(range(30, 40))
    for index, side in enumerate(sides):
        observed = Counter(tuple(sorted(set(vertices(result[vertex])) & {*side, 28+index}))
                           for vertex in exterior)
        assert observed == wanted[index]
    return result


def snapshots():
    side = (0, 1, 2, 3)
    pairs = list(combinations(side, 2))
    totals = Counter()
    for star, occupied in product(side, range(64)):
        seen = {pair for index, pair in enumerate(pairs) if occupied >> index & 1}
        actual = set(roles(side, star, seen))
        assert actual == set(mixed_roles(side, star, seen))
        totals[bool(actual)] += 1
    print('local snapshots:', totals, flush=True)


def generate(marked, output, order):
    counts = Counter()
    controls = set()
    with output.open('w') as target:
        for line in marked.read_text().splitlines():
            row, first, second, encoded = line.split()
            adj = validate_graph(encoded)
            assert len(adj) == order
            degree = [neighbors.bit_count() for neighbors in adj]
            masks = (int(first), int(second))
            sides, stars, support = mark(adj, *masks)
            bits = sum(degree)
            if order == 26:
                assert min(degree) == degree[-1] == 3 and max(degree) <= 7
                if bits > 174:
                    counts['edge_skip'] += 1
                    continue
            for index in (0, 1):
                all_roles = set(roles(sides[index], stars[index], support[index]))
                assert all_roles == set(mixed_roles(sides[index], stars[index], support[index]))
                for role in sorted(all_roles):
                    case = role[0]
                    path_mask, mixed_mask = masks[1-index], masks[index]
                    print(row, path_mask, mixed_mask, *role, encoded, file=target)
                    counts[index, case] += 1
                    if order != 26 or (index, case) in controls:
                        continue
                    other_hole = next((part for part in support[index] if len(part) == 2), None)
                    if other_hole is None:
                        continue
                    addback(adj, path_mask, mixed_mask, role)
                    try:
                        addback(adj, path_mask, mixed_mask, role, wrong_hole=other_hole)
                    except ValueError as error:
                        assert str(error) == 'declared retained hole already occupied'
                    else:
                        raise AssertionError('occupied-hole mutation passed')
                    controls.add((index, case))
                    print('addback PASS / occupied hole rejects:', row, path_mask, mixed_mask, *role,
                          'occupied', *other_hole, flush=True)
    if order == 26:
        assert controls == set(product((0, 1), ('middle', 'matching')))
    print('ordered roles by mixed index and shape:', counts, 'total',
          sum(count for key, count in counts.items() if isinstance(key, tuple)), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('order', type=int, choices=(26, 27))
    parser.add_argument('marked', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--source-check', nargs=3, type=Path, metavar=('RAW_MARKS', 'RAW_GRAPHS', 'CORES'))
    args = parser.parse_args()
    snapshots()
    if args.source_check:
        raw_marks, raw_graphs, cores = args.source_check
        source_lower(raw_marks, args.marked, raw_graphs, cores)
    generate(args.marked, args.output, args.order)


if __name__ == '__main__':
    main()
