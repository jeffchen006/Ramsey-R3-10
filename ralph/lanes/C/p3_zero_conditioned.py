"""Exact integer replay of capacity bounds conditioned on zero masks."""

import argparse
from collections import Counter, defaultdict
from functools import reduce
from itertools import combinations
import json
from math import gcd, lcm
from pathlib import Path

from p3_high_f import NO_HOLE, classify, filter_target, layouts
from p3_singleton_cover import attachment_masks, bitset, capacity_rows, independent_levels, zero_compatibility
from path_three_top import plant


def condition(masks, common, blockers, base_rows, zeroes, degree, order):
    avoid = {mask: bitset(index for index, blocker in enumerate(blockers) if not mask & blocker) for mask in masks}
    forced = {pair for pair in combinations(range(len(zeroes)), 2) if avoid[zeroes[pair[0]]] & avoid[zeroes[pair[1]]]}
    groups = defaultdict(list)
    mandatory, impossible = ([[] for _ in zeroes] for _ in range(2))
    for index, mask in enumerate(masks):
        if not mask & common:
            continue
        joins = {slot for slot, zero in enumerate(zeroes) if avoid[mask] & avoid[zero]}
        if any(mask & zeroes[slot] for slot in joins) or any(set(edge) <= joins for edge in forced):
            continue
        groups[mask & ~common, (mask & common).bit_count()].append(index)
        for slot, zero in enumerate(zeroes):
            if slot in joins:
                mandatory[slot].append(index)
            if mask & zero:
                impossible[slot].append(index)
    zero_indices = [masks.index(mask) for mask in zeroes]
    rows = {name: (bound - sum(index in indices for index in zero_indices), indices)
            for name, (bound, indices) in base_rows.items()}
    for slot, zero in enumerate(zeroes):
        need = degree - zero.bit_count()
        known = sum(slot in edge for edge in forced)
        possible = sum(slot != other and not zero & second for other, second in enumerate(zeroes))
        rows[f'no-edge-zero:{slot}'] = (order - len(zeroes) - need + possible, impossible[slot])
        rows[f'forced-edge-zero:{slot}'] = (need - known, mandatory[slot])
    scale = lcm(*(len(group) for group in groups.values()))
    orbit = {index: (number, scale // len(group))
             for number, group in enumerate(groups.values()) for index in group}
    best = {}
    for name, (bound, indices) in rows.items():
        coefficients = Counter()
        for index in indices:
            if index in orbit:
                number, weight = orbit[index]
                coefficients[number] += weight
        if not coefficients and bound >= 0:
            continue
        divisor = reduce(gcd, coefficients.values(), abs(scale * bound)) or 1
        key = tuple(sorted((number, weight // divisor) for number, weight in coefficients.items()))
        bound = scale * bound // divisor
        if key not in best or bound < best[key][1]:
            best[key] = name, bound
    return {name: (bound, key) for key, (name, bound) in best.items()}, tuple(groups)


def verify(rows, goal, target, witness):
    scale = witness['scale']
    assert type(scale) is int and scale > 0
    rhs = 0
    got = [0] * len(goal)
    for name, weight in witness['weights'].items():
        assert type(weight) is int and weight > 0
        bound, coefficients = rows[name]
        rhs += weight * bound
        for index, value in coefficients:
            got[index] += weight * value
    assert rhs < scale * target and all(value >= scale * need for value, need in zip(got, goal))
    return rhs, scale


def propose(rows, goal, target):
    from scipy.optimize import linprog
    from scipy.sparse import csc_array, vstack

    bounds, products, coordinates, values = [], [], [], []
    for number, (bound, terms) in enumerate(rows.values()):
        bounds.append(bound)
        for index, coefficient in terms:
            products.append(index)
            coordinates.append(number)
            values.append(-1. * coefficient)
    matrix = csc_array((values, (products, coordinates)), shape=(len(goal), len(rows)))
    options = {'time_limit': 2., 'threads': 1}
    solved = linprog(bounds, A_ub=matrix, b_ub=[-value for value in goal], method='highs', options=options)
    if solved.status == 3:
        solved = linprog([1] * len(rows), A_ub=vstack((matrix, csc_array([bounds]))),
                         b_ub=[-value for value in goal] + [target - 0.05], method='highs', options=options)
    if solved.status != 0:
        return f'status {solved.status}', None
    status = sum(value * bound for value, bound in zip(solved.x, bounds))
    if status < target - 1e-7:
        for scale in (1, 2, 3, 4, 6, 12, 24, 60, 120, 600, 1440, 10000, 100000):
            witness = {'scale': scale, 'weights': {name: round(value * scale) for name, value in zip(rows, solved.x)
                                                   if round(value * scale) > 0}}
            try:
                verify(rows, goal, target, witness)
            except AssertionError:
                continue
            return status, witness
    return status, None


def calibrate():
    core, graph, full = plant()
    common = graph[-1] & graph[-2] & graph[-3]
    levels = independent_levels(graph)
    masks = attachment_masks(graph, levels, 6, 3, 4, 4)
    actual = [full[vertex] >> len(core) for vertex in range(len(core))]
    base = capacity_rows(graph, levels, masks, 6, 6, 4, len(core), strong=True)
    rows, groups = condition(masks, common, levels[5], base, [mask for mask in actual if not mask & common], 6, len(core))
    counts = Counter((mask & ~common, (mask & common).bit_count()) for mask in actual if mask & common)
    assert counts.keys() <= set(groups)
    assert all(sum(coefficient * counts[groups[index]] for index, coefficient in entries) <= bound
               for bound, entries in rows.values())
    print('C21 calibrated conditional rows', len(rows), 'orbits', len(groups))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('witnesses', type=Path)
    parser.add_argument('--discover', action='store_true')
    parser.add_argument('--max-q', type=int, default=2)
    args = parser.parse_args()
    calibrate()
    witnesses = {} if args.discover else json.loads(args.witnesses.read_text())
    results = {}
    for size, key in layouts(9, 6, 4, 8, 16, 18):
        if NO_HOLE in key[1:]:
            continue
        graph = classify(9, 6, 4, key)
        if filter_target(graph) != 'pass':
            continue
        levels = independent_levels(graph)
        masks = attachment_masks(graph, levels, 9, 3, 5, 5)
        common = bitset(range(6, 10))
        zero_masks, _, _, patterns = zero_compatibility(masks, common, levels[8], 22)
        assert patterns is not None
        base = capacity_rows(graph, levels, masks, 9, 9, 6, 22, strong=True)
        stats = Counter()
        slug = ':'.join(map(str, (key[0], *key[1], *key[2])))
        for pattern in patterns:
            if len(pattern) > args.max_q:
                stats['defer'] += 1
                continue
            identifier = slug + '/' + ','.join(map(str, pattern))
            if not args.discover and identifier not in witnesses:
                stats['unproved'] += 1
                continue
            rows, groups = condition(masks, common, levels[8], base, [zero_masks[index] for index in pattern], 9, 22)
            goal, target = [int(level == 1) for _, level in groups], 20 - 2 * len(pattern)
            outcome, witness = (propose(rows, goal, target) if args.discover else ('replay', witnesses.pop(identifier)))
            if witness:
                results[identifier] = witness
                print('checked', identifier, 'q', len(pattern), 'integer bound', verify(rows, goal, target, witness))
                stats['checked'] += 1
            else:
                print('no exact witness', identifier, 'q', len(pattern), 'LP', outcome)
                stats['unproved'] += 1
        print('layout', 45 + size, slug, sorted(stats.items()))
    assert not witnesses
    if args.discover:
        args.witnesses.write_text(json.dumps(results, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
