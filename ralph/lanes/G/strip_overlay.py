#!/usr/bin/env python3
"""Generalize A's support sieve to paired windows of orders 25 through 27."""

from argparse import ArgumentParser
from collections import Counter
from functools import reduce
from itertools import product
from operator import or_
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'A'))
from filter_strip_supports import assignments, bounded_degrees, controls, gap_list, hall, vertices
from residue_bundle import parse_graph6


def overlay_terms(adj, sides, stars, centers, common, exclusive, survived):
    shared = len(common)
    length = len(survived)
    width = 6 - shared
    assert width == len(exclusive[0]) == len(exclusive[1])
    left_first, right_first = ((star, *(anchor for anchor in side if anchor != star))
                               for side, star in zip(sides, stars, strict=True))
    choices = (left_first, right_first)
    known = tuple(tuple(sum(1 << index for index, anchor in enumerate(side[:4]) if adj[vertex] >> anchor & 1)
                        for side in choices) for vertex in survived)
    gaps = tuple(sorted(gap_list(4, 4, [support[index] for support in known]),
                        key=lambda support: tuple(sorted(choices[index][col] for col in vertices(support))))
                 for index in (0, 1))
    assert all(len(part) == width for part in gaps)
    target_deficit = sum(mask.bit_count() for mask in adj) // 2 - 49 - 9*shared
    if not 0 <= target_deficit <= 12 + width**2:
        return

    forced = tuple(reduce(or_, part, 0) for part in gaps)
    surviving_mask = (1 << length) - 1
    first_exclusive = ((1 << width) - 1) << length
    second_exclusive = first_exclusive << width
    whole = (1 << 28) - 1
    potential_neighbors = [sum(1 << index for index, other in enumerate(survived) if adj[vertex] >> other & 1)
                           | (whole ^ surviving_mask) for vertex in survived]
    potential_neighbors += [surviving_mask | second_exclusive] * width
    potential_neighbors += [surviving_mask | first_exclusive] * width
    potential_neighbors += [surviving_mask] * shared
    existing_degree = [adj[vertex].bit_count() for vertex in survived]
    passed = set()
    pivot_stats = Counter()

    for left_leaf, right_leaf in product(range(1, 4), repeat=2):
        if not (forced[0] >> left_leaf & 1 and forced[1] >> right_leaf & 1):
            continue
        central = tuple((16, 16, 16, 16, *(16 | (1 << index) for index in range(1, 4) if index != leaf))
                        for leaf in (left_leaf, right_leaf))
        for left, right, shared_types in assignments(known, gaps, central, shared, 5):
            canonical = tuple(sorted(shared_types))
            assignment = (*left, *right, *canonical)
            if assignment in passed:
                continue
            support = tuple(first | (second << 5) for first, second in (*known, *assignment))
            columns = [sum(1 << idx for idx, signature in enumerate(support) if signature >> bit & 1) for bit in range(10)]
            allowed = []
            for idx, mask in enumerate(support):
                not_adjacent = reduce(or_, (columns[bit] for bit in vertices(mask)), 0)
                allowed.append(potential_neighbors[idx] & ~not_adjacent)
            if any(not (columns[bit] >> idx & 1 or allowed[idx] & columns[bit]
                        or (bit in (0, 5) and columns[5-bit] >> idx & 1))
                   for idx in range(28) for bit in range(10)):
                continue
            cap_cross = sum((allowed[idx] & second_exclusive).bit_count() for idx in vertices(first_exclusive))
            possible_more = [mask & ~surviving_mask if idx < length else mask for idx, mask in enumerate(allowed)]
            minima = [1 if mask & columns[4] & columns[9] else 2 for mask in allowed[:length]]
            minima += [1] * (2 * width) + [0] * shared
            degrees = existing_degree + [mask.bit_count() for mask in support[length:]]
            if not any(width <= target_deficit - deficit <= cap_cross for profile in ((6, 0), (5, 2))
                       for deficit in bounded_degrees(support, possible_more, degrees, minima, length, target_deficit, profile)):
                continue
            if not hall([whole & ~((1 << idx) | mask) for idx, mask in enumerate(allowed)], support, 5, pivot_stats):
                continue
            passed.add(assignment)
            out = []
            for vertex, mask_pair in zip((*exclusive[0], *exclusive[1], *common), assignment, strict=True):
                for side, mask in zip(choices, mask_pair, strict=True):
                    for index, anchor in enumerate(side[:4]):
                        out.append((vertex, anchor, bool(mask >> index & 1)))
            yield tuple(out)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--control', action='store_true')
    args = parser.parse_args()
    if args.control:
        controls()


if __name__ == '__main__':
    main()
