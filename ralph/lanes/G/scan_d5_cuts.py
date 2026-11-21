#!/usr/bin/env python3
"""Exact LP consequences of the order-33 degree-five exclusion."""

import argparse
from collections import Counter
import csv
from fractions import Fraction
import json
from math import comb
from pathlib import Path

from scan import solve, verify
from scan_private_equality import signatures
from typed_lp import Model, PRESENT, build


HERE = Path(__file__).resolve().parent


def consequences(model, counts, edges, cap, equality=True):
    number = counts[0]
    roots = [key for key in model.bounds if key[:2] == ('x', 6)]
    low_residue = [key for key in roots if edges - sum(key[2]) <= cap]
    high_residue = [key for key in roots if edges - sum(key[2]) > cap]
    model.le({key: 1 for key in low_residue if key[2].count(6) != number - 1}, 0,
             'no_d6_exterior_for_low_residue')
    if number >= 3:
        model.le({key: 1 for key in low_residue}, 1, 'at_most_one_universal_d6')
        model.le({('m', 6, 6): 1, **{key: comb(number - 1, 2) for key in low_residue}},
                 comb(number, 2), 'universal_induces_d6_star')
    if edges <= cap + 48 or cap == 132:
        model.le({key: 1 for key in model.bounds if key[:2] == ('p', 6) and key[3] > key[2] - 6},
                 0, 'degree_at_least_6_in_all_residues')
    elif number:
        for degree in range(7, 10):
            model.le({**{key: 1 for key in model.bounds
                         if key[:3] == ('p', 6, degree) and key[3] > degree - 6},
                      **{key: key[2].count(degree) - counts[degree - 6] for key in high_residue}},
                     0, f'higher_codegree_only_at_high_residue_{degree}')
    if equality:
        allowed, _ = signatures()
        model.le({key: 1 for key in roots if sum(key[2]) == 48 and key[2] not in allowed}, 0,
                 'degree6_equality_profile')


def model(counts, edges, floor8, floor9, cap, floor7=107):
    assert len(counts) == 4 and sum(counts) == 40
    assert sum(degree * count for degree, count in enumerate(counts, 6)) == 2 * edges
    assert edges >= 162 and (not counts[0] or edges >= 168)
    assert floor7 in (107, 108) and floor8 in (95, 97) and floor9 >= 86
    result = build(dict(zip(range(6, 10), counts)), {6: 120, 7: floor7, 8: floor8, 9: floor9},
                   40, 9, True, PRESENT['combined'])
    assert cap in (121, 122, 123, 132)
    if counts[0]:
        consequences(result, counts, edges, cap)
    return result


def direct_model(counts):
    result = Model()
    index = result.col(('n6',), 40)
    result.le({index: 1}, 2, 'degree_six_vertices_form_clique')
    result.le({index: -1}, -counts[0], 'pinned_distribution')
    return result


def cases():
    with (HERE / 'round4_cases.csv').open() as stream:
        for row in csv.DictReader(line for line in stream if not line.startswith('#')):
            key = tuple(int(row[f'n{degree}']) for degree in range(6, 10))
            if not row['round4_cut'] and key[0]:
                yield int(row['e']), key, int(row['t9_new'])


def cases_for_floor108():
    with (HERE / 'round5_cases.csv').open() as stream:
        for row in csv.DictReader(line for line in stream if not line.startswith('#')):
            key = tuple(int(row[f'n{degree}']) for degree in range(6, 10))
            if not row['round5_cut'] and key[1]:
                yield int(row['e']), key, int(row['t9_after'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('records', type=Path)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--cap', type=int, default=132, choices=(121, 122, 123, 132))
    parser.add_argument('--floor7-108', action='store_true')
    args = parser.parse_args()
    tally = Counter()
    if args.verify:
        seen = set()
        for line in args.records.read_text().splitlines():
            item = json.loads(line)
            params = tuple(item[key] for key in ('n', 'e', 'floor8', 'floor9'))
            cap = item.get('cap', 121)
            floor7 = item.get('floor7', 107)
            signature = (tuple(params[0]), *params[1:], cap, floor7)
            assert signature not in seen
            seen.add(signature)
            target = direct_model(params[0]) if item['kind'] == 'direct' else model(*params, cap, floor7)
            if item['kind'] == 'direct':
                assert cap == 132 or params[1] <= cap + 48
                assert (params[1], tuple(params[0])) in {(e, c) for e, c, _ in cases()}
            assert verify(target, {int(key): Fraction(value) for key, value in item['y'].items()})
            tally[item['kind']] += 1
        print(f'Exact replay: {dict(tally)}')
        return
    if args.floor7_108:
        assert args.cap == 132
    floor7 = 108 if args.floor7_108 else 107
    with args.records.open('w') as stream:
        for edges, counts, previous in (cases_for_floor108() if args.floor7_108 else cases()):
            if counts[0] >= 3 and (args.cap == 132 or edges <= args.cap + 48):
                item = {'n': counts, 'e': edges, 'floor8': 95, 'floor9': 86,
                        'cap': args.cap, 'kind': 'direct', 'y': {0: 1, 1: 1}}
                assert verify(direct_model(counts), {0: Fraction(1), 1: Fraction(1)})
                print(json.dumps(item, separators=(',', ':')), file=stream, flush=True)
                print(f'{edges},{counts}: directly excluded', flush=True)
                tally['direct'] += 1
                continue

            def trial(floor8, floor9, kind):
                status, multiplier = solve(model(counts, edges, floor8, floor9, args.cap, floor7))
                if status != 'cert':
                    return False
                print(json.dumps({'n': counts, 'e': edges, 'floor8': floor8, 'floor9': floor9,
                                  'cap': args.cap, 'floor7': floor7, 'kind': kind, 'y': multiplier},
                                 separators=(',', ':')), file=stream, flush=True)
                tally[kind] += 1
                return True

            if trial(95, 86, 'unglued') or trial(97, 88, 'glued'):
                print(f'{edges},{counts}: excluded', flush=True)
                continue
            for floor9 in range(previous, 87, -1):
                if not trial(97, floor9, 't9'):
                    break
                print(f'{edges},{counts}: improved t9 <= {floor9 - 1}', flush=True)
    print(f'Found: {dict(tally)}')


if __name__ == '__main__':
    main()
