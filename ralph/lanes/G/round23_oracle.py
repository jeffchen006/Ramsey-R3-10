"""Crosswalk independent A blockers and mutant plants into G's address scheme."""

import json
import sys
from pathlib import Path

from round22_control import unflatten
from round22_deep import projected_activity
from round23_h5 import Physical, build, load_models


def convert(oracle, row):
    size = len(oracle.grid)
    record = dict(grid=[], options=[], boundary=[])
    for site in row['sites']:
        if isinstance(site, int):
            record['boundary'].append(site)
        elif site[0] < size:
            assert site[0] == site[1]
            record['grid'].append(site[0])
        else:
            record['options'].append(tuple(coord - size for coord in site))
    return {key: sorted(items) for key, items in record.items()}


def val(clause, positive):
    return any(literal in positive if literal > 0 else -literal not in positive for literal in clause)


def check(ref, previous):
    fixtures = json.loads(ref.read_text())
    assert fixtures['schema'] == 'h5.physical-blocker.v1'
    rows = json.loads((previous / 'manifest.json').read_text())
    crossed = 0
    for target in fixtures['targets']:
        board = target['board']
        oracle = Physical(rows[board]['grid'])
        model = load_models(previous / 'work' / f'b{board:03}' / 'solve.log')
        for key in ('witness', 'repeated_witness'):
            witness = target[key]
            assert list(oracle.row(convert(oracle, witness), 10)) == witness['compact']
            assert not val(witness['compact'], model)
            crossed += 1
    assert crossed == 4
    for variant, witness in fixtures['controls'].items():
        plant = witness['plant']
        fold, oracle = build(unflatten(plant['board'], 3), '', target=False, bound=7)
        positive = projected_activity(fold, plant)
        absent, graph = oracle.model_witness(positive, 7)
        assert absent is None and graph == plant['graph']
        record = convert(oracle, witness)
        if variant == 'short_padding':
            try:
                oracle.row(record, 7)
            except AssertionError:
                pass
            else:
                raise AssertionError('bad length accepted')
            row = oracle.row(record, 6)
            assert not val(row, positive)
        else:
            row = oracle.row(record, 7)
            omitted = witness['omitted_guard' if variant == 'missing_guard' else 'omitted_literal']
            assert val(row, positive) and not val(set(row) - {omitted}, positive)
        assert list(row) == witness['compact']
    print('4 independently supplied physical I10 clauses, 3 width-three lost-positive mutations')


if __name__ == '__main__':
    check(*map(Path, sys.argv[1:]))
