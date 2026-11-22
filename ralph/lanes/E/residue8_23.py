#!/usr/bin/env python3
"""Project the e8 largest-incidence-16 profiles onto the three other wings."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations, combinations_with_replacement, product
import json
from pathlib import Path
from time import process_time

from cubic32 import automorphisms, mask_image
from deficit73 import mask
from involution_sat import from_graph6
from m11_support import Supports, image
from residue23 import canon, degree_vector


PROFILES = ((10, 10, 12), (10, 11, 11))


def admissible(core, groups, residue, high):
    assert sum(residue) == 8 and set(residue) == {0, 2} and high == 6
    rows = [degree_vector(group, 8) for group in groups]
    assert tuple(sorted(map(sum, rows))) in PROFILES
    assert all(sum(row[vertex]-1 for row in rows)+residue[vertex] == 2 for vertex in range(8))
    roots = [mask(vertex for vertex, count in enumerate(row) if count == 1) for row in rows]
    if any(not 4 <= root.bit_count() <= 6 for root in roots):
        return False
    full_high_shapes = {canon(core, root) for root in roots if root.bit_count() == 6}
    return len(full_high_shapes) == 1


def scan(key, check, stream):
    core = tuple(from_graph6(key))
    assert len(core) == 8 and {row.bit_count() for row in core} == {2}
    autos = tuple(automorphisms(core))
    support = Supports(core, 6)
    counts = Counter()
    observed = []
    for four in combinations(range(8), 4):
        keep = mask(four)
        if not check and keep != min(mask_image(keep, permutation) for permutation in autos):
            continue
        cap = tuple(2 if keep >> vertex & 1 else 0 for vertex in range(8))
        residue = tuple(2-value for value in cap)
        cache = {size: support.catalog(size, cap) for size in (10, 11, 12)}
        rows = {group: degree_vector(group, 8) for group in set().union(*cache.values())}
        stable = tuple(permutation for permutation in autos if mask_image(keep, permutation) == keep)
        for profile in PROFILES:
            by_row = defaultdict(list)
            for last in cache[profile[2]]:
                by_row[rows[last]].append(last)
            pairs = (combinations_with_replacement(cache[profile[0]], 2) if profile[0] == profile[1]
                     else product(cache[profile[0]], cache[profile[1]]))
            choices = ((first, second, last) for first, second in pairs
                       for last in by_row.get(tuple(cap[vertex]+3-rows[first][vertex]-rows[second][vertex]
                                                     for vertex in range(8)), ())
                       if profile[1] != profile[2] or last >= second)
            for groups in choices:
                if any(sum(rows[group][vertex]-1 for group in groups) != cap[vertex] for vertex in range(8)):
                    continue
                if not admissible(core, groups, residue, 6):
                    continue

                def transported(permutation):
                    return tuple(sorted((image(group, permutation) for group in groups), key=lambda group: (sum(col.bit_count() for col in group), group)))

                if not check:
                    if groups != min(transported(permutation) for permutation in stable):
                        continue
                    row = (key, groups, residue, 6)
                else:
                    canon_keep, canon_groups = min((mask_image(keep, permutation), transported(permutation)) for permutation in autos)
                    canon_residue = tuple(0 if canon_keep >> vertex & 1 else 2 for vertex in range(8))
                    row = (key, canon_groups, canon_residue, 6)
                observed.append(row)
                counts[profile] += 1
    unique = sorted(set(observed))
    assert check or len(observed) == len(unique)
    for row in unique:
        print(json.dumps(row, separators=(',', ':')), file=stream)
    print(key, 'retained local profile hits', dict(counts), 'canonical', len(unique), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('keys', type=Path)
    parser.add_argument('out', type=Path)
    parser.add_argument('--independent', action='store_true')
    args = parser.parse_args()
    start = process_time()
    keys = args.keys.read_text(encoding='ascii').splitlines()
    with args.out.open('x', encoding='ascii') as sink:
        for key in keys:
            scan(key, args.independent, sink)
    print('e8 extreme roster', process_time()-start, 'CPU-s', flush=True)
