#!/usr/bin/env python3
"""Reconstruct case sets from the pinned census and certified bound records, not G's summarizer."""

from collections import Counter
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LANE = ROOT / 'ralph/lanes/G'
DEGREES = tuple(range(6, 10))


def read_csv(path):
    with path.open() as stream:
        yield from csv.DictReader(line for line in stream if not line.startswith('#'))


def distribution(row):
    return tuple(int(row[f'n{degree}']) for degree in DEGREES)


def pin(distributions):
    return {tuple(row['n'][2:]): (row['e'], row['t9_U8'])
            for row in distributions if row['e'] < 180 and row['t9_U8'] >= 88}


def apply_bounds(bounds, path, six, seven):
    for line in path.read_text().splitlines():
        record = json.loads(line)
        if record['floor6'] == six and record.get('floor7', 104) == seven:
            key = tuple(record['n'])
            bounds[key] = min(bounds[key], record['threshold'])


def edges_167_with_six(keys, totals):
    return {key for key in keys if key[0] and totals[key] == 167}


def main():
    small = [{'n': [0, 0, 0, 1, 34, 5], 'e': 162, 't9_U8': 88},
             {'n': [0, 0, 1, 0, 23, 16], 'e': 167, 't9_U8': 87},
             {'n': [0, 0, 0, 0, 0, 40], 'e': 180, 't9_U8': 99}]
    assert pin(small) == {(0, 1, 34, 5): (162, 88)}
    assert edges_167_with_six([(1, 0, 23, 16), (0, 0, 26, 14)],
                              {(1, 0, 23, 16): 167, (0, 0, 26, 14): 167}) == {(1, 0, 23, 16)}

    pinned = json.loads((ROOT / 'lean/data/cases_pin1/degseq_gr_mtf.json').read_text())['survivors']
    original = pin(pinned)
    totals = {key: value[0] for key, value in original.items()}
    before = {key: value[1] for key, value in original.items()}
    assert len(pinned) == 545 and len(original) == 524
    assert all(sum(key) == 40 and sum(count * degree for count, degree in zip(key, DEGREES)) == 2 * total
               for key, total in totals.items())
    assert [row['n'] for row in pinned if row['e'] == 180] == [[0, 0, 0, 0, 0, 40]]

    round1 = list(read_csv(LANE / 't9_round1.csv'))
    assert len(round1) == 524
    assert {distribution(row): (int(row['e']), int(row['baseline_t9_U8'])) for row in round1} == original
    bounds = {distribution(row): int(row['certified_t9_upper']) for row in round1}
    assert all(bounds[key] <= before[key] for key in before)
    apply_bounds(bounds, LANE / 'root_floor_certs.jsonl', 119, 104)
    active = {key for key in bounds if bounds[key] >= 88 and not (key[0] and totals[key] == 166)}
    assert len(active) == 454 and sum(bounds[key] == 88 for key in active) == 20

    old_167 = edges_167_with_six(original, totals)
    fresh_167 = edges_167_with_six(active, totals)
    assert len(old_167) == 56 and len(fresh_167) == 55
    declared = list(read_csv(LANE / 'root_certs/closed167.csv'))
    assert len(declared) == 55 and {distribution(row) for row in declared} == fresh_167
    assert all(int(row['e']) == 167 and int(row['farkas_rhs']) == -int(row['n6']) < 0
               and int(row['t9_upper_floor119']) == bounds[distribution(row)] for row in declared)
    assert sum(bounds[key] == 88 for key in fresh_167) == 3
    print('524 pinned near-regular -> 454 before round 3. 56 degree-six e167 cuts; 55 new; 3 overlap U88.')
    print('Old e167 cut:', sorted(old_167 - fresh_167))

    first_cut = {key: 'root6_at_167' for key in fresh_167}
    live = active - fresh_167
    current = bounds.copy()
    apply_bounds(current, LANE / 'root_floor120_certs.jsonl', 120, 104)
    assert all(current[key] >= 88 for key in live)
    for level, suffix in [(105, ''), (106, '_106'), (107, '_107')]:
        apply_bounds(current, LANE / f'root_floor7{suffix}_certs.jsonl', 120, level)
        closed = {key for key in live if current[key] <= 87}
        for key in closed:
            first_cut[key] = f'root7_floor{level}'
        live -= closed
    counts = Counter(first_cut.values())
    assert [counts[f'root7_floor{level}'] for level in (105, 106, 107)] == [8, 6, 9]
    assert len(live) == 376 and sum(current[key] == 88 for key in live) == 13

    final = list(read_csv(LANE / 'round3_cases.csv'))
    assert len(final) == 454 and {distribution(row) for row in final} == active
    assert all(int(row['t9_before']) == bounds[distribution(row)] and
               row['round3_cut'] == first_cut.get(distribution(row), '') for row in final)
    assert {distribution(row) for row in final if not row['round3_cut'] and int(row['t9_after']) == 88} == {
        key for key in live if current[key] == 88}
    print('Degree-seven increments: 8/6/9. Open: 376 near-regular + R; 13 conditional U88.')
    next_floor = {key for key in live if key[0] and totals[key] == 168}
    assert len(next_floor) == 47
    print('47 presently open e168 rows would fall if the degree-six floor rises to 121.')


if __name__ == '__main__':
    main()
