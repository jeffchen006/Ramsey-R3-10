#!/usr/bin/env python3
"""Exact tiny necessary packing of the degree-six roots' low-degree neighbours."""

from collections import Counter
from functools import cache
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path
from time import process_time

from scan_private_equality import signatures

HERE = Path(__file__).resolve().parent


@cache
def subsets(roots):
    pairs = list(combinations(range(roots), 2))
    position = {edge: 1 << index for index, edge in enumerate(pairs)}
    masks = [(group, sum(position[edge] for edge in combinations(group, 2)))
             for size in range(roots, 1, -1) for group in combinations(range(roots), size)]
    return position, masks


def matchings(remaining, possible, position):
    if not remaining:
        yield 0
        return
    first, *tail = remaining
    for index, second in enumerate(tail):
        if possible(first, second):
            edge = position[first, second]
            for other in matchings(tail[:index] + tail[index + 1:], possible, position):
                yield edge | other


def packing(capacity, requirements, forbidden, groups):
    need = sum(requirements) - capacity
    if need <= 0:
        yield forbidden
        return
    valid = [(members, pairs) for members, pairs in groups
             if not (pairs & forbidden) and all(requirements[vertex] for vertex in members)]

    def extend(start, locked, unmet, savings):
        if savings <= 0:
            yield locked
            return
        if savings > sum(unmet) - max(unmet, default=0):
            return
        for index in range(start, len(valid)):
            members, pairs = valid[index]
            if pairs & locked or any(not unmet[vertex] for vertex in members):
                continue
            reduced = unmet.copy()
            for vertex in members:
                reduced[vertex] -= 1
            yield from extend(index + 1, locked | pairs, reduced, savings - len(members) + 1)

    yield from extend(0, forbidden, list(requirements), need)


def typed_pack(capacity, requirements, forbidden):
    _, groups = subsets(len(requirements[0]))
    order = sorted(range(len(capacity)), key=lambda index: capacity[index] - sum(requirements[index]))

    def work(depth, locked):
        if depth == len(order):
            return True
        index = order[depth]
        return any(work(depth + 1, used) for used in packing(capacity[index], requirements[index], locked, groups))

    return work(0, forbidden)


def direct(capacity, requirements, forbidden):
    roots = len(requirements[0])
    position, _ = subsets(roots)
    possibilities = [product(*(combinations(range(size), count) for count in spec))
                     for size, spec in zip(capacity, requirements)]
    for drawn in product(*possibilities):
        if all(sum(len(set(by_root[left]) & set(by_root[right])) for by_root in drawn)
               <= int(not (forbidden & pair)) for (left, right), pair in position.items()):
            return True
    return False


def calibrate():
    tested = 0
    for capacity in product((1, 2), repeat=2):
        for requirements in product(*(list(product(range(size + 1), repeat=3)) for size in capacity)):
            for forbidden in (0, 1):
                assert typed_pack(capacity, requirements, forbidden) == direct(capacity, requirements, forbidden)
                tested += 1
    print(f'{tested} exact colored packing controls', flush=True)


def analyse(counts, profiles):
    roots = counts[0]
    position, _ = subsets(roots)
    allowed = [profile for profile in profiles if profile[0] < roots
               and all(r <= n for r, n in zip(profile[1:], counts[1:]))]
    considered = 0
    for neighbours in combinations_with_replacement(allowed, roots):
        needs_edge = [index for index, profile in enumerate(neighbours) if profile[0]]
        if len(needs_edge) & 1:
            continue
        considered += 1
        good = lambda left, right: all(a + b <= available for a, b, available in
                                      zip(neighbours[left][1:], neighbours[right][1:], counts[1:]))
        requirements = tuple([profile[index] for profile in neighbours] for index in (1, 2))
        for forbidden in matchings(needs_edge, good, position):
            if typed_pack(counts[1:3], requirements, forbidden):
                return True, considered
    return False, considered


def main():
    start = process_time()
    calibrate()
    profiles = sorted(tuple(row.count(degree) for degree in range(6, 10)) for row in signatures()[0])
    tally = Counter()
    for line in (HERE / 'round3_cases.csv').read_text().splitlines()[1:]:
        if not line.startswith('168,'):
            continue
        _, *rest = line.split(',')
        counts = tuple(map(int, rest[:4]))
        if not counts[0]:
            continue
        survives, considered = analyse(counts, profiles)
        tally[survives] += 1
        print(f'{counts},{survives},{considered}', flush=True)
    print(f'{dict(tally)} CPU={process_time() - start:.3f}s')


if __name__ == '__main__':
    main()
