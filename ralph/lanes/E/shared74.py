#!/usr/bin/env python3
"""Necessary rooted-incidence compatibility for isomorphic vertex-deletion windows."""

import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
import json
from pathlib import Path
from time import process_time

from involution_cores import bits, graph
from involution_sat import from_graph6


MIXED = (10, 10, 11, 11)


@lru_cache(maxsize=65536)
def core_signature(core, selected):
    roots = tuple(bits(selected))
    rooted = tuple(core[vertex] & selected for vertex in roots)
    exterior = tuple(core[vertex] & selected for vertex in range(len(core)) if not selected >> vertex & 1)
    return roots, rooted, exterior


@lru_cache(maxsize=131072)
def fingerprint(core, selected, groups):
    roots, rooted, unmarked = core_signature(core, selected)
    columns = (*unmarked, *(support & selected for group in groups for support in group))
    sizes = Counter(mask.bit_count() for mask in columns)
    counts = tuple(sizes[size] for size in range(len(roots)+1))
    colors = tuple((adj.bit_count(), tuple(sorted(mask.bit_count() for mask in columns if mask >> root & 1)))
                   for root, adj in zip(roots, rooted))
    arcs = tuple(sorted((colors[left], tuple(sorted(colors[right] for right, root in enumerate(roots)
                        if rooted[left] >> root & 1))) for left in range(len(roots))))
    supports = tuple(sorted(tuple(sorted(colors[index] for index, root in enumerate(roots) if mask >> root & 1))
                            for mask in columns))
    return counts, arcs, supports


@lru_cache(maxsize=65536)
def subset_masks(selected, size):
    return tuple(sum(1 << vertex for vertex in roots) for roots in combinations(tuple(bits(selected)), size))


def compatible(core, first, second, high_count):
    first_roots, first_groups = first
    second_roots, second_groups = second
    overlap = first_roots.bit_count()+second_roots.bit_count()-high_count
    if overlap <= 0:
        return True
    first_types = {fingerprint(core, selected, first_groups) for selected in subset_masks(first_roots, overlap)}
    return any(fingerprint(core, selected, second_groups) in first_types
               for selected in subset_masks(second_roots, overlap))


@lru_cache(maxsize=2048)
def singles(group, order):
    return sum(1 << vertex for vertex in range(order) if sum(column >> vertex & 1 for column in group) == 1)


def window(core, groups, index):
    return singles(groups[index], len(core)), tuple(sorted(group for slot, group in enumerate(groups) if slot != index))


@lru_cache(maxsize=32768)
def root_orders(core, selected, groups):
    roots, rooted, unmarked = core_signature(core, selected)
    columns = (*unmarked, *(support & selected for group in groups for support in group))
    color_blocks = {}
    for vertex, row in zip(roots, rooted):
        color = (row.bit_count(), tuple(sorted(mask.bit_count() for mask in columns if mask >> vertex & 1)))
        color_blocks.setdefault(color, []).append(vertex)
    best, orders = None, []
    for blocks in product(*(permutations(color_blocks[color]) for color in sorted(color_blocks))):
        order = sum(blocks, ())
        translate = dict(zip(roots, (1 << order.index(vertex) for vertex in roots)))
        compact = {mask: sum(translate[vertex] for vertex in bits(mask)) for mask in set(columns)}
        stem = (tuple(sum(translate[peer] for peer in bits(core[vertex] & selected)) for vertex in order),
                tuple(sorted(compact[mask] for mask in columns)))
        if best is None or stem < best:
            best, orders = stem, [order]
        elif stem == best:
            orders.append(order)
    return best, tuple(orders)


def marked_type(core, selected, stem, orders, inside, extra):
    labels = (*tuple(bits(inside & ~selected)), *(len(core)+slot for slot, _ in extra))
    supports = dict(extra)

    def w_neighbors(vertex):
        return core[vertex] if vertex < len(core) else supports[vertex-len(core)]

    def adjacent(left, right):
        if left >= len(core) and right >= len(core):
            return 1
        if right < len(core):
            return w_neighbors(left) >> right & 1
        return w_neighbors(right) >> left & 1

    def code(order):
        colors = {vertex: sum(1 << index for index, root in enumerate(order) if w_neighbors(vertex) >> root & 1)
                  for vertex in labels}
        blocks = {}
        for vertex in labels:
            blocks.setdefault(colors[vertex], []).append(vertex)
        return min((tuple(colors[vertex] for vertex in ext_order),
                    tuple(adjacent(left, right) for left, right in combinations(ext_order, 2)))
                   for blocks_order in product(*(permutations(blocks[color]) for color in sorted(blocks)))
                   for ext_order in (sum(blocks_order, ()),))

    return stem, min(map(code, orders))


@lru_cache(maxsize=32768)
def marked_types(core, selected, inside, groups, high_count):
    required = high_count-inside.bit_count()
    stem, orders = root_orders(core, selected, groups)
    if required == 0:
        extras = ((),)
    else:
        columns = tuple((group, support) for group, supports in enumerate(groups) for support in supports)
        columns = tuple((group, slot, support) for slot, (group, support) in enumerate(columns))
        extras = (tuple((slot, support) for group, slot, support in selected_columns)
                  for selected_columns in combinations(columns, required)
                  if required != 2 or (selected_columns[0][0] != selected_columns[1][0] and
                                      not selected_columns[0][2] & selected_columns[1][2]))
    return frozenset(marked_type(core, selected, stem, orders, inside, extra) for extra in extras)


def marked_compatible(core, first, second, high_count):
    first_roots, first_groups = first
    second_roots, second_groups = second
    overlap = first_roots.bit_count()+second_roots.bit_count()-high_count
    if overlap <= 0:
        return True
    first_by_stem = {}
    second_by_stem = {}
    for roots, groups, by_stem in ((*first, first_by_stem), (*second, second_by_stem)):
        for selected in subset_masks(roots, overlap):
            stem, _ = root_orders(core, selected, groups)
            by_stem.setdefault(stem, []).append(selected)
    for stem in first_by_stem.keys() & second_by_stem.keys():
        first_types = set().union(*(marked_types(core, selected, first_roots, first_groups, high_count)
                                   for selected in first_by_stem[stem]))
        if any(not first_types.isdisjoint(marked_types(core, selected, second_roots, second_groups, high_count))
               for selected in second_by_stem[stem]):
            return True
    return False


def surviving_counts(core, groups, marked=False):
    windows = tuple(window(core, groups, index) for index in range(4))
    for high_count in (6, 7, 8):
        if any(not roots.bit_count() <= high_count <= roots.bit_count()+2 for roots, _ in windows):
            continue
        if all(compatible(core, first, second, high_count) for first, second in combinations(windows, 2)):
            if not marked or all(marked_compatible(core, first, second, high_count)
                                 for first, second in combinations(windows, 2)):
                yield high_count


def calibration():
    order = 13
    core = graph(order, [(left, right) for left, right in combinations(range(order), 2)
                         if (right-left) % order in (1, 5, 8, 12)])
    independent = lambda vertices: all(not core[left] >> right & 1 for left, right in combinations(vertices, 2))
    assert not any(all(core[left] >> right & 1 for left, right in combinations(vertices, 2))
                   for vertices in combinations(range(order), 3))
    assert not any(independent(vertices) for vertices in combinations(range(order), 5))
    assert any(independent(vertices) for vertices in combinations(range(order), 4))
    independent_triples = tuple(set(vertices) for vertices in combinations(range(order), 3) if independent(vertices))
    counts = Counter()
    for first in independent_triples:
        for shift in range(1, order):
            second = {(vertex+shift) % order for vertex in first}
            if first & second:
                continue
            markers = tuple(vertex for vertex in range(order) if vertex not in first | second)
            interior = graph(len(markers), [(left,right) for left,right in combinations(range(len(markers)), 2)
                                            if core[markers[left]] >> markers[right] & 1])
            cards = []
            rooted_cards = []
            for retained, omitted in ((second, first), (first, second)):
                active = (set(range(order))-omitted)
                degrees = {vertex: sum(core[vertex] >> neighbor & 1 for neighbor in active) for vertex in active}
                high_count = sum(degree == 4 for degree in degrees.values())
                columns = tuple(sum(1 << index for index, marker in enumerate(markers) if core[vertex] >> marker & 1)
                                for vertex in sorted(retained))
                roots = sum(1 << index for index, marker in enumerate(markers) if degrees[marker] == 4)
                cards.append(((roots, (columns,)), high_count))
                rooted_cards.append((roots, columns))
            (first_card, first_count), (second_card, second_count) = cards
            assert first_count == second_count
            assert compatible(interior, first_card, second_card, first_count)
            assert marked_compatible(interior, first_card, second_card, first_count)
            counts['translated positives'] += 1
            counts['nonempty matched roots'] += first_card[0].bit_count()+second_card[0].bit_count() > first_count
            selected, columns = rooted_cards[0]
            if selected:
                changed = list(columns)
                changed[0] ^= selected & -selected
                candidate = (selected, (tuple(changed),))
                assert not compatible(interior, first_card, candidate, selected.bit_count())
                assert not marked_compatible(interior, first_card, candidate, selected.bit_count())
                counts['planted one-bit mismatches'] += 1
    assert all(counts[category] for category in ('translated positives', 'nonempty matched roots', 'planted one-bit mismatches'))
    print('C13(1,5) calibration:', dict(counts), flush=True)


def pilot(path, every, limit, rejected, marked):
    result = Counter()
    started = process_time()
    for index, line in enumerate(path.open(encoding='ascii')):
        if index % every:
            continue
        key, profile, projected, options = json.loads(line)
        if tuple(profile) != MIXED:
            continue
        core = tuple(from_graph6(key))
        projected = tuple(map(tuple, projected))
        result['projections'] += 1
        viable = False
        for option in options:
            groups = (*projected, tuple(option))
            possibilities = tuple(surviving_counts(core, groups, marked))
            result['lifts'] += 1
            result['surviving lifts'] += bool(possibilities)
            viable |= bool(possibilities)
            for high_count in possibilities:
                result[f'surviving lifts K={high_count}'] += 1
        result['surviving projections'] += viable
        if rejected is not None and not viable:
            print(index, file=rejected)
        if limit and result['projections'] == limit:
            break
    print(path.name, 'stride', every, 'limit', limit, dict(result), f'cpu={process_time()-started:.3f}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', type=Path, nargs='*')
    parser.add_argument('--every', type=int, default=1)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--marked', action='store_true')
    parser.add_argument('--reject', type=argparse.FileType('w'))
    args = parser.parse_args()
    if args.reject is not None:
        assert len(args.paths) == 1
    calibration()
    for path in args.paths:
        pilot(path, args.every, args.limit, args.reject, args.marked)


if __name__ == '__main__':
    main()
