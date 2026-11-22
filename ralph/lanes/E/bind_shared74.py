#!/usr/bin/env python3
"""Bind a complete mixed support cover and regenerate its final LRAT input CNFs."""

import argparse
from collections import Counter, defaultdict
import csv
from itertools import combinations, combinations_with_replacement, permutations, product
from pathlib import Path
import subprocess

from batch_a11 import LIMIT, TOOLS
from involution_sat import from_graph6
from m11_sat import FastCuts, encode
from replay_shared74 import read
from rescue_a11 import direct_options


def apply_permutation(support, permutation):
    return sum(1 << destination for source, destination in enumerate(permutation) if support >> source & 1)


def support_cover(key, first_branches=None):
    core = tuple(from_graph6(key))
    order = len(core)
    cap = tuple(4-row.bit_count() for row in core)
    assert len(core) == 8 and min(cap) >= 0 and max(cap) <= 2 and sum(cap) == 10
    autos = tuple(perm for perm in permutations(range(order))
                  if all(apply_permutation(core[source], perm) == core[dest] for source, dest in enumerate(perm)))
    groups = [dict(), dict()]
    for surplus in product(*(range(bound+1) for bound in cap)):
        total = sum(surplus)
        if total in (2, 3):
            for group in direct_options(core, tuple(value+1 for value in surplus), ()):
                groups[total-2][group] = surplus
    small, large = groups
    by_cost = defaultdict(list)
    for group, cost in large.items():
        by_cost[cost].append(group)
    all_groups = small | large
    transformed = {group: tuple(tuple(sorted(apply_permutation(mask, perm) for mask in group)) for perm in autos)
                   for group in all_groups}
    if first_branches is not None:
        first_branches.update(first for first in small if first == min(transformed[first]))

    problematic = [(left, right) for left, right in combinations(range(order), 2)
                   if not (core[left] >> right & 1 or core[left] & core[right])]
    codes = {}
    for group in all_groups:
        cost = all_groups[group]
        paircode = []
        for left, right in problematic:
            has_common = any((mask >> left & 1) and (mask >> right & 1) for mask in group)
            paircode.append((has_common, cost[left] > 0, cost[right] > 0))
        codes[group] = tuple(paircode)

    cover = defaultdict(set)
    for first, second in combinations_with_replacement(sorted(small), 2):
        uses = tuple(bound-left-right for bound, left, right in zip(cap, small[first], small[second]))
        if min(uses) < 0:
            continue
        pair_images = tuple(tuple(sorted(pair)) for pair in zip(transformed[first], transformed[second]))
        if min(pair_images) != (first, second):
            continue
        stabilizer = tuple(index for index, pair in enumerate(pair_images) if pair == (first, second))
        for third, used in large.items():
            tail = tuple(remaining-amount for remaining, amount in zip(uses, used))
            if min(tail) < 0:
                continue
            for fourth in by_cost[tail]:
                if fourth < third:
                    continue
                if any(tuple(sorted((transformed[third][index], transformed[fourth][index]))) < (third, fourth)
                       for index in stabilizer):
                    continue
                quartet = (first, second, third, fourth)
                for columns in zip(*(codes[group] for group in quartet)):
                    if any(not columns[omitted][role] and not any(common for index, (common, _, _) in enumerate(columns)
                                                                  if index != omitted)
                           for omitted in range(4) for role in (1, 2)):
                        break
                else:
                    cover[quartet[:3]].add(fourth)
    print(key, 'independent support counts', len(small), len(large), 'automorphisms', len(autos), flush=True)
    return dict(cover)


def verify_cover(cover_path, key, branches_path=None):
    first_branches = set() if branches_path else None
    direct = support_cover(key, first_branches)
    stats = Counter()
    branch_projections, branch_lifts = Counter(), Counter()
    for this_key, profile, parts, omitted in read(cover_path):
        assert this_key == key and profile == [10, 10, 11, 11]
        parts = tuple(map(tuple, parts))
        omitted = tuple(map(tuple, omitted))
        assert len(omitted) == len(set(omitted)) and direct.pop(parts) == set(omitted)
        stats['projection orbits'] += 1
        stats['full support orbits'] += len(omitted)
        if branches_path:
            branch_projections[parts[0]] += 1
            branch_lifts[parts[0]] += len(omitted)
    assert not direct
    print('independent exact cover:', dict(stats), flush=True)
    if branches_path:
        with branches_path.open(encoding='ascii') as source:
            rows = [(tuple(map(int, row['branch'].split(','))), int(row['projections']), int(row['lifts']))
                    for row in csv.DictReader(source, delimiter='\t')]
        expected = [(branch, branch_projections[branch], branch_lifts[branch]) for branch in sorted(first_branches)]
        assert rows == expected
        assert branch_projections.keys() <= first_branches
        print('independent first-branch table:', len(rows), 'including',
              sum(projections == 0 for _, projections, _ in rows), 'empty', flush=True)


def verify_lrat(cover_path, trace_path, folder, fastcuts):
    required = [(index, lift) for index, lift, status, *_ in read(trace_path) if status == 'open']
    assert len(required) == len(set(required)) and set(required) == {
        tuple(map(int, proof.stem.split('_'))) for proof in folder.glob('*.lrat')}
    fast = FastCuts(fastcuts)
    pending = iter(required)
    target = next(pending, None)
    checks = 0
    for index, (key, profile, parts, omitted) in enumerate(read(cover_path)):
        while target is not None and target[0] == index:
            lift = target[1]
            groups = (*parts, omitted[lift])
            assert [sum(map(int.bit_count, group)) for group in groups] == profile
            variables, clauses, _, _ = encode(from_graph6(key), groups, (7,)*4, (7,)*24, cut_size=8, fast=fast)
            contents = (f'p cnf {variables} {len(clauses)}\n' + ''.join(
                ' '.join(map(str, (*row, 0)))+'\n' for row in clauses)).encode('ascii')
            prefix = folder/f'{index}_{lift}'
            cnf, proof = prefix.with_suffix('.cnf'), prefix.with_suffix('.lrat')
            assert cnf.read_bytes() == contents
            result = subprocess.run(['nice', '-n', '5', 'timeout', '60', 'bash', str(LIMIT), '25',
                                     str(TOOLS/'cake_lpr'), str(cnf), str(proof)], capture_output=True, check=True)
            assert b's VERIFIED UNSAT' in result.stdout.splitlines(), (index, lift)
            target = next(pending, None)
            checks += 1
    assert target is None and checks == len(required)
    print('fresh CNF and CakeLRAT replay:', checks, 'checks', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cover', type=Path)
    parser.add_argument('--key')
    parser.add_argument('--branches', type=Path)
    parser.add_argument('--trace', type=Path)
    parser.add_argument('--proofs', type=Path)
    parser.add_argument('--fastcuts', type=Path, default=Path('../r6_e11/m11_fastcuts.so'))
    args = parser.parse_args()
    assert args.key or args.proofs
    assert not args.branches or args.key
    if args.key:
        verify_cover(args.cover, args.key, args.branches)
    if args.proofs:
        verify_lrat(args.cover, args.trace, args.proofs, args.fastcuts)
