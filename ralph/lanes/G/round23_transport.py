"""Versioned replacement for the direction-sensitive h6 replay entry point."""

import csv
import json
import sys
from collections import Counter
from itertools import product
from pathlib import Path

from round22_control import ROOT, flatten, tiny_positive, tiny_strict, mutations, unflatten


def action(label, left, right, swap):
    board = unflatten(label, 5)
    output = [[0] * 5 for _ in range(5)]
    for row, col in product(range(5), repeat=2):
        first, second = left[row], right[col]
        if swap:
            first, second = second, first
        output[first][second] = board[row][col]
    return flatten(output)


def transporter(row):
    left, right = (tuple(map(int, row[key])) for key in ('left_perm', 'right_perm'))
    swap = bool(int(row['swap']))
    return left, right, swap


def inverse(left, right, swap):
    lhs, rhs = (tuple(perm.index(index) for index in range(5)) for perm in (left, right))
    return (rhs, lhs, swap) if swap else (lhs, rhs, swap)


def holes(raw, left, right, swap):
    mapped = tuple(tuple(sorted(sum(1 << perm[index] for index in range(5) if mask >> index & 1)
                                for mask in shore)) for shore, perm in zip(raw, (left, right)))
    return mapped[::-1] if swap else mapped


def compare_inventory(path):
    ref = ROOT / 'scratch/A/r22'
    version = json.loads((ROOT / 'scratch/A/r23/transport.v1.json').read_text())
    assert version['schema'] == 'h6.label-to-representative.v1'
    local = {flatten(board['grid']): board for board in json.loads(path.read_text())}
    counted, seen, reversed_failures = Counter(), set(), 0
    for row in csv.DictReader((ROOT / version['source']).open(), delimiter='\t'):
        label, rep = row['label'], row['representative']
        args = transporter(row)
        assert label not in seen and action(label, *args) == rep
        assert action(rep, *inverse(*args)) == label
        reversed_failures += action(rep, *args) != label
        counted[rep] += 1
        seen.add(label)
    assert reversed_failures == version['reversed_action_failures']
    masses = {key: board['orbit_size'] for key, board in local.items()}
    assert counted == masses == {row['board']: int(row['labelled']) for row in
                                csv.DictReader((ref / 'h6.boards.tsv').open(), delimiter='\t')}
    known = {(key, *left, *right) for key, board in local.items() for left, right in board['keys']}
    external = {(row['board'], *(int(row[key]) for key in ('left_hole_0', 'left_hole_1',
                                                            'right_hole_0', 'right_hole_1')))
                for row in csv.DictReader((ref / 'h6.holes.tsv').open(), delimiter='\t')}
    assert known == external
    for row in version['rejection_cases']:
        args = transporter(row)
        assert action(row['label'], *args) == row['representative']
        assert action(row['representative'], *args) == row['wrongly_forward_from_rep'] != row['label']
        truth = tuple(map(tuple, row['representative_holes']))
        assert holes(row['raw_holes'], *args) == truth
        assert holes(truth, *inverse(*args)) == tuple(map(tuple, row['raw_holes']))
    assert (len(local), len(seen), len(known)) == (version['representatives'], version['raw_labels'], version['hole_keys'])
    print('forward/inverse board transport, board masses, keys, wrong-direction rejections:',
          len(local), len(seen), len(known), reversed_failures)


if __name__ == '__main__':
    compare_inventory(Path(sys.argv[1]))
    if '--small' in sys.argv[2:]:
        tiny_strict()
        tiny_positive()
        mutations()
