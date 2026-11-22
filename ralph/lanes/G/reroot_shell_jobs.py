#!/usr/bin/env python3
"""Exact shell-signature schedules for the mixed equality reroots."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations, product
from pathlib import Path

from pinned_anchor_window import roles, unpack

EDGE_FLOOR = {24: 56, 25: 65, 26: 73, 27: 85}


def unpaired_floor(key_type):
    return 108 if key_type.startswith('B.') else 99 if key_type.startswith('A8') else 90


def mask(labels):
    return sum(1 << label for label in labels)


def slots(adj, side, exterior, holes):
    wanted = Counter({1 << anchor: 4 for anchor in side})
    wanted.update(mask(pair) for pair in combinations(side, 2) if tuple(pair) not in holes)
    seen = Counter(adj[vertex] & mask(side) for vertex in exterior)
    assert not (seen - wanted)
    return sorted((wanted - seen).elements())


def assigned_roles(row):
    row_id, adj, small, large = unpack(row)
    origin = '_'.join((row_id, *row.split()[1:3]))
    outside = tuple(vertex for vertex in range(21) if vertex not in (*small, *large))
    star, = (anchor for anchor in small if adj[anchor] & mask(large))
    for degree in (8, 9):
        for role in roles(adj, small, large, degree):
            orientation, _, _, _, _, shape, hole, peer_hole = role
            if orientation:
                continue
            key = '_'.join(map(str, (origin, degree, orientation, shape, *hole, *peer_hole)))
            missing = slots(adj, large, outside, (hole, peer_hole))
            assert len(missing) == 15 - degree
            nons = tuple(anchor for anchor in small if anchor != star)
            variants = [('leaf', 0, mask(nons))]
            for tau, leaf in product((0, 1), nons):
                variants.append((f'full{tau}-{leaf}', 1 - tau, mask(anchor for anchor in nons if anchor != leaf)))
            for kind, common, old_doubles in variants:
                gained = len(missing) - 2 - common
                yield (f'A{degree}.{gained + 22}.{kind.split("-")[0]}', key, kind, 2, gained, common,
                       mask(small), old_doubles, missing)
    for endpoint_s, endpoint_b in product(small, repeat=2):
        if endpoint_s != endpoint_b and star in (endpoint_s, endpoint_b):
            shape = 'matching'
        elif endpoint_s == endpoint_b == star:
            shape = 'middle'
        else:
            continue
        missing = slots(adj, large, outside, ())
        assert len(missing) == 8
        for tau in (0, 1):
            if tau and endpoint_s > endpoint_b:
                continue
            key = f'{origin}_{shape}_{endpoint_s}_{endpoint_b}_{tau}'
            yield (f'B.{25 + tau}.{shape}', key, str(tau), 4, 3 + tau, 1 - tau,
                   mask(small) ^ (1 << endpoint_s), mask(small) ^ (1 << endpoint_b), missing)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--sample', type=int)
    args = parser.parse_args()
    rows = args.source.read_text().splitlines()
    if args.sample:
        rows = [rows[idx * len(rows) // args.sample] for idx in range(args.sample)]
    counts = Counter()
    for row in rows:
        jobs = list(assigned_roles(row))
        if not jobs:
            continue
        print(6, *row.split())
        print(len(jobs))
        for key_type, key, variant, keep, gained, common, first, second, missing in jobs:
            counts[key_type] += 1
            orders = (22 + keep, 22 + gained)
            floors = tuple(max(2, order - 23) for order in orders)
            if key_type.startswith('B.'):
                floors = 4, (4 if gained == 4 else (3 if 'middle' in key_type else 2))
            print(key_type, key, variant, keep, gained, common, first, second, len(missing),
                  *floors, *(EDGE_FLOOR[order] for order in orders), unpaired_floor(key_type), 1, *missing)
    import sys
    print(dict(sorted(counts.items())), file=sys.stderr)


if __name__ == '__main__':
    main()
