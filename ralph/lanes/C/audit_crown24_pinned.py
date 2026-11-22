#!/usr/bin/env python3
"""Literal positive/adverse deck controls and independent large-support oracle."""

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, permutations, product
import json
from pathlib import Path

from crown24_pinned import (bits, build_pinned, decode, isomorphisms, large_supports, mask_of,
                            support_trace, trace, analyze, enumerate_supports)


def core_on_cycle(order, steps):
    return tuple(sum(1 << ((site + step) % order) for step in steps) for site in range(order))


@lru_cache(maxsize=128)
def literal_supports(core, singleton_sites):
    return literal_row_supports(core, tuple(1 if site in singleton_sites else 3 for site in range(8)))


@lru_cache(maxsize=128)
def literal_row_supports(core, degrees):
    singleton_sites = tuple(site for site, degree in enumerate(degrees) if degree == 1)
    if len(singleton_sites) > 6:
        return set()
    extras = tuple(site for site, degree in enumerate(degrees) if degree != 1)
    edges = {(left, right) for left in range(8) for right in bits(core[left]) if left < right}
    roots = [{site for site in range(8) if selection >> site & 1} for selection in range(1, 256)]
    independent = [test for test in roots if not any(left in test and right in test for left, right in edges)]
    forced = tuple({site} for site in singleton_sites) + (set(),) * (6-len(singleton_sites))
    arbitrary = tuple(tuple(set(choice) for choice in combinations(range(6), degrees[site])) for site in extras)
    answer = set()
    for wildcards in product(*arbitrary):
        support = {site: {index} for index, site in enumerate(singleton_sites)}
        support.update(zip(extras, wildcards))
        if any(support[left] & support[right] for left, right in edges):
            continue
        if any(len(set.union(*(support[site] for site in test))) < len(test) for test in independent):
            continue
        masks = tuple(sorted(sum(2**site for site in forced[index] | {site for site in extras if index in support[site]})
                             for index in range(6)))
        answer.add(masks)
    return answer


def small_decks():
    parent = core_on_cycle(13, (1, -1, 5, -5))
    possible_sets = ({0, 2, 4}, {0, 2, 6}, {0, 2, 4, 6})
    checks = mutations = 0
    sources = set()
    assert not any(parent[left] & parent[right] for left, right in combinations(range(13), 2)
                   if parent[left] >> right & 1)
    assert not any(not any(parent[left] >> right & 1 for left, right in combinations(picked, 2))
                   for picked in combinations(range(13), 5))
    for omitted in possible_sets:
        assert not any(parent[left] >> right & 1 for left, right in combinations(omitted, 2))
        retained = set(range(13)) - omitted
        high = max(sum(parent[site] >> peer & 1 for peer in retained) for site in retained)
        source_sites = tuple(sorted(site for site in retained if (parent[site] & mask_of(retained)).bit_count() == high))
        assert 2 <= len(source_sites) <= 6
        for shift in range(1, 13):
            other = {(site + shift) % 13 for site in omitted}
            if other & omitted:
                continue
            kept = set(range(13)) - other
            target_sites = tuple(sorted(site for site in kept if (parent[site] & mask_of(kept)).bit_count() == high))
            planted = tuple((site + shift) % 13 for site in source_sites)
            actual = set(isomorphisms(parent, source_sites, parent, target_sites))
            literal = {image for image in permutations(target_sites)
                       if all((parent[source_sites[first]] >> source_sites[second] & 1) == (parent[image[first]] >> image[second] & 1)
                              for first, second in combinations(range(len(image)), 2))}
            assert actual == literal and planted in actual
            a_roots, b_roots = source_sites[:4], planted[:4]
            available = kept - omitted
            hist = trace(parent, retained, a_roots)
            fixed = trace(parent, available, b_roots)
            residual = Counter(sum(2**i for i, root in enumerate(b_roots) if parent[site] >> root & 1) for site in omitted)
            assert hist == fixed + residual
            wrong = list(parent)
            nonroot = next(site for site in available if site not in target_sites)
            root = b_roots[0]
            wrong[root] ^= 1 << nonroot
            wrong[nonroot] ^= 1 << root
            assert set(isomorphisms(parent, source_sites, tuple(wrong), target_sites)) == actual
            assert trace(wrong, available, b_roots) + residual != hist
            checks += 1
            mutations += 1
            sources.add(len(source_sites))
    print('C13 exact labelled deck restorations', checks, 'same-high-shape trace mutations', mutations,
          'high set sizes', sorted(sources))


def bulk_support_control():
    checks = 0
    for label, foursets in [('G?qa`_', ((0, 1, 2, 4), (0, 1, 3, 5), (0, 2, 4, 6))),
                            ('G?r@`_', ((0, 1, 4, 5), (0, 2, 4, 6)))]:
        core = decode(label)
        for singles in foursets:
            expected = literal_supports(core, singles)
            got = large_supports(core, singles)
            assert len(got) == len(expected) and set(got) == expected
            for columns in got:
                for subset in combinations(range(8), 4):
                    pinned = build_pinned(core, (columns,))
                    assert tuple(sorted(trace(pinned, range(8, 14), subset).items())) == support_trace(columns, subset)
                    checks += 1
            print('literal support masks', label, singles, len(got))
    assert checks
    print('trace incidence checks', checks)


def literal_graph6(label):
    order = ord(label[0])-63
    value = 0
    for char in label[1:]:
        value = 64*value + ord(char)-63
    value >>= 6*(len(label)-1)-order*(order-1)//2
    adjacency = [set() for site in range(order)]
    for right in reversed(range(order)):
        for left in reversed(range(right)):
            if value & 1:
                adjacency[left].add(right)
                adjacency[right].add(left)
            value >>= 1
    assert not value
    return adjacency


def literal_pilot(row, anchored=False):
    label, groups, residue, high = row
    core = literal_graph6(label)
    core_bits = tuple(sum(2**site for site in neighbors) for neighbors in core)
    wings = tuple(range(8+6*role, 14+6*role) for role in range(3))
    supports = {site: {root for root in range(8) if mask >> root & 1}
                for wing, group in zip(wings, groups) for site, mask in zip(wing, group)}
    pinned = [*map(set, core), *map(set, supports.values())]
    for site, roots in supports.items():
        for root in roots:
            pinned[root].add(site)
    sizes = tuple(sum(len(supports[site]) for site in wing) for wing in wings)
    singleton_sites = tuple(site for site in range(8) if residue[site] == 0)
    exterior = high - len(singleton_sites)
    seed = tuple(right in core[left] for left, right in combinations(singleton_sites, 2))

    def byte(neighbors, roots):
        return ''.join('1' if root in neighbors else '0' for root in roots)

    source = Counter(byte(neighbors, singleton_sites) for neighbors in pinned)
    vocab = sorted(source.keys() | {''.join(chars) for chars in product('01', repeat=len(singleton_sites))})
    possible_columns = None
    comparisons = []
    for wing, size in zip(wings, sizes):
        target_roots = tuple(site for site in range(8) if sum(site in supports[peer] for peer in wing) == 1)
        if (anchored and len(target_roots) != high) or (not anchored and size != 10):
            continue
        kept = set(range(26)) - set(wing)
        known = tuple(pinned[site] for site in kept)
        allowed = defaultdict(lambda: (set(), set()))
        for mapping in permutations(target_roots):
            image, outside = mapping[:len(singleton_sites)], mapping[len(singleton_sites):]
            if (len(outside) == 2 and outside[1] not in core[outside[0]]) or tuple(right in core[left] for left, right in combinations(image, 2)) != seed:
                continue
            pattern = tuple(byte(core[site], image) for site in outside)
            requirements, legal = allowed[pattern]
            requirements.add(tuple(image))
            difference = source.copy()
            difference.subtract(byte(neighbors, image) for neighbors in known)
            if any(difference[item] < 0 for item in vocab) or difference.total() != 6:
                continue
            if any(sum(difference[item] for item in vocab if item[index] == '1') != 1+residue[root]
                   for index, root in enumerate(image)):
                continue
            if any(difference[item] and any(image[right] in core[image[left]] and item[left] == item[right] == '1'
                                            for left, right in combinations(range(len(image)), 2)) for item in vocab):
                continue
            legal.add((tuple(image), tuple(difference[item] for item in vocab)))
        comparisons.append(allowed)
    if not comparisons:
        return None, None

    def eligible_in_each_wing(column_sets, high_pair):
        active = set(supports) - set(high_pair)
        allowed = [{site for site in active if supports[site].isdisjoint(column)} for column in column_sets]
        if set.union(*allowed) != active or any(len(peers) < 7-len(col) for peers, col in zip(allowed, column_sets)):
            return False
        miss_counts = tuple(sum(not (peers & set(wing)) for peers in allowed) for wing in wings)
        return all(misses <= high-sum(sum(root in supports[site] for site in wing) == 1 for root in range(8))
                   for wing, misses in zip(wings, miss_counts))

    positive = []
    counts = [0] * 6
    block = {site: role for role, wing in enumerate(wings) for site in wing}
    pair_capacity = {(first, second): sum(supports[left].isdisjoint(supports[right])
                                        for left, right in product(wings[first], wings[second]))
                     for first, second in combinations(range(3), 2)}
    for pair in combinations(supports, exterior):
        if exterior == 2:
            left, right = pair
            if block[left] == block[right] or not supports[left].isdisjoint(supports[right]):
                continue
        counts[0] += 1
        if any(capacity < 30-sizes[first]-sizes[second] + int(not {first, second}.issuperset({block[site] for site in pair}))
               for (first, second), capacity in pair_capacity.items()):
            continue
        counts[1] += 1
        code = tuple(byte(supports[site], singleton_sites) for site in pair)
        if not all(code in comparison for comparison in comparisons):
            continue
        counts[2] += 1
        options = tuple(comparison[code][1] for comparison in comparisons)
        if not all(options):
            continue
        counts[3] += 1
        if possible_columns is None:
            possible_columns = tuple(sorted(literal_row_supports(core_bits, tuple(1+amount for amount in residue))))
        same = []
        for columns in possible_columns:
            col_sets = tuple({root for root in range(8) if mask >> root & 1} for mask in columns)

            def matches(option):
                for roots, demand in option:
                    observed = Counter(byte(col, roots) for col in col_sets)
                    if tuple(observed[item] for item in vocab) == demand:
                        return True
                return False

            if all(matches(option) for option in options):
                same.append((columns, col_sets))
        if not same:
            continue
        counts[4] += 1
        permitted = [list(columns) for columns, col_sets in same if eligible_in_each_wing(col_sets, pair)]
        if permitted:
            counts[5] += 1
            positive.append([list(pair), permitted])
    return counts, positive


def replay_pilot(frozen, result, anchored):
    source = {int(index): row for index, row in map(json.loads, frozen.read_text().splitlines())}
    seen = set()
    totals = [0] * 6
    for printed in map(json.loads, result.read_text().splitlines()):
        index = printed['index']
        assert index not in seen
        seen.add(index)
        stage_counts, positive = literal_pilot(source[index], anchored=anchored)
        if stage_counts is None:
            assert printed['status'] == 'OPEN_NO_ALL_W_ANCHOR', index
            continue
        assert stage_counts == printed['pairs'] and positive == printed['retained'], index
        totals = [current + extra for current, extra in zip(totals, stage_counts)]
    assert seen == source.keys()
    print('independent full stage and pair/support ledger', len(seen), totals)


def anchor_synthetic():
    triple = lambda role: tuple(3 if index == role else 1 for index in range(4))
    double = lambda first, second: tuple(2 if index in (first, second) else 1 for index in range(4))
    examples = (
        ('even-six', tuple(triple(role) for role in range(4) for _ in range(2)), (6,)),
        ('b15-equal', (triple(3),) * 3 + (double(0, 3), double(0, 1), double(0, 2), double(1, 2), double(1, 2)), (5, 6)),
        ('b15-ten', (triple(3),) * 3 + (double(1, 3),) + (double(0, 2),) * 2 + (double(1, 2),) * 2, (6,)),
        ('b15-two-tens', (triple(3),) * 3 + (triple(2), double(2, 3), double(0, 1), double(0, 2), double(1, 2)), (6,)),
    )
    states = Counter()
    for label in ('G?qa`_', 'G?r@`_'):
        core = decode(label)
        for name, by_site, high_values in examples:
            degrees = tuple(zip(*by_site))
            possible = []
            for vector in degrees:
                got = enumerate_supports(core, vector)
                literal = literal_row_supports(core, vector)
                assert set(got) == literal
                if not got:
                    break
                possible.append(got)
            if len(possible) != 4:
                continue
            for high in high_values:
                retained = tuple(choices[0] for choices in possible[:3])
                residue = tuple(degree-1 for degree in degrees[3])
                row = (label, retained, residue, high)
                result = analyze(row, anchored=True)
                stage, kept = literal_pilot(row, anchored=True)
                if stage is None:
                    assert result['status'] == 'OPEN_NO_ALL_W_ANCHOR'
                    states['no anchor'] += 1
                else:
                    assert result['pairs'] == stage and json.loads(json.dumps(result['retained'])) == kept
                    states[high-degrees[3].count(1)] += 1
                print('synthetic geometry only', label, name, high, result.get('status', stage), 'D supports', len(possible[3]))
    assert set(states) == {0, 1, 2, 'no anchor'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--anchored', action='store_true')
    parser.add_argument('pilot', type=Path, nargs='*')
    args = parser.parse_args()
    if args.pilot:
        assert len(args.pilot) == 2
        replay_pilot(*args.pilot, args.anchored)
    else:
        small_decks()
        bulk_support_control()
        anchor_synthetic()
