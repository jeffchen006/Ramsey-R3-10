#!/usr/bin/env python3
"""Exact overlap of two marked induced cards, followed by a rectangle filter."""

from dataclasses import dataclass
from itertools import combinations


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def graph(order, edges):
    rows = [0] * order
    for left, right in edges:
        if not (0 <= left < order and 0 <= right < order and left != right):
            raise ValueError('invalid edge')
        rows[left] |= 1 << right
        rows[right] |= 1 << left
    return tuple(rows)


def induced(rows, order):
    return tuple(sum(1 << index for index, old in enumerate(order)
                     if rows[vertex] & (1 << old)) for vertex in order)


def triangle_free(rows):
    return not any(row & rows[other] for row in rows for other in bits(row))


def independent_witness(rows, size, free=None):
    if not size:
        return 0
    if free is None:
        free = (1 << len(rows)) - 1
    while free.bit_count() >= size:
        low = free & -free
        free ^= low
        rest = independent_witness(rows, size - 1, free & ~rows[low.bit_length() - 1])
        if rest is not None:
            return low | rest
    return None


def crown_witness(rows, groups):
    if len(groups) != 4 or any(not group for group in groups):
        raise ValueError('expected four nonempty group masks')
    core = (1 << len(rows)) - 1
    for group in groups:
        if group & ~core:
            raise ValueError('group masks overlap or exceed order')
        core ^= group
    for size, scope in ((6, 0), (7, 1), (8, 3), (10, 4)):
        for mark in combinations(groups, scope):
            witness = independent_witness(rows, size, core | sum(mark))
            if witness is not None:
                return size, witness
    return None


def shared_colors(one, two, overlap, degrees):
    left = tuple(row.bit_count() for row in one[:overlap])
    right = tuple(degrees[vertex] + (row & ((1 << overlap) - 1)).bit_count()
                  - row.bit_count() for vertex, row in enumerate(two[:overlap]))
    return left, right


@dataclass(frozen=True)
class Rectangle:
    lower: tuple
    left_start: int
    right_start: int
    allowed: tuple
    left_need: tuple
    right_need: tuple

    def with_edges(self, rows):
        lower = list(self.lower)
        for index, row in enumerate(rows):
            left = self.left_start + index
            lower[left] |= row << self.right_start
            for other in bits(row):
                lower[self.right_start + other] |= 1 << left
        return tuple(lower)


def stitch(one, two, overlap, degrees):
    """Cards ordered (physical X, private L) and (physical X, private R)."""
    left_count = len(one) - overlap
    right_count = len(two) - overlap
    if min(overlap, left_count, right_count) < 1 or len(degrees) != overlap + left_count + right_count:
        raise ValueError('invalid overlap or degree length')
    overlap_mask = (1 << overlap) - 1
    if any((first ^ second) & overlap_mask for first, second in zip(one[:overlap], two[:overlap])):
        return 'sign', None
    if (not triangle_free(one) or not triangle_free(two)
            or any(row >> overlap for row in one[overlap:] + two[overlap:])):
        return 'card', None
    left_color, right_color = shared_colors(one, two, overlap, degrees)
    if left_color != right_color:
        vertex = next(index for index, pair in enumerate(zip(left_color, right_color)) if pair[0] != pair[1])
        return 'shared-degree', (vertex, left_color[vertex], right_color[vertex])
    lower = tuple(row | ((two[index] & ~overlap_mask) << left_count)
                  for index, row in enumerate(one[:overlap])) + one[overlap:] + two[overlap:]
    left_need = tuple(degrees[overlap + index] - row.bit_count()
                      for index, row in enumerate(one[overlap:]))
    right_need = tuple(degrees[len(one) + index] - row.bit_count()
                       for index, row in enumerate(two[overlap:]))
    allowed = tuple(sum(1 << index for index, other in enumerate(two[overlap:]) if not row & other)
                    for row in one[overlap:])
    return 'rectangle', Rectangle(lower, overlap, len(one), allowed, left_need, right_need)


def hall_failure(allowed, left_need, right_need):
    """None means feasible, otherwise return a checkable demand/cut receipt."""
    if min(left_need + right_need) < 0:
        return 'negative', left_need, right_need
    if sum(left_need) != sum(right_need):
        return 'totals', sum(left_need), sum(right_need)
    right_neighbors = tuple(sum(1 << index for index, row in enumerate(allowed) if row & (1 << other))
                            for other in range(len(right_need)))
    for subset in range(1, 1 << len(left_need)):
        demand = sum(left_need[index] for index in bits(subset))
        capacity = sum(min(need, (neighbors & subset).bit_count())
                       for need, neighbors in zip(right_need, right_neighbors))
        if demand > capacity:
            return 'cut', subset, demand, capacity
    return None


def supported(allowed, left_need, right_need):
    failure = hall_failure(allowed, left_need, right_need)
    if failure is not None:
        return failure, None
    possible = [0] * len(allowed)
    for index, row in enumerate(allowed):
        if not left_need[index]:
            continue
        for other in bits(row):
            if not right_need[other]:
                continue
            bit = 1 << other
            rest_rows = allowed[:index] + (row ^ bit,) + allowed[index + 1:]
            rest_left = left_need[:index] + (left_need[index] - 1,) + left_need[index + 1:]
            rest_right = right_need[:other] + (right_need[other] - 1,) + right_need[other + 1:]
            if hall_failure(rest_rows, rest_left, rest_right) is None:
                possible[index] |= bit
    return None, tuple(possible)


def matching_failure(allowed, left_need, right_need, left_scope, right_scope, size):
    """True iff no factor can contain a matching of size `size` in the scope."""
    if hall_failure(allowed, left_need, right_need) is not None:
        return True
    left_sites = tuple(index for index in bits(left_scope) if left_need[index])
    right_sites = sum(1 << other for other in bits(right_scope) if right_need[other])
    if size > min(len(left_sites), right_sites.bit_count()):
        return True
    for chosen in combinations(left_sites, max(0, size)):
        row_need = tuple(need - (index in chosen) for index, need in enumerate(left_need))

        def extend(position, free, rest_allowed):
            if position == len(chosen):
                used = right_sites ^ free
                col_need = tuple(need - ((used >> other) & 1) for other, need in enumerate(right_need))
                return hall_failure(rest_allowed, row_need, col_need) is None
            index = chosen[position]
            for other in bits(free & allowed[index]):
                bit = 1 << other
                reduced = rest_allowed[:index] + (rest_allowed[index] ^ bit,) + rest_allowed[index + 1:]
                if extend(position + 1, free ^ bit, reduced):
                    return True
            return False

        if extend(0, right_sites, allowed):
            return False
    return True
