#!/usr/bin/env python3
"""Check the coordinate-pair matching condition on one-sided supports."""

from collections import Counter
from itertools import combinations

from mask_sat import bits


def missing_pairs(kernel, degree, side, profile):
    width = degree - 1
    mask = (1 << width) - 1
    other = kernel[(1-side) * width:(2-side) * width]
    full = Counter(((row >> (side * width)) & mask) | (1 << width) for row in other)
    full.update(profile)
    seen = {edge for support in full for edge in combinations(bits(support), 2)}
    return [(first, second) for first, second in combinations(range(degree), 2) if (first, second) not in seen]


def matches(kernel, degree, side, profile):
    missing = missing_pairs(kernel, degree, side, profile)
    return len({vertex for edge in missing for vertex in edge}) == 2 * len(missing)


def encode_matching(formula, kernel, degree, side, occupants):
    width = degree - 1
    full = (1 << width) - 1
    opposite = kernel[(1-side) * width:(2-side) * width]
    fixed = [((row >> (side * width)) & full) | (1 << width) for row in opposite]
    for coordinate in range(degree):
        uncertain = []
        for other in range(degree):
            if other == coordinate:
                continue
            pair = (1 << coordinate) | (1 << other)
            if any(support & pair == pair for support in fixed):
                continue
            uncertain.append(tuple(levels[0] for support, levels in occupants.items() if support & pair == pair))
        for first, second in combinations(uncertain, 2):
            formula.add(*first, *second)
