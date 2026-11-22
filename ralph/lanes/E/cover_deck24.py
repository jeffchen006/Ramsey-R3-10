#!/usr/bin/env python3
"""Independent column-first generation of labelled e8/bmax16 rosters."""

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, permutations, product
import json
from pathlib import Path
from time import process_time

from involution_sat import from_graph6
from residue23 import canon


def masks_of_size(size):
    return tuple(sum(1 << v for v in row) for row in combinations(range(8), size))


def membership(mask):
    return tuple(v for v in range(8) if mask >> v & 1)


def factory(core):
    independent = tuple(word for word in range(256) if all(not (core[v] & word) for v in membership(word)))

    @lru_cache(None)
    def columns_of(degrees):
        singles = tuple(v for v in range(8) if degrees[v] == 1)
        if len(singles) > 6:
            return ()
        high_sites = tuple(v for v in range(8) if degrees[v] > 1)
        high_mask = sum(1 << v for v in high_sites)
        allowed = [tuple(word for word in independent if word >> v & 1 and word & ~(high_mask | 1 << v) == 0)
                   for v in singles]
        filler = tuple(word for word in independent if word & ~high_mask == 0)
        checks = tuple(word for word in independent if word & high_mask and word.bit_count() >= 2)
        result = []
        for non_single in combinations_with_replacement(filler, 6-len(singles)):
            for single in product(*allowed):
                columns = (*non_single, *single)
                if any(sum(column >> v & 1 for column in columns) != degrees[v] for v in high_sites):
                    continue
                if any(sum(bool(word & column) for column in columns) < word.bit_count() for word in checks):
                    continue
                result.append(tuple(sorted(columns)))
        assert len(result) == len(set(result))
        return tuple(sorted(result))

    return columns_of


def generate(key, offset, stride, stream):
    core = tuple(from_graph6(key))
    assert len(core) == 8 and {row.bit_count() for row in core} == {2}
    core_edges = frozenset((v, w) for v, w in combinations(range(8), 2) if core[v] >> w & 1)
    automorphisms = [perm for perm in permutations(range(8))
                     if frozenset(tuple(sorted((perm[v], perm[w]))) for v, w in core_edges) == core_edges]
    transports = [{word: sum(1 << perm[v] for v in membership(word)) for word in range(256)} for perm in automorphisms]
    columns_of = factory(core)
    tally = Counter()
    norms = set()
    for keep in masks_of_size(4)[offset::stride]:
        keep_sites = membership(keep)
        norm = min(perm[keep] for perm in transports)
        emit = tuple(perm for perm in transports if perm[keep] == norm)
        residue = tuple(0 if norm >> v & 1 else 2 for v in range(8))

        @lru_cache(None)
        def images(columns):
            return tuple(tuple(sorted(perm[word] for word in columns)) for perm in emit)

        buckets = defaultdict(list)
        for extras in product(range(3), repeat=4):
            if sum(extras) not in (2, 3, 4) or sum(bool(val) for val in extras) < 2:
                continue
            physical = dict(zip(keep_sites, extras, strict=True))
            row = tuple(1+physical.get(v, 0) for v in range(8))
            singles = sum(1 << v for v in range(8) if row[v] == 1)
            shape = canon(core, singles) if singles.bit_count() == 6 else None
            cols = columns_of(row)
            if cols:
                buckets[sum(extras)].append((extras, shape, cols))
        for profile in ((2, 2, 4), (2, 3, 3)):
            lookup = {extra: (shape, columns) for extra, shape, columns in buckets[profile[2]]}
            for left, middle in product(buckets[profile[0]], buckets[profile[1]]):
                complement = tuple(2-first-second for first, second in zip(left[0], middle[0], strict=True))
                right = lookup.get(complement)
                if right is None:
                    continue
                if len({shape for shape in (left[1], middle[1], right[0]) if shape is not None}) != 1:
                    continue
                for groups in product(left[2], middle[2], right[1]):
                    if any(profile[i] == profile[i+1] and groups[i] > groups[i+1] for i in (0, 1)):
                        continue
                    variants = zip(*(images(group) for group in groups), strict=True)
                    if profile[0] == profile[1]:
                        canonical = min((*sorted((first, second)), third) for first, second, third in variants)
                    else:
                        canonical = min((first, *sorted((second, third))) for first, second, third in variants)
                    norms.add((canonical, residue))
                    tally[profile] += 1
    for groups, residue in sorted(norms):
        print(json.dumps((key, groups, residue, 6), separators=(',', ':')), file=stream)
    print(key, 'independent column-first', offset, stride, dict(tally), len(norms),
          process_time(), 'CPU-s', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('key')
    parser.add_argument('output', type=Path)
    parser.add_argument('--offset', type=int, required=True)
    parser.add_argument('--stride', type=int, required=True)
    args = parser.parse_args()
    assert 0 <= args.offset < args.stride
    with args.output.open('x', encoding='ascii') as output:
        generate(args.key, args.offset, args.stride, output)
