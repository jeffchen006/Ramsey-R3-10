#!/usr/bin/env python3
"""Cover (10,10,10,12) with only the three size-ten groups pinned."""

import argparse
from itertools import combinations, combinations_with_replacement
import json
from pathlib import Path

from cubic32 import automorphisms, invert, neighborhoods
from involution_sat import from_graph6
from m11_support import Supports, core_cover, image, triples


def windows(key):
    core = from_graph6(key)
    support = Supports(core, 6)
    autos = tuple(automorphisms(core))
    cap = tuple(4-mask.bit_count() for mask in core)
    old = {tuple(sorted(invert(rows))) for double in combinations(range(8), 2) for rows in neighborhoods(core, double)}
    entries = {10: support.catalog(10, cap)}
    old = {group for group in old if all(left <= right for left, right in zip(support.info(group)[0], cap))}
    assert set(entries[10]) == old
    profile = (10, 10, 10, 12)
    count = 0
    for projection, _, _ in triples(core, support, profile, cap, entries, autos):
        count += 1
        yield key, profile, projection, []
    print(key, 'local', len(old), 'projections', count, flush=True)


def independent_check(key, filename):
    core = from_graph6(key)
    autos = tuple(automorphisms(core))
    cap = tuple(4-mask.bit_count() for mask in core)
    raw = []
    for pair in combinations(range(8), 2):
        if not all(cap[actor] for actor in pair):
            continue
        marks = (1 << pair[0]) | (1 << pair[1])
        raw.extend((tuple(sorted(invert(rows))), marks) for rows in neighborhoods(core, pair))
    raw = sorted(set(raw))
    expected = set()
    for data in combinations_with_replacement(raw, 3):
        groups, marks = zip(*data)
        if any(sum(mark >> actor & 1 for mark in marks) > cap[actor] for actor in range(8)):
            continue
        expected.add(min(tuple(sorted(image(group, perm) for group in groups)) for perm in autos))
    observed = []
    for text in filename.open(encoding='ascii'):
        label, profile, groups, omitted = json.loads(text)
        assert label == key and profile == [10, 10, 10, 12] and not omitted
        observed.append(tuple(map(tuple, groups)))
    assert len(observed) == len(set(observed)) and set(observed) == expected
    print('independent projection cover matches', key, len(expected), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('verify-cores', 'census', 'verify'))
    parser.add_argument('keys', type=Path)
    parser.add_argument('--core', type=int)
    parser.add_argument('--manifest', type=Path)
    args = parser.parse_args()
    keys = args.keys.read_text(encoding='ascii').splitlines()
    if args.mode == 'verify-cores':
        core_cover(keys)
        return
    if args.core is not None:
        keys = keys[args.core:args.core+1]
    assert len(keys) == 1
    if args.mode == 'verify':
        independent_check(keys[0], args.manifest)
    else:
        with args.manifest.open('w', encoding='ascii') as out:
            for entry in windows(keys[0]):
                print(json.dumps(entry, separators=(',', ':')), file=out)


if __name__ == '__main__':
    main()
