#!/usr/bin/env python3
"""Exact join of the scoped gate against E's immutable named pilot receipts."""

import argparse
from collections import Counter
from decimal import Decimal
import json
from pathlib import Path


def compare(scoped, receipts):
    rows = {row['index']: row for row in map(json.loads, scoped.read_text().splitlines())}
    terminals = {}
    for receipt in receipts:
        for line in receipt.read_text().splitlines():
            index, status, formula, proof, offset, length, cpu, cuts = line.split('\t')
            index = int(index)
            assert index not in terminals
            if status == 'CHECKED':
                assert len(formula) == len(proof) == 64 and int(offset) >= 0 and int(length) > 0
            terminals[index] = status, int(length), Decimal(cpu), len(json.loads(cuts))
    assert rows.keys() == terminals.keys()
    print('row denominator by stage', [sum(row['pairs'][stage] > 0 for row in rows.values()) for stage in range(6)])
    for profile in ((10, 10, 12), (10, 11, 11)):
        counts = [sum(tuple(row['profile']) == profile and row['pairs'][stage] > 0 for row in rows.values()) for stage in range(6)]
        print(profile, counts)
    for selector in (True, False):
        chosen = [index for index, row in rows.items() if bool(row['retained']) == selector]
        statuses = Counter(terminals[index][0] for index in chosen)
        print('keep' if selector else 'veto', len(chosen), sorted(statuses.items()),
              'bytes', sum(terminals[index][1] for index in chosen),
              'cpu', sum(terminals[index][2] for index in chosen),
              'lazy', sum(terminals[index][3] for index in chosen))
    gate = sum(Decimal(str(row['cpu'])) for row in rows.values())
    avoidable = sum(terminals[index][2] for index, row in rows.items() if not row['retained'])
    print('in-process gate CPU-s', gate, 'hypothetical same-pilot net CPU-s', avoidable-gate)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scoped', type=Path)
    parser.add_argument('receipts', type=Path, nargs='+')
    args = parser.parse_args()
    compare(args.scoped, args.receipts)
