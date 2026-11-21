#!/usr/bin/env python3
"""Whole-family upper bounds for one-sided, unique-triple mask projections."""

import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations, product
from math import comb, prod
from pathlib import Path

from mask_sat import bits, decode


def cardinality_polynomial(capacities):
    tallies = Counter(capacities)
    assert tallies.keys() <= {0, 1, 2}
    return cardinality_by_tally(tallies[1], tallies[2])


@lru_cache(maxsize=None)
def cardinality_by_tally(ones, twos):
    coefficients = [1]
    for capacity in (1,) * ones + (2,) * twos:
        expanded = [0] * (len(coefficients) + capacity)
        for index, count in enumerate(coefficients):
            for add in range(capacity + 1):
                expanded[index + add] += count
        coefficients = expanded
    return coefficients


@lru_cache(maxsize=None)
def matched_polynomial(ones, twos, uncovered, allowance):
    optional = cardinality_by_tally(ones, twos - uncovered)
    coefficients = [0] * (len(optional) + 2 * uncovered)
    for zeros in range(min(allowance, uncovered) + 1):
        positive = uncovered - zeros
        for doubled in range(positive + 1):
            multiplicity = comb(uncovered, zeros) * comb(positive, doubled)
            for index, value in enumerate(optional):
                coefficients[index + positive + doubled] += multiplicity * value
    return coefficients


@lru_cache(maxsize=4096)
def local_stars(caps, available, max_supports, allowance=None):
    counts = [[0] * (max_supports + 1) for _ in range(max_supports + 1)]
    caps = list(caps)
    eligible = tuple((left, right) for index, (left, right) in enumerate(combinations(range(len(caps)), 2))
                     if available >> index & 1)

    def visit(start, triples_used):
        ones, twos = caps.count(1), caps.count(2)
        polynomial = (cardinality_by_tally(ones, twos) if allowance is None
                      else matched_polynomial(ones, twos, twos, allowance))
        for pairs_used, count in enumerate(polynomial[:max_supports + 1 - triples_used]):
            counts[pairs_used][triples_used] += count
        if triples_used == max_supports:
            return
        for index in range(start, len(eligible)):
            left, right = eligible[index]
            if not caps[left] or not caps[right]:
                continue
            caps[left] -= 1
            caps[right] -= 1
            visit(index + 1, triples_used + 1)
            caps[left] += 1
            caps[right] += 1

    visit(0, 0)
    return counts


def cube_root_floor(integer):
    base = 0
    for shift in reversed(range((integer.bit_length() + 2) // 3)):
        trial = base | (1 << shift)
        if trial**3 <= integer:
            base = trial
    return base


class Family:
    def __init__(self, order, degree, kernel, side, matching=False):
        self.width = degree - 1
        self.order = order
        self.degree = degree
        self.kernel = kernel
        self.side = side
        self.matching = matching
        assert self.width * 2 == len(kernel) and 2 * degree < order < 6 * degree - 12
        self.outside = order - 2 * degree
        self.minimum = sum(row.bit_count() for row in kernel) // 2
        own = kernel[side * self.width:(side + 1) * self.width]
        opposite = kernel[(1 - side) * self.width:(2 - side) * self.width]
        self.cap = [[0] * self.width for _ in own]
        self.fixed = [((row >> (side * self.width)) & ((1 << self.width) - 1)) for row in opposite]
        fixed_triples = [support for support in self.fixed if support.bit_count() == 2]
        self.duplicates = len(fixed_triples) != len(set(fixed_triples))
        self.base = [sum(kernel[neighbor].bit_count() for neighbor in bits(row)) for row in own]
        self.remaining = [self.width - row.bit_count() for row in own]
        for left, right in combinations(range(self.width), 2):
            mask = (1 << left) | (1 << right)
            self.cap[left][right] = self.cap[right][left] = 2 - sum(support & mask == mask for support in self.fixed)
        assert min(map(min, self.cap)) >= 0
        self.singleton_min = max(0, (degree * self.minimum + 1) // 2
                                - (2 * degree * self.width - 3 * (order - degree - 1)) - self.fixed.count(0))

    def upper(self):
        if self.duplicates or (self.matching and self.remaining.count(self.width) > 1):
            return 0
        pairs_all = cardinality_polynomial(self.cap[left][right] for left, right in combinations(range(self.width), 2))
        stars = []
        pairs_away = []
        triples_away = []
        for coord in range(self.width):
            others = [other for other in range(self.width) if other != coord]
            allowed = sum(1 << index for index, (left, right) in enumerate(combinations(others, 2))
                          if self.cap[left][right])
            stars.append(local_stars(tuple(self.cap[coord][other] for other in others), allowed,
                                     self.remaining[coord],
                                     int(self.remaining[coord] < self.width) if self.matching else None))
            pairs_away.append(sum(self.cap[left][right] for left, right in combinations(others, 2)))
            triples_away.append(sum(bool(self.cap[left][middle] and self.cap[left][right] and self.cap[middle][right])
                                    for left, middle, right in combinations(others, 3)))
        result = 0
        incidence = sum(self.remaining)
        for singleton_mask in range(1 << self.width):
            singles = singleton_mask.bit_count()
            doubles = 3 * self.outside - incidence - 2 * singles
            triples = incidence - 2 * self.outside + singles
            if singles < self.singleton_min or not 0 <= doubles < len(pairs_all) or triples < 0:
                continue
            volumes = []
            for coord, star in enumerate(stars):
                required = self.remaining[coord] - bool(singleton_mask >> coord & 1)
                volumes.append(sum(star[on_pairs][on_triples] for on_triples in range(required + 1)
                                   if (on_pairs := required - on_triples) + 2 * on_triples + self.base[coord] >= self.minimum
                                   and 0 <= doubles - on_pairs <= pairs_away[coord]
                                   and 0 <= triples - on_triples <= triples_away[coord]))
            result += cube_root_floor(prod(volumes) * pairs_all[doubles])
        return result

    def brute_control(self):
        assert self.width <= 4
        if self.duplicates:
            return 0
        sets = [(sum(1 << vertex for vertex in support), support)
                for size in range(1, 4) for support in combinations(range(self.width), size)]
        capacities = [min((self.cap[left][right] for left, right in combinations(support, 2)), default=1)
                      for _, support in sets]
        count = 0
        for values in product(*(range((min(cap, 1) if len(support) == 3 else cap) + 1)
                                for cap, (_, support) in zip(capacities, sets))):
            if sum(values) != self.outside:
                continue
            actual = [(mask, support, val) for (mask, support), val in zip(sets, values) if val]
            if sum(val for _, support, val in actual if len(support) == 1) < self.singleton_min:
                continue
            if any(sum(val for _, support, val in actual if coord in support) != self.remaining[coord]
                   or sum((len(support) - 1) * val for _, support, val in actual if coord in support)
                   + self.base[coord] < self.minimum for coord in range(self.width)):
                continue
            if any(sum(val for mask, _, val in actual if mask >> left & 1 and mask >> right & 1) > self.cap[left][right]
                   for left, right in combinations(range(self.width), 2)):
                continue
            if self.matching:
                from pair_match import matches

                if not matches(self.kernel, self.degree, self.side, {mask: val for mask, _, val in actual}):
                    continue
            count += 1
        return count


def sat_control(order, degree, kernel, side, matching):
    from pysat.solvers import Cadical195

    from factor_sat import Formula, build_side

    with Cadical195() as solver:
        formula = Formula(solver)
        minimum = sum(row.bit_count() for row in kernel) // 2
        occupants, _, _ = build_side(formula, kernel, order, degree, minimum, 0, side, {}, True)
        if matching:
            from pair_match import encode_matching

            encode_matching(formula, kernel, degree, side, occupants)
        count = 0
        while solver.solve():
            positive = {literal for literal in solver.get_model() if literal > 0}
            formula.add(*(-literal for levels in occupants.values() for literal in levels if literal in positive))
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('order', type=int)
    parser.add_argument('degree', type=int)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--indices', type=int, nargs='+')
    parser.add_argument('--matching', action='store_true')
    args = parser.parse_args()
    print('index\tedges\tside0_upper\tside1_upper\tbest_upper' + ('\tside0_exact\tside1_exact' if args.control else ''),
          flush=True)
    catalog = args.catalogue.read_text().splitlines()
    for index in args.indices if args.indices is not None else range(len(catalog)):
        kernel = decode(catalog[index])
        families = [Family(args.order, args.degree, kernel, side, args.matching) for side in (0, 1)]
        uppers = [family.upper() for family in families]
        exact = [family.brute_control() for family in families] if args.control else []
        if args.control:
            assert exact == [sat_control(args.order, args.degree, kernel, side, args.matching) for side in (0, 1)]
        assert all(found <= bound for found, bound in zip(exact, uppers))
        print(index, families[0].minimum, *uppers, min(uppers), *exact, sep='\t', flush=True)


if __name__ == '__main__':
    main()
