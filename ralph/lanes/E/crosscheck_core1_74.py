#!/usr/bin/env python3
"""Artifact-only crosscheck; it runs no encoders, solvers or proof checkers."""

from collections import Counter
from itertools import groupby
import json
from pathlib import Path


def roster(path):
    rows = [tuple(json.loads(row)[:2]) for row in Path(path).read_bytes().splitlines()]
    assert rows == sorted(set(rows))
    return set(rows)


def main():
    pending = roster('../r20_shared/residual.jsonl')
    accepted = roster('accepted.1.jsonl')
    remaining = roster('remaining.1.jsonl')
    assert not accepted & remaining and accepted | remaining == pending

    record_rows = list(map(json.loads, Path('checked.1.jsonl').read_bytes().splitlines()))
    records = {tuple(case['id']): case for case in record_rows}
    assert records.keys() == accepted and len(records) == len(record_rows)
    attempted = {tuple(map(int, item.name.split('_'))) for item in Path('target').iterdir()}
    assert accepted <= attempted <= pending

    by_index = {index: list(keys) for index, keys in groupby(sorted(accepted), key=lambda key: key[0])}
    with Path('../r18_shared/cover.1.jsonl').open('rb') as cover:
        for index, raw in enumerate(cover):
            if index not in by_index:
                continue
            key, profile, groups, omitted = json.loads(raw)
            assert key == 'G?bFbo' and profile == [10, 10, 11, 11]
            for identity in by_index.pop(index):
                actual = omitted[identity[1]]
                assert records[identity]['omitted'] == actual
                assert [sum(mask.bit_count() for mask in group) for group in [*groups, actual]] == profile
    assert not by_index

    proof_markers = set()
    for identity, record in records.items():
        folder = Path('target')/f'{identity[0]}_{identity[1]}'
        reference = (folder/'reference8.cnf').read_bytes().splitlines()
        narrow = (folder/'width3.cnf').read_bytes().splitlines()
        for cnf in (reference, narrow):
            prefix, form, variables, clauses = cnf[0].split()
            assert (prefix, form) == (b'p', b'cnf') and int(clauses) == len(cnf) - 1
        assert reference[0].split()[2] == narrow[0].split()[2]
        assert not (Counter(narrow[1:]) - Counter(reference[1:])), identity
        stem = 'width3' if record['width'] == 3 else 'reference8'
        for extension, marker in (('cake_lpr', b's VERIFIED UNSAT'), ('lrat-check', b'c VERIFIED')):
            path = folder/f'{stem}.{extension}.log'
            assert marker in path.read_bytes().splitlines()
            proof_markers.add(path)
    if not remaining:
        assert len(proof_markers) == (len(list(Path('target').rglob('*.cake_lpr.log'))) +
                                      len(list(Path('target').rglob('*.lrat-check.log'))))
    print('independent artifact check:', len(accepted), 'actual omitted groups and raw CNF submultisets;',
          len(proof_markers), 'checker markers;', len(remaining), 'unproved IDs', flush=True)


if __name__ == '__main__':
    main()
