#!/usr/bin/env python3
"""Reconstruct the floor-122 ledger and certify new t9 bounds, if any."""

import argparse
from collections import Counter
import csv
from fractions import Fraction
import json
from pathlib import Path

from freeze_round6 import ledger
from scan import solve, verify
from scan_d5_cuts import consequences
from typed_lp import Model, PRESENT, build


FIELDS = ('e', 'n6', 'n7', 'n8', 'n9')


def profile(key, floor9):
    edges, *counts = key
    target = build(dict(zip(range(6, 10), counts)), {6: 122, 7: 108, 8: 97, 9: floor9},
                   40, 9, True, PRESENT['combined'])
    if counts[0]:
        consequences(target, counts, edges, 132)
    return target


def live_cases(baseline):
    closed = {}
    for key in baseline:
        edges, n6, n7, n8, n9 = key
        if n6 and edges < 170:
            closed[key] = '122+48'
        elif (edges, n6, n8) == (170, 2, 0):
            closed[key] = 'adjacent-d6-parity'
    cases = {key: value for key, value in baseline.items() if key not in closed}
    assert Counter(key[0] for key in closed) == {168: 20, 169: 19, 170: 1}
    assert len(cases) == 238
    return cases, closed


def direct_certificate(key):
    edges = key[0]
    target = Model()
    col = target.col(('Z',), 54)
    target.le({col: -1}, -48, 'private_cell_floor')
    target.le({col: 1}, edges - 122, 'residue_floor')
    return target, {0: Fraction(1), 1: Fraction(1)}


def replay(path, baseline, cases):
    kinds = Counter()
    seen = set()
    for line in path.read_text().splitlines():
        record = json.loads(line)
        key = tuple(record['key'])
        kind = record['kind']
        assert (kind, key) not in seen and key in baseline
        seen.add((kind, key))
        weights = {int(index): Fraction(value) for index, value in record['y'].items()}
        if kind == 'low-edge':
            assert key not in cases and key[0] < 170 and key[1] > 0
            target, _ = direct_certificate(key)
        elif kind == 'parity':
            assert key not in cases and key == (170, 2, 7, 0, 31)
            target = profile(key, 88)
        else:
            assert key in cases
            assert kind in {'floor88', 'threshold'}
            assert (record['floor9'] == 88 if kind == 'floor88'
                    else 89 <= record['floor9'] <= baseline[key])
            target = profile(key, record['floor9'])
        assert verify(target, weights), key
        kinds[kind] += 1
    assert (kinds['low-edge'], kinds['parity']) == (39, 1)
    print('exact rational replay:', dict(kinds))


def scan_all(directory, baseline, cases, closed):
    tally = Counter()
    with (directory / 'thresholds.csv').open('w') as output, \
         (directory / 'multipliers.jsonl').open('w') as certfile:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow((*FIELDS, 'inherited_t9', 't9', 'status'))

        def record(key, kind, weights, **extra):
            print(json.dumps({'key': key, 'kind': kind, 'y': weights, **extra}, sort_keys=True),
                  file=certfile, flush=True)

        for key in sorted(closed):
            if key[0] < 170:
                target, weights = direct_certificate(key)
                assert verify(target, weights)
                record(key, 'low-edge', {index: str(value) for index, value in weights.items()})
            else:
                status, weights = solve(profile(key, 88))
                assert status == 'cert', key
                record(key, 'parity', weights)

        for key, previous in sorted(cases.items()):
            status, weights = solve(profile(key, 88))
            if status == 'cert':
                record(key, 'floor88', weights, floor9=88)
                writer.writerow((*key, previous, '', 'floor88'))
                tally['floor88'] += 1
                continue
            assert status == 'feasible', (key, 88, status)
            threshold = previous
            best_weights = None
            for floor9 in range(previous, 88, -1):
                status, weights = solve(profile(key, floor9))
                if status == 'feasible':
                    break
                assert status == 'cert', (key, floor9, status)
                threshold, best_weights = floor9 - 1, weights
            if best_weights:
                record(key, 'threshold', best_weights, floor9=threshold + 1)
            outcome = ('old-U88' if previous == 88 else
                       'new-U88' if threshold == 88 else
                       'improved' if threshold < previous else 'unchanged')
            writer.writerow((*key, previous, threshold, outcome))
            tally[outcome] += 1
        print('threshold outcomes:', dict(tally))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    baseline, _ = ledger()
    cases, closed = live_cases(baseline)
    if not args.verify:
        scan_all(args.directory, baseline, cases, closed)
    replay(args.directory / 'multipliers.jsonl', baseline, cases)


if __name__ == '__main__':
    main()
