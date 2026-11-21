#!/usr/bin/env python3
"""Replay local obstructions directly on emitted side-profile multisets."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
import re

from factor_sat import bits, decode


def instances(degree, library):
    result = set()
    for size, patterns in library.items():
        for coords in combinations(range(degree), int(size)):
            lift = {mask: sum(1 << coords[index] for index in bits(mask)) for mask in range(1, 1 << len(coords))}
            for masks in patterns:
                result.add(tuple(sorted(Counter(lift[mask] for mask in masks).items())))
    return sorted(result, key=lambda pattern: (len(pattern), pattern))


def verify(file, degree, order, catalogue, library):
    name = re.fullmatch(r'k(\d+)-([01])-(shadow|local)\.profiles', file.name)
    assert name is not None, file
    index, side, mode = name.groups()
    index, side = int(index), int(side)
    width = degree - 1
    kernel = decode(catalogue[index])
    own = list(range(side * width, (side + 1) * width))
    other = range((1 - side) * width, (2 - side) * width)
    fixed = Counter(((kernel[pos] >> (side * width)) & ((1 << width) - 1)) | (1 << width) for pos in other)
    edge_count = sum(row.bit_count() for row in kernel) // 2
    failed = 0
    duplicate_triples = 0
    failed_examples = Counter()
    seen = set()
    for line in file.read_text().splitlines():
        profile = Counter(dict(tuple(map(int, entry.split(':'))) for entry in line.split()))
        canonical = tuple(sorted(profile.items()))
        assert canonical not in seen and sum(profile.values()) == order - 2 * degree
        seen.add(canonical)
        assert all(0 < mask < (1 << width) and 1 <= mask.bit_count() <= 3 and count > 0
                   for mask, count in profile.items())
        for bit, pos in enumerate(own):
            count = sum(number for mask, number in profile.items() if mask >> bit & 1)
            assert count == width - kernel[pos].bit_count()
            q = sum(kernel[neighbor].bit_count() for neighbor in bits(kernel[pos]))
            q += sum((mask.bit_count() - 1) * number for mask, number in profile.items() if mask >> bit & 1)
            assert q >= edge_count
        full = profile + fixed
        assert all(full[1 << bit] <= 1 for bit in range(degree))
        for left, right in combinations(range(degree), 2):
            assert sum(number for mask, number in full.items() if mask >> left & mask >> right & 1) <= 2
        duplicate_triples += any(mask.bit_count() == 3 and number > 1 for mask, number in full.items())
        for needed in (pattern for mask, number in full.items() for threshold in range(1, number + 1)
                       for pattern in library.get((mask, threshold), ())):
            if all(full[mask] >= number for mask, number in needed):
                assert mode != 'local', (file, line, needed)
                failed += 1
                failed_examples[sum(number for _, number in needed)] += 1
                break
    print(f'{index}\t{side}\t{mode}\t{len(seen)}\t{failed}\t{duplicate_triples}\t{dict(sorted(failed_examples.items()))}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('order', type=int)
    parser.add_argument('degree', type=int)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('obstructions', type=Path)
    parser.add_argument('files', type=Path, nargs='+')
    args = parser.parse_args()
    catalogue = args.catalogue.read_text().splitlines()
    library = defaultdict(list)
    for pattern in instances(args.degree, json.loads(args.obstructions.read_text())):
        trigger = max(pattern, key=lambda entry: (entry[1], entry[0].bit_count(), entry[0]))
        library[trigger].append(pattern)
    print('kernel\tside\tmode\tprofiles\texcluded_by_local\tduplicate_triples\tby_witness_size')
    for file in sorted(set(args.files)):
        verify(file, args.degree, args.order, catalogue, library)


if __name__ == '__main__':
    main()
