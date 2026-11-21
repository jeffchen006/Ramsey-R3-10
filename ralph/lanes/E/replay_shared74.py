#!/usr/bin/env python3
"""Replay mixed-window receipts using direct color-preserving rooted mappings."""

import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations, groupby, permutations, product
import json
from pathlib import Path

from involution_sat import from_graph6
from m11_prop import proof_check, targets


@lru_cache(maxsize=16384)
def card(core, groups, omitted, high_count):
    masks = tuple(support for group in groups for support in group)
    group_ids = tuple(index for index, group in enumerate(groups) for _ in group)
    present = tuple(slot for slot, group in enumerate(group_ids) if group != omitted)
    removed = tuple(slot for slot, group in enumerate(group_ids) if group == omitted)
    inside = tuple(vertex for vertex in range(len(core)) if sum(masks[slot] >> vertex & 1 for slot in removed) == 1)
    count = high_count-len(inside)
    if not 0 <= count <= 2:
        return (), (), ()
    extras = tuple(selected for selected in combinations(present, count)
                   if count != 2 or (group_ids[selected[0]] != group_ids[selected[1]]
                                     and not masks[selected[0]] & masks[selected[1]]))
    return inside, tuple(masks[slot] for slot in present), tuple(tuple(masks[slot] for slot in option) for option in extras)


def projected(mask, roots):
    return sum(((mask >> vertex) & 1) << index for index, vertex in enumerate(roots))


@lru_cache(maxsize=65536)
def unmarked(core, columns, roots):
    outside = tuple(vertex for vertex in range(len(core)) if vertex not in roots)
    columns = tuple(projected(mask, roots) for mask in (*columns, *(core[vertex] for vertex in outside)))
    return tuple(projected(core[vertex], roots) for vertex in roots), tuple(sorted(columns))


def colors(code):
    internal, columns = code
    return tuple((row.bit_count(), tuple(sorted(value.bit_count() for value in columns if value >> index & 1)))
                 for index, row in enumerate(internal))


@lru_cache(maxsize=65536)
def marks(core, roots, inside, extras):
    remainder = tuple(vertex for vertex in inside if vertex not in roots)
    results = set()
    for option in extras:
        masks = (*(core[vertex] for vertex in remainder), *option)
        colors_of = tuple(projected(mask, roots) for mask in masks)
        blocks = [[index for index, value in enumerate(colors_of) if value == color] for color in sorted(set(colors_of))]
        edges = set()
        for left, right in combinations(range(len(masks)), 2):
            if (left >= len(remainder) or masks[right] >> remainder[left] & 1):
                edges.add((left, right))
        for pieces in product(*(permutations(block) for block in blocks)):
            order = sum(pieces, ())
            results.add((tuple(colors_of[index] for index in order),
                         tuple(tuple(sorted(pair)) in edges for pair in combinations(order, 2))))
    return frozenset(results)


def possible_pair(core, first, second, high_count):
    first_inside, first_columns, first_extras = first
    second_inside, second_columns, second_extras = second
    overlap = len(first_inside)+len(second_inside)-high_count
    if overlap <= 0:
        return True
    second_roots = tuple((roots, colors(unmarked(core, second_columns, roots)))
                         for roots in combinations(second_inside, overlap))
    for first_roots in combinations(first_inside, overlap):
        first_code = unmarked(core, first_columns, first_roots)
        first_colors = colors(first_code)
        for roots, second_colors in second_roots:
            if sorted(first_colors) != sorted(second_colors):
                continue
            options = tuple(tuple(vertex for vertex, color in zip(roots, second_colors) if color == first_color)
                            for first_color in first_colors)
            for candidate in product(*options):
                if len(set(candidate)) != overlap or first_code != unmarked(core, second_columns, candidate):
                    continue
                left = marks(core, first_roots, first_inside, first_extras)
                right = marks(core, candidate, second_inside, second_extras)
                if left & right:
                    return True
    return False


def compatible(core, groups):
    for high_count in (6, 7, 8):
        cards = tuple(card(core, groups, omitted, high_count) for omitted in range(4))
        if all(window[2] for window in cards) and all(possible_pair(core, first, second, high_count)
                                                     for first, second in combinations(cards, 2)):
            return True
    return False


def read(path):
    with path.open(encoding='ascii') as stream:
        yield from map(json.loads, stream)


def replay(cover, trace):
    receipts = iter(groupby(read(trace), key=lambda row: row[0]))
    stats = Counter()
    for index, (key, profile, projected_groups, omitted) in enumerate(read(cover)):
        core = tuple(from_graph6(key))
        projected_groups = tuple(map(tuple, projected_groups))
        assert profile == [10, 10, 11, 11] and omitted
        serial, records = next(receipts)
        records = tuple(records)
        assert serial == index and records
        stats['projections'] += 1
        stats['lifts'] += len(omitted)
        if records[0][1] == -1:
            assert len(records) == 1 and records[0][2:4] == ['graph', 3] and records[0][4][0]
            pinned, eligible = targets(core, projected_groups)
            proof_check(pinned, eligible, 7, 74, *records[0][4])
            stats['projection graphs'] += 1
            stats['lifts refuted as projection'] += len(omitted)
            continue
        assert len(records) == len(omitted)
        for position, record in enumerate(records):
            assert record[1] == position
            groups = (*projected_groups, tuple(omitted[position]))
            if record[2] == 'graph':
                dropped, witness = record[3:]
                assert 0 <= dropped <= 2 and 0 < witness[0] <= 5
                pinned, eligible = targets(core, groups[:dropped]+groups[dropped+1:])
                proof_check(pinned, eligible, 7, 74, *witness)
                stats['lift graphs'] += 1
            elif record[2] == 'incompatible':
                assert len(record) == 3 and not compatible(core, groups), (index, position)
                stats['lift incompatibilities'] += 1
            else:
                assert record[2] == 'open' and len(record) == 3
                stats['open lifts'] += 1
    assert next(receipts, None) is None
    print('explicit mapping replay:', dict(stats), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cover', type=Path)
    parser.add_argument('trace', type=Path)
    args = parser.parse_args()
    replay(args.cover, args.trace)
