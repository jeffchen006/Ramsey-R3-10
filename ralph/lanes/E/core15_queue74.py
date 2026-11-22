#!/usr/bin/env python3
"""Audit core 15's frozen queue, branch identities and checked routes."""

import argparse
from bisect import bisect_right
from collections import Counter
import csv
from hashlib import sha256
from itertools import accumulate
import json
from pathlib import Path

from audit_routes74 import REBIND, recheck
from replay_shared74 import read


def partition(queue, sample):
    assert len(sample) > 1 and len(queue) >= len(sample)
    assert queue == sorted(set(queue))
    assert sample == [queue[pos * (len(queue) - 1) // (len(sample) - 1)] for pos in range(len(sample))]
    remaining = sorted(set(queue) - set(sample))
    assert len(set(sample) | set(remaining)) == len(queue)
    return remaining


def branch_at(index, first_group, branches, stops):
    number = bisect_right(stops, index)
    assert 0 <= index < stops[-1] and tuple(first_group) == branches[number]
    return number


def branch_rows(original, queue):
    with (original/'pilot.15.branches.tsv').open(encoding='ascii') as source:
        branches = [(tuple(map(int, row['branch'].split(','))), int(row['projections']), int(row['lifts']))
                    for row in csv.DictReader(source, delimiter='\t')]
    assert len(branches) == 34 and all(rows and lifts for _, rows, lifts in branches)
    assert sum(lifts for _, _, lifts in branches) == 716045
    stops = list(accumulate(rows for _, rows, _ in branches))
    assert stops[-1] == 94738
    keys = [group for group, _, _ in branches]
    by_index = {}
    for index, lift in queue:
        by_index.setdefault(index, []).append(lift)
    answer = {}
    with (original/'cover.15.jsonl').open('rb') as cover:
        for index, row in enumerate(cover):
            if index not in by_index:
                continue
            key, profile, parts, omitted = json.loads(row)
            assert key == 'GCQf?{' and profile == [10, 10, 11, 11]
            branch = branch_at(index, parts[0], keys, stops)
            for lift in by_index[index]:
                assert 0 <= lift < len(omitted)
                groups = (*parts, omitted[lift])
                assert [sum(mask.bit_count() for mask in group) for group in groups] == profile
                answer[index, lift] = (branch, ','.join(map(str, keys[branch])), sha256(row).hexdigest(),
                                       ','.join(map(str, omitted[lift])))
    assert list(answer) == queue
    assert len(by_index) == 110 and len({info[0] for info in answer.values()}) == 12
    return answer


def ids(path):
    answer = []
    for index, lift, marker in read(path):
        assert marker == 'open' and type(index) is type(lift) is int and index >= 0 and lift >= 0
        answer.append((index, lift))
    return answer


def frozen_inputs(original):
    queue = ids(original/'queue.15.jsonl')
    sample = ids(original/'spaced.15.jsonl')
    assert (len(queue), len(sample)) == (142, 16)
    assert queue[0] == (22646, 18) and queue[-1] == (93731, 12)
    return queue, sample, partition(queue, sample)


def prepare(original):
    queue, _, remaining = frozen_inputs(original)
    receipts = Counter()
    found = []
    for index, lift, kind, *_ in read(original/'receipt.15.jsonl'):
        receipts[kind] += 1
        if kind == 'open':
            found.append((index, lift))
    assert found == queue
    branch_rows(original, queue)
    with Path('remaining.15.jsonl').open('x', encoding='ascii') as output:
        for index, lift in remaining:
            print(json.dumps((index, lift, 'open'), separators=(',', ':')), file=output)
    print('frozen merged receipt exact equality:', len(queue), 'IDs;', len(remaining), 'not in sample;', dict(receipts))


def route_audit(folder, items):
    labels = [f'{index}_{lift}' for index, lift in items]
    fresh = Path(f'{folder}.rebind.log')
    stats = recheck(Path(f'{folder}.log'), fresh, Path(folder), labels)
    print(folder, len(items), dict(stats), flush=True)
    checked = [match[2] for line in fresh.read_text(encoding='ascii').splitlines()
               if (match := REBIND.fullmatch(line))]
    return {key: (folder, route) for key, route in zip(items, checked, strict=True)}


def final_audit(original, mode):
    queue, sample, remaining = frozen_inputs(original)
    assert ids(Path('remaining.15.jsonl')) == remaining
    if mode == 'compare':
        for route in ('narrow', 'wide'):
            assert sorted(route_audit(f'compare.{route}', sample)) == sample
        return
    covered = route_audit(f'compare.{mode}', sample)
    for shard in range(4):
        fresh = route_audit(f'proof.{shard}', remaining[shard::4])
        assert not covered.keys() & fresh.keys()
        covered.update(fresh)
    assert sorted(covered) == queue
    branches = branch_rows(original, queue)
    print('complete exact checked union:', len(covered), dict(Counter(choice for _, choice in covered.values())))
    with Path('checked.15.tsv').open('x', encoding='ascii') as output:
        print('projection', 'lift', 'first_branch', 'first_group', 'row_sha256', 'omitted_group',
              'folder', 'route', sep='\t', file=output)
        for item in queue:
            print(*item, *branches[item], *covered[item], sep='\t', file=output)


def calibrate():
    queue = [(0, 0), (0, 1), (1, 0), (2, 0), (3, 4), (5, 0)]
    assert partition(queue, [(0, 0), (1, 0), (5, 0)]) == [(0, 1), (2, 0), (3, 4)]
    assert branch_at(1, [4, 5], [(4, 5), (6, 7)], [2, 6]) == 0
    assert branch_at(2, [6, 7], [(4, 5), (6, 7)], [2, 6]) == 1
    for control in (lambda: partition(queue, [(0, 0), (2, 0), (5, 0)]),
                    lambda: partition(queue + [queue[-1]], [queue[0], queue[-1]]),
                    lambda: branch_at(2, [4, 5], [(4, 5), (6, 7)], [2, 6])):
        try:
            control()
        except AssertionError:
            continue
        raise AssertionError('invalid spacing, duplicate ID, or wrong first branch accepted')
    print('small queue/branch controls: good partition/branch boundaries; bad spacing, duplicate and wrong branch rejected')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'compare', 'wide', 'narrow', 'calibrate'))
    parser.add_argument('--original', type=Path, default=Path('../r16_shared'))
    args = parser.parse_args()
    if args.mode == 'calibrate':
        calibrate()
    elif args.mode == 'prepare':
        prepare(args.original)
    else:
        final_audit(args.original, args.mode)
