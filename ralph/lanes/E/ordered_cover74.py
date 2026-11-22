#!/usr/bin/env python3
"""Bind the mixed cover's exact global projection and lift order."""

import argparse
from collections import Counter
import csv
from hashlib import sha256
from itertools import zip_longest
import json
from pathlib import Path

from bind_shared74 import support_cover
from bind_width74 import binding


def ordered_rows(key, projections):
    for parts, lifts in sorted(projections.items()):
        yield (json.dumps((key, (10, 10, 11, 11), parts, sorted(lifts)),
                          separators=(',', ':')) + '\n').encode('ascii')


def match(actual, expected):
    digest = sha256()
    for index, (found, wanted) in enumerate(zip_longest(actual, expected)):
        if found != wanted:
            raise ValueError(f'ordered cover differs at projection {index}')
        digest.update(wanted)
    return digest.hexdigest()


def verify(cover, key, table):
    first_branches = set()
    projections = support_cover(key, first_branches)
    branch_rows = Counter(parts[0] for parts in projections)
    branch_lifts = Counter()
    for parts, lifts in projections.items():
        branch_lifts[parts[0]] += len(lifts)
    with cover.open('rb') as actual:
        digest = match(actual, ordered_rows(key, projections))
    with table.open(encoding='ascii') as source:
        branches = [(tuple(map(int, row['branch'].split(','))),
                     int(row['projections']), int(row['lifts']))
                    for row in csv.DictReader(source, delimiter='\t')]
    assert branches == [(branch, branch_rows[branch], branch_lifts[branch]) for branch in sorted(first_branches)]
    assert branch_rows.keys() <= first_branches
    print('byte-identical ordered regeneration:', len(projections), 'projections,',
          sum(branch_lifts.values()), 'lifts,', len(branches), 'branches,',
          sum(not rows for _, rows, _ in branches), 'empty; SHA256', digest, flush=True)


def calibrate(folder):
    first = ((0, 2), (3, 4), (5, 6))
    second = ((1, 2), (3, 4), (5, 6))
    projections = {second: {(1, 2)}, first: {(2, 3), (1, 2)}}
    expected = [b'["toy",[10,10,11,11],[[0,2],[3,4],[5,6]],[[1,2],[2,3]]]\n',
                b'["toy",[10,10,11,11],[[1,2],[3,4],[5,6]],[[1,2]]]\n']
    assert match(expected, ordered_rows('toy', projections)) == sha256(b''.join(expected)).hexdigest()
    for mutated in (expected[::-1], expected[:1], [*expected, expected[-1]],
                    [expected[0].replace(b'[[1,2],[2,3]]', b'[[2,3],[1,2]]'), expected[1]]):
        try:
            match(mutated, ordered_rows('toy', projections))
        except ValueError:
            pass
        else:
            raise AssertionError('accepted misordered, missing, or surplus projection/lift')
    core, groups, bounds = (0,), ((1,), (0,), (0,), (0, 0)), (3,)*4
    degrees = (2, 1, 2, 1, 1)
    wide = folder/'positive.8.cnf'
    binding(core, groups, bounds, degrees, wide, folder/'positive.3.cnf')
    try:
        binding(core, groups, bounds, degrees, wide, folder/'negative.3.cnf')
    except AssertionError:
        pass
    else:
        raise AssertionError('accepted narrow belonging to another exact-degree branch')
    print('ordered mutation controls and misbound six-site narrow rejected', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    control = commands.add_parser('calibrate')
    control.add_argument('folder', type=Path)
    bind = commands.add_parser('verify')
    bind.add_argument('cover', type=Path)
    bind.add_argument('key')
    bind.add_argument('branches', type=Path)
    args = parser.parse_args()
    if args.command == 'calibrate':
        calibrate(args.folder)
    else:
        verify(args.cover, args.key, args.branches)
