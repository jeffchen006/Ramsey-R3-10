#!/usr/bin/env python3
"""Exact W-support orbits for four saturated, six-vertex attachments."""

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, permutations, product
import json
from pathlib import Path

from cubic32 import automorphisms, mask_image
from involution_cores import bits, graph
from involution_sat import from_graph6, witnesses


PROFILES = ((10, 10, 10, 12), (10, 10, 11, 11))


class Supports:
    def __init__(self, core, width):
        self.core = tuple(core)
        self.width = width
        self.alpha = tuple(pick for size in range(2, len(core)+1)
                           for pick in witnesses(core, (1 << len(core))-1, size))
        self.pairs = tuple((left, right) for left, right in combinations(range(len(core)), 2)
                           if not core[left] >> right & 1 and not core[left] & core[right])
        self.pairmask = (1 << len(self.pairs))-1

    @lru_cache(None)
    def options(self, degree):
        core, width = self.core, self.width
        singles = [vertex for vertex, count in enumerate(degree) if count == 1]
        if len(singles) > width or not all(1 <= count <= width for count in degree):
            return ()
        extra = sorted((vertex for vertex, count in enumerate(degree) if count > 1),
                       key=lambda vertex: (-degree[vertex], -core[vertex].bit_count(), vertex))
        rows = [0] * len(core)
        for slot, vertex in enumerate(singles):
            rows[vertex] = 1 << slot
        tests = defaultdict(list)
        for independent in self.alpha:
            for vertex in reversed(extra):
                if independent >> vertex & 1:
                    tests[vertex].append(tuple(bits(independent)))
                    break
        complete = set()

        def visit(index):
            if index == len(extra):
                complete.add(tuple(sorted(sum(1 << vertex for vertex, row in enumerate(rows) if row >> slot & 1)
                                          for slot in range(width))))
                return
            vertex = extra[index]
            allowed = (1 << width)-1
            for other in bits(core[vertex]):
                allowed &= ~rows[other]
            for selection in combinations(tuple(bits(allowed)), degree[vertex]):
                rows[vertex] = sum(1 << slot for slot in selection)
                for test in tests[vertex]:
                    union = 0
                    for actor in test:
                        union |= rows[actor]
                    if union.bit_count() < len(test):
                        break
                else:
                    visit(index+1)
            rows[vertex] = 0

        visit(0)
        return tuple(sorted(complete))

    @lru_cache(None)
    def info(self, group):
        rows = tuple(sum(1 << slot for slot, column in enumerate(group) if column >> vertex & 1)
                     for vertex in range(len(self.core)))
        degree = tuple(row.bit_count() for row in rows)
        common, protected = 0, 0
        for index, (left, right) in enumerate(self.pairs):
            if rows[left] & rows[right]:
                common |= 1 << index
                if min(degree[left], degree[right]) >= 2:
                    protected |= 1 << index
        return tuple(count-1 for count in degree), common, protected

    def catalog(self, size, cap):
        surplus = size - len(self.core)
        entries = defaultdict(list)
        for index in product(*(range(remain+1) for remain in cap)):
            if sum(index) == surplus:
                entries[index].extend(self.options(tuple(count+1 for count in index)))
        return tuple(sorted(group for groups in entries.values() for group in groups))

    def admissible(self, groups):
        single, twice, protected = 0, 0, 0
        for group in groups:
            _, common, safe = self.info(group)
            twice |= single & common
            single |= common
            protected |= safe
        return twice | protected == self.pairmask


@lru_cache(None)
def image(group, perm):
    return tuple(sorted(mask_image(column, perm) for column in group))


def group_image(groups, profile, perm):
    return tuple(sorted((image(group, perm) for group, size in zip(groups, profile) if size == value))[rank]
                 for value, rank in ((size, profile[:index].count(size)) for index, size in enumerate(profile)))


def triples(core, support, profile, cap, entries, autos):
    small, middle, third, last = profile
    assert small == middle <= third <= last
    all_small = entries[small]
    for first in all_small:
        first_cost, _, _ = support.info(first)
        for second in all_small:
            if second < first:
                continue
            second_cost, _, _ = support.info(second)
            if any(left+right > remain for remain, left, right in zip(cap, first_cost, second_cost)):
                continue
            pair_orbit = tuple((tuple(sorted((image(first, perm), image(second, perm)))), perm) for perm in autos)
            if any(pair < (first, second) for pair, _ in pair_orbit) and third != small:
                continue
            for final in entries[third]:
                if third == small and final < second:
                    continue
                final_cost, _, _ = support.info(final)
                residue = tuple(remain-left-right-curr for remain, left, right, curr
                                in zip(cap, first_cost, second_cost, final_cost))
                if min(residue) < 0:
                    continue
                if third == small:
                    same_orbit = lambda pair, perm: tuple(sorted((*pair, image(final, perm))))
                    if any(same_orbit(pair, perm) < (first, second, final) for pair, perm in pair_orbit):
                        continue
                    stabilizer = tuple(perm for pair, perm in pair_orbit
                                       if same_orbit(pair, perm) == (first, second, final))
                else:
                    block = tuple(perm for pair, perm in pair_orbit if pair == (first, second))
                    if any(image(final, perm) < final for perm in block):
                        continue
                    stabilizer = tuple(perm for perm in block if image(final, perm) == final)
                assert sum(residue) == last-len(core)
                yield (first, second, final), residue, stabilizer


def windows(key, profiles=PROFILES, limit=None):
    core = from_graph6(key)
    autos = tuple(automorphisms(core))
    assert len(core) == 8 and sum(row.bit_count() for row in core) == 22
    cap = tuple(4-row.bit_count() for row in core)
    support = Supports(core, 6)
    entries = {size: support.catalog(size, cap) for size in (10, 11)}
    print(key, 'autos', len(autos), 'local', {size: len(groups) for size, groups in entries.items()}, flush=True)
    stats = Counter()
    for profile in profiles:
        for parts, residue, stabilizer in triples(core, support, profile, cap, entries, autos):
            stats[profile, 'projection'] += 1
            options = support.options(tuple(count+1 for count in residue))
            stats[profile, 'nonempty'] += bool(options)
            viable = []
            for omitted in options:
                if not support.admissible((*parts, omitted)):
                    continue
                if any(image(omitted, perm) < omitted for perm in stabilizer):
                    continue
                if profile[2] == profile[3] and any(group_image((*parts, omitted), profile, perm) < (*parts, omitted)
                                                        for perm in autos):
                    continue
                viable.append(omitted)
            if not viable:
                continue
            stats[profile, 'dominated'] += 1
            stats[profile, 'lifted'] += len(viable)
            yield key, profile, parts, viable
            if limit is not None and sum(count for (prof, stage), count in stats.items() if stage == 'dominated') >= limit:
                print(key, 'PILOT STOP', sorted(stats.items()), flush=True)
                return
    print(key, 'COMPLETE', sorted(stats.items()), flush=True)
    image.cache_clear()
    Supports.options.cache_clear()
    Supports.info.cache_clear()


def core_cover(keys):
    assert len(keys) == len(set(keys))
    found = set()
    for key in keys:
        core = from_graph6(key)
        assert len(core) == 8 and min(map(int.bit_count, core)) == 2 and max(map(int.bit_count, core)) <= 4
        assert sum(map(int.bit_count, core)) == 22
        assert not any(core[left] & core[right] for left in range(8) for right in bits(core[left]))
        orbit = set()
        for perm in permutations(range(8)):
            if mask_image(core[perm.index(0)], perm) != 6:
                continue
            current = [0] * 8
            for vertex, row in enumerate(core):
                current[perm[vertex]] = mask_image(row, perm)
            orbit.add(tuple(current))
        assert orbit and not found & orbit
        found |= orbit
    remaining = [(left, right) for left, right in combinations(range(1, 8), 2) if right > 2]
    direct = set()
    for more in combinations(remaining, 9):
        rows = graph(8, [(0, 1), (0, 2), *more])
        if all(2 <= row.bit_count() <= 4 for row in rows) and not any(
                rows[left] & rows[right] for left in range(8) for right in bits(rows[left])):
            direct.add(tuple(rows))
    assert found == direct
    print('complete e11 core cover:', len(keys), len(found), flush=True)


def calibrate():
    counts = Counter()
    for order in (3, 4):
        for matrix in range(1 << (order-1)):
            core = graph(order, [(vertex, vertex+1) for vertex in range(order-1) if matrix >> vertex & 1])
            width = 3
            support = Supports(core, width)
            for degree in product(range(1, width+1), repeat=order):
                if sum(degree) > order+3:
                    continue
                expected = set()
                for rows in product(*(tuple(combinations(range(width), val)) for val in degree)):
                    edges = {(left, right) for left, right in combinations(range(order), 2) if core[left] >> right & 1}
                    edges.update((vert, order+slot) for vert, row in enumerate(rows) for slot in row)
                    if any(all(pair in edges for pair in combinations(subset, 2))
                           for subset in combinations(range(order+width), 3)):
                        continue
                    if any(all(pair not in edges for pair in combinations(subset, 2))
                           for subset in combinations(range(order+width), width+1)):
                        continue
                    expected.add(tuple(sorted(sum(1 << vert for vert, row in enumerate(rows) if slot in row)
                                              for slot in range(width))))
                actual = support.options(degree)
                assert set(actual) == expected and len(actual) == len(expected)
                counts['support_vectors'] += 1
                counts['local_supports'] += len(expected)
    core = graph(4, [(0, 1), (1, 2), (2, 3)])
    support = Supports(core, 3)
    autos = tuple(automorphisms(core))
    cap = (2, 2, 2, 2)
    for profile in ((5, 5, 6, 8), (5, 5, 5, 9)):
        entries = {size: support.catalog(size, cap) for size in profile[:3]}
        brute = set()
        for left, right, third in product(*(entries[size] for size in profile[:3])):
            costs = [support.info(group)[0] for group in (left, right, third)]
            if all(sum(values) <= upper for values, upper in zip(zip(*costs), cap)):
                brute.add(min(group_image((left, right, third), profile[:3], perm) for perm in autos))
        generated = {parts for parts, _, _ in triples(core, support, profile, cap, entries, autos)}
        assert generated == brute and brute, (profile, len(generated), len(brute))
        counts['orbit_projections'] += len(brute)
    print('control matches independent labeled supports and all projection orbits:', dict(counts), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    sub.add_parser('calibrate')
    target = sub.add_parser('census')
    target.add_argument('keys', type=Path)
    target.add_argument('manifest', type=Path)
    target.add_argument('--core', type=int)
    target.add_argument('--profile', type=int, choices=(0, 1))
    target.add_argument('--limit', type=int)
    args = parser.parse_args()
    if args.mode == 'calibrate':
        calibrate()
    else:
        keys = args.keys.read_text(encoding='ascii').splitlines()
        core_cover(keys)
        if args.core is not None:
            keys = keys[args.core:args.core+1]
            assert keys
        with args.manifest.open('w', encoding='ascii') as out:
            profiles = PROFILES if args.profile is None else (PROFILES[args.profile],)
            for key in keys:
                for entry in windows(key, profiles=profiles, limit=args.limit):
                    print(json.dumps(entry, separators=(',', ':')), file=out)


if __name__ == '__main__':
    main()
