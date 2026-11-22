#!/usr/bin/env python3
"""Necessary degree-seven deck tests on one physical E-23 projection row."""

import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
import json
from pathlib import Path
from time import process_time


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def mask_of(sites):
    return sum(1 << site for site in sites)


def decode(label):
    order = ord(label[0]) - 63
    assert 0 <= order < 63
    raw = ''.join(f'{ord(ch)-63:06b}' for ch in label[1:])
    adjacency = [0] * order
    for sign, pair in zip(raw, ((second, first) for first in range(order) for second in range(first))):
        if sign == '1':
            left, right = pair
            adjacency[left] |= 1 << right
            adjacency[right] |= 1 << left
    return tuple(adjacency)


def build_pinned(core, groups):
    adjacency = list(core)
    for support in (support for group in groups for support in group):
        for root in bits(support):
            adjacency[root] |= 1 << len(adjacency)
        adjacency.append(support)
    return tuple(adjacency)


def trace(adjacency, vertices, roots):
    return Counter(mask_of(index for index, root in enumerate(roots) if adjacency[site] >> root & 1)
                   for site in vertices)


@lru_cache(maxsize=4096)
def shape_maps(adjacency, sites):
    degree = {site: (adjacency[site] & mask_of(sites)).bit_count() for site in sites}
    sorted_shape = tuple(sorted(degree.values()))
    cells = tuple(tuple(site for site in sites if degree[site] == value) for value in sorted(set(degree.values())))
    by_key = {}
    for ordered_cells in product(*(tuple(permutations(cell)) for cell in cells)):
        order = tuple(site for cell in ordered_cells for site in cell)
        key = tuple(adjacency[left] >> right & 1 for left, right in combinations(order, 2))
        by_key.setdefault(key, []).append(order)
    return sorted_shape, by_key


def isomorphisms(source, source_sites, target, target_sites):
    source_degree, source_maps = shape_maps(source, source_sites)
    target_degree, target_maps = shape_maps(target, target_sites)
    if source_degree != target_degree:
        return
    source_key = min(source_maps)
    source_order = source_maps[source_key][0]
    positions = tuple(source_order.index(site) for site in source_sites)
    for order in target_maps.get(source_key, ()):
        yield tuple(order[position] for position in positions)


def wing_orders(groups):
    start = 8
    answer = []
    for group in groups:
        answer.append(tuple(range(start, start + len(group))))
        start += len(group)
    return tuple(answer)


@lru_cache(maxsize=128)
def large_supports(core, singles):
    return enumerate_supports(core, tuple(1 if site in singles else 3 for site in range(8)))


@lru_cache(maxsize=128)
def enumerate_supports(core, degree_vector):
    singles = tuple(site for site, degree in enumerate(degree_vector) if degree == 1)
    if len(singles) > 6:
        return ()
    fixed = mask_of(singles)
    extras = tuple(site for site in range(8) if not fixed >> site & 1)
    independent = tuple(sel for sel in range(1, 256) if not any(core[site] & sel for site in bits(sel)))
    allowed = [0] * 8
    for slot, site in enumerate(singles):
        allowed[site] = 1 << slot
    choices = {degree: tuple(mask_of(cols) for cols in combinations(range(6), degree))
               for degree in set(degree_vector) if degree > 1}
    answers = set()

    def visit(index, assigned):
        if index == len(extras):
            columns = tuple(mask_of(site for site in range(8) if allowed[site] >> slot & 1) for slot in range(6))
            answers.add(tuple(sorted(columns)))
            return
        site = extras[index]
        blocked = 0
        for neighbor in bits(core[site] & assigned):
            blocked |= allowed[neighbor]
        pending = assigned | (1 << site)
        tests = tuple(tuple(bits(sel)) for sel in independent if sel >> site & 1 and sel & pending == sel)
        for selection in choices[degree_vector[site]]:
            if selection & blocked:
                continue
            allowed[site] = selection
            for test in tests:
                union = 0
                for peer in test:
                    union |= allowed[peer]
                if union.bit_count() < len(test):
                    break
            else:
                visit(index + 1, pending)

    visit(0, fixed)
    return tuple(sorted(answers))


@lru_cache(maxsize=65536)
def support_trace(columns, roots):
    return tuple(sorted(Counter(mask_of(index for index, root in enumerate(roots) if column >> root & 1)
                                for column in columns).items()))


def extend_trace(core, source_histogram, pinned, vertices, target_roots, large_rows):
    fixed_histogram = trace(pinned, vertices, target_roots)
    difference = {word: source_histogram[word] - fixed_histogram[word] for word in range(1 << len(target_roots))}
    if any(count < 0 for count in difference.values()) or sum(difference.values()) != 6:
        return None
    if any(sum(count for word, count in difference.items() if word >> index & 1) != large_rows[root]
           for index, root in enumerate(target_roots)):
        return None
    if any(count and any(core[target_roots[index]] & mask_of(target_roots[other] for other in bits(word))
                         for index in bits(word)) for word, count in difference.items()):
        return None
    return tuple((word, count) for word, count in difference.items() if count)


def compatible_supports(columns, pair, pinned, parts, budgets):
    if any(not any(not pinned[site] & column for column in columns)
           for site in range(8, len(pinned)) if site not in pair):
        return False
    for part, limit in zip(parts, budgets):
        if sum(not any(site not in pair and not pinned[site] & column for site in part)
               for column in columns) > limit:
            return False
    return all(sum(site not in pair and not pinned[site] & column for site in range(8, len(pinned)))
               >= 7 - column.bit_count() for column in columns)


def analyze(row, anchored=False):
    label, raw_groups, residue, high_count = row
    core = decode(label)
    groups = tuple(tuple(group) for group in raw_groups)
    assert len(core) == 8 and all(neighbors.bit_count() == 2 for neighbors in core)
    assert len(groups) == 3 and all(len(group) == 6 for group in groups)
    sizes = tuple(sum(column.bit_count() for column in group) for group in groups)
    if not anchored:
        assert sorted(residue) == [0] * 4 + [2] * 4 and high_count == 6
        assert sorted(sizes) in ([10, 10, 12], [10, 11, 11])
    assert set(residue) <= {0, 1, 2} and sum(sizes) + 8 + sum(residue) == 48
    assert all(size >= 10 for size in sizes) and 8+sum(residue) >= max(sizes)
    parts = wing_orders(groups)
    part_of = {site: role for role, part in enumerate(parts) for site in part}
    all_sites = tuple(range(26))
    pinned = build_pinned(core, groups)
    assert all(pinned[site].bit_count() == 7 - residue[site] for site in range(8))
    singles = tuple(site for site in range(8) if not residue[site])
    large_rows = tuple(value + 1 for value in residue)
    small_rows = tuple(tuple(sum(column >> root & 1 for column in group) for root in range(8)) for group in groups)
    budgets = tuple(high_count - rows.count(1) for rows in small_rows)
    assert all(1 <= count <= 3 for rows in small_rows for count in rows)
    assert all(0 <= limit <= 2 for limit in budgets)
    exterior = high_count - len(singles)
    assert 0 <= exterior <= 2
    source_histogram = trace(pinned, all_sites, singles)
    comparison = []
    for omitted, (size, budget) in enumerate(zip(sizes, budgets)):
        if (not anchored and size == 10) or (anchored and budget == 0):
            roots = tuple(site for site in range(8) if small_rows[omitted][site] == 1)
            assert len(roots) == high_count
            known_sites = tuple(site for site in all_sites if site not in parts[omitted])
            comparison.append((roots, known_sites))
    if not comparison:
        return {'core': label, 'profile': sizes, 'status': 'OPEN_NO_ALL_W_ANCHOR'}
    caps = tuple((first, second, 30 - sizes[first] - sizes[second], 3-first-second)
                 for first, second in combinations(range(3), 2))
    upper = {(first, second): sum(not pinned[left] & pinned[right] for left, right in product(parts[first], parts[second]))
             for first, second, _, _ in caps}
    result = {'core': label, 'profile': sizes, 'pairs': [0] * 6, 'supports': 0, 'retained': [],
              'rectangle_upper': [upper[first, second] for first, second, _, _ in caps],
              'rectangle_floor': [floor for _, _, floor, _ in caps]}
    support_pool = None
    for pair in combinations(range(8, 26), exterior):
        if exterior == 2:
            left, right = pair
            if part_of[left] == part_of[right] or pinned[left] & pinned[right]:
                continue
        selected_roles = {part_of[site] for site in pair}
        result['pairs'][0] += 1
        if any(upper[first, second] < floor + int(remaining in selected_roles)
               for first, second, floor, remaining in caps):
            continue
        result['pairs'][1] += 1
        source = list(pinned)
        if exterior == 2:
            source[left] |= 1 << right
            source[right] |= 1 << left
        roots_and_pair = (*singles, *pair)
        maps = [tuple(order[:len(singles)] for order in isomorphisms(tuple(source), roots_and_pair, core, roots))
                for roots, _ in comparison]
        if not all(maps):
            continue
        result['pairs'][2] += 1
        required = [set((order, demand) for order in orders
                        if (demand := extend_trace(core, source_histogram, pinned, sites, order, large_rows)) is not None)
                    for orders, (_, sites) in zip(maps, comparison)]
        if not all(required):
            continue
        result['pairs'][3] += 1
        if support_pool is None:
            support_pool = enumerate_supports(core, large_rows)
            result['supports'] = len(support_pool)
        same_support = tuple(columns for columns in support_pool
                             if all(any(support_trace(columns, order) == demand for order, demand in options)
                                    for options in required))
        if not same_support:
            continue
        result['pairs'][4] += 1
        compatible = tuple(columns for columns in same_support if compatible_supports(columns, pair, pinned, parts, budgets))
        if not compatible:
            continue
        result['pairs'][5] += 1
        result['retained'].append((pair, compatible))
    return result


def load_rows(path, ids):
    chosen = set(ids)
    output = {}
    with path.open(encoding='ascii') as catalog:
        for index, line in enumerate(catalog):
            if index in chosen:
                output[index] = json.loads(line)
                if len(output) == len(chosen):
                    break
    assert output.keys() == chosen
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--anchored', action='store_true', help='Use any retained omission with no exterior d7 sites.')
    parser.add_argument('plan', type=Path)
    parser.add_argument('indices', type=int, nargs='+')
    args = parser.parse_args()
    for index, row in load_rows(args.plan, args.indices).items():
        before = process_time()
        result = analyze(row, anchored=args.anchored)
        print(json.dumps(dict(index=index, **result, cpu=round(process_time() - before, 6)), separators=(',', ':')), flush=True)
