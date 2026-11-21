#!/usr/bin/env python3
"""Root a max12 forest at an edge maximizing the number of 2/2 squares."""

from collections import Counter
from itertools import combinations

from kernel_projection import bits


def isolated_edges(kernel):
    return sum(row.bit_count() == 1 and kernel[row.bit_length() - 1].bit_count() == 1
               for row in kernel) // 2


def exact_square_counts(graph):
    counts = {}
    for first, row in enumerate(graph):
        for second in bits(row & ~((1 << (first + 1)) - 1)):
            counts[first, second] = sum(
                (row & graph[other]).bit_count() == 2 and (graph[second] & graph[corner]).bit_count() == 2
                for other in bits(graph[second] ^ (1 << first))
                for corner in bits(row & graph[other] & ~(1 << second)))
    return counts


def check_pair_formula():
    for fixed in (0, 1):
        for count_two in range(3):
            for count_three in range(3):
                shared = fixed + count_two + count_three
                if 1 <= shared <= 2:
                    exact = shared == 1 and count_two == 1
                    envelope = max(0, 2 - 2 * fixed - count_two - 2 * count_three)
                    assert envelope == exact, (fixed, count_two, count_three)


def append_q22(model, kernel, degree, maximum=None):
    width = degree - 1
    assert len(kernel) == 2 * width
    t_value = isolated_edges(kernel) if maximum is None else maximum
    seen = {(terms, rhs) for terms, rhs, _ in model.rows}
    for anchor, row in enumerate(kernel):
        side = ((1 << width) - 1) << (anchor // width * width)
        fixed = int(row.bit_count() == 1 and kernel[row.bit_length() - 1].bit_count() == 1)
        slack = t_value - fixed
        if slack < 0:
            model.rows.append(((), -1, f'q22-fixed:{anchor}'))
            continue
        rows = {}
        for other in bits(side ^ (1 << anchor)):
            if row & kernel[other]:
                continue
            pair = (1 << anchor) | (1 << other)
            rows[other] = Counter()
            for mask, col in model.p.items():
                if mask & pair == pair:
                    rows[other][col] -= (mask & side).bit_count() - 1
        for size in range(slack + 1, len(rows) + 1):
            rhs = slack - 2 * size
            for partners in combinations(rows, size):
                terms = Counter()
                for other in partners:
                    terms.update(rows[other])
                normalized = tuple(sorted(terms.items()))
                if (normalized, rhs) not in seen:
                    seen.add((normalized, rhs))
                    label = ','.join(map(str, partners))
                    model.rows.append((normalized, rhs, f'q22-root-cap:{anchor}:{label}'))
    return t_value
