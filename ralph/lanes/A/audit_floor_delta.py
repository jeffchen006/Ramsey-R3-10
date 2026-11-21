#!/usr/bin/env python3
"""Rebuild the degree-floor ledger from the pinned case list and witness keys."""

from collections import Counter
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LANE_G = ROOT / 'ralph/lanes/G'
PINNED = ROOT / 'lean/data/cases_pin1/degseq_gr_mtf.json'
KEYS = ('n6', 'n7', 'n8', 'n9')
STAGES = ((120, 104, 'root_floor120_certs.jsonl', 36),
          (120, 105, 'root_floor7_certs.jsonl', 40),
          (120, 106, 'root_floor7_106_certs.jsonl', 48),
          (120, 107, 'root_floor7_107_certs.jsonl', 45))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rows(path):
    return [json.loads(row) for row in path.read_text().splitlines()]


def edge_count(key):
    require(len(key) == 4 and sum(key) == 40 and min(key) >= 0, f'invalid distribution {key}')
    twice = sum(degree * count for degree, count in enumerate(key, 6))
    require(twice % 2 == 0, f'odd degree sum {key}')
    return twice // 2


def stages_from_witnesses(name, before, floor6, floor7, count):
    records = rows(LANE_G / name)
    require(len(records) == count, f'{name}: unexpected witness count')
    bounds = {}
    for record in records:
        key = tuple(record['n'])
        threshold = record['threshold']
        require(key in before and record['e'] == edge_count(key)
                and before[key] > threshold >= 87 and record['floor6'] == floor6
                and record.get('floor7', 104) == floor7
                and ((floor7 == 104 and key[0] > 0) or (floor7 > 104 and key[1] > 0)),
                f'{name}: misbound witness {key}')
        bounds[key] = min(threshold, bounds.get(key, 99))
    return bounds


def read_csv(name):
    with (LANE_G / name).open() as stream:
        return list(csv.DictReader(line for line in stream if not line.startswith('#')))


def main():
    records = json.loads(PINNED.read_text())['survivors']
    before = {}
    for record in records:
        require(record['n'][:2] == [0, 0], 'non-MTF baseline row')
        key = tuple(record['n'][2:])
        require(edge_count(key) == record['e'] and key not in before, 'invalid pinned row')
        before[key] = record['t9_U8']
    require(len(before) == 545 and before.pop((0, 0, 0, 40)) == 99, 'Case R/baseline mismatch')
    near_regular = {key: bound for key, bound in before.items() if bound >= 88}
    require(len(near_regular) == 524, 'pinned near-regular count mismatch')

    old_bounds = dict(near_regular)
    source_by_key = {key: 'pinned' for key in old_bounds}
    for record in rows(LANE_G / 't9_round1_certs.jsonl'):
        require(record['n'][:2] == [0, 0], 'non-MTF round-1 witness')
        key = tuple(record['n'][2:])
        threshold = record['threshold']
        require(key in old_bounds and old_bounds[key] > threshold >= 87 and edge_count(key) == record['e'],
                f'round-1 witness key mismatch {key}')
        old_bounds[key] = threshold
        source_by_key[key] = record['family']
    baseline_csv = read_csv('t9_round1.csv')
    require(len(baseline_csv) == len(near_regular), 'round-1 CSV count mismatch')
    for record in baseline_csv:
        key = tuple(int(record[field]) for field in KEYS)
        check = (int(record['baseline_t9_U8']), int(record['certified_t9_upper']), record['evidence'])
        require(check == (near_regular[key], old_bounds[key], source_by_key[key])
                and int(record['e']) == edge_count(key), f'round-1 CSV row mismatch {key}')
    require(len({tuple(record[field] for field in KEYS) for record in baseline_csv}) == len(near_regular),
            'duplicate round-1 CSV rows')

    floor119 = stages_from_witnesses('root_floor_certs.jsonl', old_bounds, 119, 104, 63)
    updated = {key: min(value, floor119.get(key, 99)) for key, value in old_bounds.items()}
    baseline = {key: value for key, value in updated.items()
                if value >= 88 and not (key[0] and edge_count(key) <= 166)}
    require(len(baseline) == 454 and Counter(baseline.values())[88] == 20, 'floor-119 baseline mismatch')

    final = dict(baseline)
    closed = {}
    for key in baseline:
        if edge_count(key) == 167 and key[0]:
            closed[key] = 'root6_at_167'
    expected_closed167 = {(key, -key[0], baseline[key]) for key in closed}
    input_closed167 = read_csv('root_certs/closed167.csv')
    supplied = {(tuple(int(row[field]) for field in KEYS), int(row['farkas_rhs']),
                 int(row['t9_upper_floor119'])) for row in input_closed167 if row['e'] == '167'}
    require(supplied == expected_closed167 and len(supplied) == len(input_closed167) == 55,
            'e167 closure identity mismatch')
    require(sum(key[0] > 0 and edge_count(key) == 167 for key in near_regular) == 56,
            'global e167 closure count mismatch')

    for floor6, floor7, name, count in STAGES:
        active = {key: value for key, value in final.items() if key not in closed}
        bounds = stages_from_witnesses(name, active, floor6, floor7, count)
        for key, threshold in bounds.items():
            final[key] = threshold
            if threshold == 87:
                closed[key] = f'root7_floor{floor7}'

    columns = ('e', *KEYS, 't9_before', 't9_after', 'round3_cut')
    print(*columns, sep=',')
    counts = Counter()
    for key in sorted(baseline, key=lambda key: (edge_count(key), key)):
        cut = closed.get(key, '')
        print(edge_count(key), *key, baseline[key], final[key], cut, sep=',')
        counts[cut or 'open'] += 1
        counts['further_U88'] += int(not cut and final[key] == 88)
    targets = {'root6_at_167': 55, 'root7_floor105': 8, 'root7_floor106': 6,
               'root7_floor107': 9, 'open': 376, 'further_U88': 13}
    require(counts == targets, f'unexpected exact delta {counts}')
    print('# ' + ', '.join(f'{key}={value}' for key, value in sorted(counts.items())))


if __name__ == '__main__':
    main()
