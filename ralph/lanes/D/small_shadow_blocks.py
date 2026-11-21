#!/usr/bin/env python3
"""Hand-checkable opposite incidence blockers, replayed on fixed profiles."""

from functools import lru_cache
from itertools import combinations, combinations_with_replacement

from factor_sat import bits
from opposite_shadow import independent_shadows


@lru_cache(maxsize=8192)
def compatible_right(kernel, mask):
    possible = (1 << len(kernel)) - 1
    for coordinate in bits(mask):
        possible &= ~kernel[coordinate]
    return possible


@lru_cache(maxsize=8192)
def pair_blocked(kernel, first, second):
    if not first & second:
        return False
    possible = compatible_right(kernel, first) | compatible_right(kernel, second)
    return any(not possible & shadow
               for shadow in independent_shadows(kernel, first | second, len(kernel)))


def tests(kernel, profile):
    left = sorted(profile.elements())
    pair_ok = not any(pair_blocked(kernel, first, second) for first, second in combinations(left, 2))
    transversal_ok = True
    if all(mask.bit_count() == 1 for mask in kernel) and len(set(kernel)) == len(kernel):
        for mask in left:
            if mask.bit_count() != 1:
                continue
            needs = [target ^ mask for target in left if target != mask and target & mask]
            if not any(all(sum(1 << coordinate for coordinate in choice) & need for need in needs)
                       for choice in combinations(bits(((1 << len(kernel)) - 1) ^ mask), 3)):
                transversal_ok = False
                break
    return pair_ok, transversal_ok


def add_blockers(formula, kernel, occupants):
    pairs = 0
    for first, second in combinations_with_replacement(sorted(occupants), 2):
        if first == second and len(occupants[first]) < 2:
            continue
        if not pair_blocked(kernel, first, second):
            continue
        first_lit, second_lit = occupants[first][0], occupants[second][0]
        if first == second:
            formula.add(-occupants[first][1])
        else:
            formula.add(-first_lit, -second_lit)
        pairs += 1
    transversals = 0
    if all(mask.bit_count() == 1 for mask in kernel) and len(set(kernel)) == len(kernel):
        whole = (1 << len(kernel)) - 1
        for private, slots in occupants.items():
            if private.bit_count() != 1:
                continue
            choice = []
            for positions in combinations(bits(whole ^ private), 3):
                mask = sum(1 << coord for coord in positions)
                claim = formula.var()
                choice.append(claim)
                for other, other_slots in occupants.items():
                    if other != private and other & private and not other & mask:
                        formula.add(-claim, -other_slots[0])
            formula.add(-slots[0], *choice)
            transversals += len(choice)
    return pairs, transversals
