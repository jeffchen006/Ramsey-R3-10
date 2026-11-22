#!/usr/bin/env python3
"""Bind round-13 G keys and replay integer-scaled Farkas contradictions.

This trusts the previously audited row generator, not G's case selector,
scanner, or rational verifier. It does not certify feasibility or optimality.
"""

from collections import Counter, defaultdict
import csv
from fractions import Fraction
from hashlib import sha256
import json
from math import lcm
from pathlib import Path
import sys

from check_round6_scope import FIELDS, csv_keys


ROOT = Path(__file__).resolve().parents[3]
G = ROOT / 'ralph/lanes/G'
CRITIC = ROOT / 'scratch/critic/r12'
SCOUT = ROOT / 'scratch/ideas/r012_N'
TARGET = ROOT / 'scratch/G/round13'
PARITY_KEY = (170, 2, 7, 0, 31)


def key(row):
    result = tuple(int(row[field]) for field in FIELDS)
    edges, *counts = result
    assert min(counts) >= 0 and sum(counts) == 40
    assert sum(degree * count for degree, count in enumerate(counts, 6)) == 2 * edges
    return result


def keyed_table(path, delimiter=','):
    with path.open() as stream:
        rows = list(csv.DictReader(stream, delimiter=delimiter))
    table = {key(row): row for row in rows}
    assert len(table) == len(rows)
    return table


def margin(rows, bounds, weights):
    if not weights or any(weight <= 0 or not 0 <= index < len(rows)
                          for index, weight in weights.items()):
        raise ValueError('invalid multiplier index or sign')
    scale = lcm(*(weight.denominator for weight in weights.values()))
    rhs = 0
    lhs = defaultdict(int)
    for index, weight in weights.items():
        coefficients, bound, _ = rows[index]
        multiplier = weight.numerator * (scale // weight.denominator)
        rhs += multiplier * bound
        for column, coefficient in coefficients.items():
            lhs[column] += multiplier * coefficient
    extremizer = {column: bounds[column] if value < 0 else 0 for column, value in lhs.items()}
    return Fraction(sum(lhs[column] * value for column, value in extremizer.items()) - rhs, scale)


def controls():
    rows = [({'edges': -1}, -1, 'lower'), ({'edges': 1}, 1, 'upper')]
    weights = {0: Fraction(1, 3), 1: Fraction(1, 3)}
    assert margin(rows, {'edges': 13}, weights) == 0
    rows[1] = ({'edges': 1}, 0, 'upper')
    assert margin(rows, {'edges': 13}, weights) == Fraction(1, 3)
    assert margin(rows, {'edges': 13}, {0: Fraction(1)}) < 0
    assert margin(rows, {'edges': 0}, {0: Fraction(1)}) > 0
    try:
        margin(rows, {'edges': 13}, {0: Fraction(-1)})
    except ValueError:
        pass
    else:
        raise AssertionError('negative weight accepted')


def main():
    controls()
    baseline = {case: int(row['t9']) for case, row in csv_keys('round6_baseline.csv').items()
                if not row['cut']}
    assert len(baseline) == 278
    lower = {case for case in baseline if case[0] < 170 and case[1]}
    zero_eight = {case for case in baseline if case[0] == 170 and case[1] == 2 and case[3] == 0}
    assert zero_eight == {PARITY_KEY}
    closed = lower | zero_eight
    assert Counter(case[0] for case in closed) == {168: 20, 169: 19, 170: 1}
    assert Counter(case[1] for case in closed if case[0] == 168) == {1: 11, 2: 9}
    surviving = baseline.keys() - closed
    assert Counter(case[1] for case in surviving if case[0] == 170 and case[1]) == {1: 9, 2: 7}
    assert closed == keyed_table(CRITIC / 'closed40.tsv', '\t').keys()
    assert surviving == keyed_table(CRITIC / 'surviving238.tsv', '\t').keys()
    impact = [json.loads(line) for line in (SCOUT / 'impact.jsonl').read_text().splitlines()]
    assert len(impact) == len(closed) and {(item['edges'], *item['counts']) for item in impact} == closed
    assert len(surviving) == 238
    assert sha256((CRITIC / 'closed40.tsv').read_bytes()).hexdigest() == (
        'e875e49967a356def3d29cc6333c5d774fd88997f56cd2e09d842344d67ff1c6')
    print('closed: 20+19+1, disjoint from surviving 238; C40 and N manifest exact')

    table = keyed_table(TARGET / 'thresholds.csv')
    assert table.keys() == surviving
    u88 = {case for case in baseline if baseline[case] == 88}
    assert len(u88) == 10 and all(case[1] == 0 for case in u88)
    assert u88 == {case for case, row in table.items() if int(row['t9']) == 88}
    improved = {}
    for case, row in table.items():
        old, new = int(row['inherited_t9']), int(row['t9'])
        assert old == baseline[case] and 88 <= new <= old
        assert row['status'] == ('improved' if new < old else 'old-U88' if old == 88 else 'unchanged')
        if old != new:
            assert old == new + 1 and case[1] > 0
            improved[case] = new
    assert Counter(row['status'] for row in table.values()) == {'old-U88': 10, 'unchanged': 216, 'improved': 12}
    print('t9 roster: 10 unchanged U88; 216 other unchanged; 12 improved by one')

    sys.path.insert(0, str(G))
    from scan_d5_cuts import consequences
    from typed_lp import PRESENT, build

    seen = set()
    row_families = Counter()
    for line in (TARGET / 'multipliers.jsonl').read_text().splitlines():
        item = json.loads(line)
        case = tuple(item['key'])
        assert case not in seen
        seen.add(case)
        edges, *counts = case
        if case in lower:
            assert item['kind'] == 'low-edge' and 'floor9' not in item
            rows = [({'Z': -1}, -48, 'private'), ({'Z': 1}, edges - 122, 'residue')]
            bounds = {'Z': 54}
        else:
            floor9 = 88 if case in zero_eight else improved[case] + 1
            assert (item['kind'], item.get('floor9')) == (
                ('parity', None) if case in zero_eight else ('threshold', floor9))
            model = build(dict(zip(range(6, 10), counts)), dict(zip(range(6, 10), (122, 108, 97, floor9))),
                          40, 9, True, PRESENT['combined'])
            consequences(model, counts, edges, 132)
            rows, bounds = model.rows, model.bounds
        weights = {int(index): Fraction(weight) for index, weight in item['y'].items()}
        assert len(weights) == len(item['y'])
        gap = margin(rows, bounds, weights)
        assert gap > 0, (case, gap)
        if case not in lower:
            row_families.update(rows[index][2].split('_(')[0].rstrip('+-') for index in weights)
            print(f'{case}: {item["kind"]}; gap={gap}; support={len(weights)}')
    assert seen == closed | improved.keys()
    print('PASS: 39 direct, 1 parity, 12 tightened threshold certificates; arithmetic only')
    print('Selected row families', *sorted(row_families.items()), sep='\n')


if __name__ == '__main__':
    main()
