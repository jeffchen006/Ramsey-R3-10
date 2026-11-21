#!/usr/bin/env python3
"""Emit the exact new-cut/U88 index, with a witness locator for each cut."""

import csv
import json
from collections import Counter
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def main():
    names = {105: 'root_floor7_certs.jsonl', 106: 'root_floor7_106_certs.jsonl',
             107: 'root_floor7_107_certs.jsonl'}
    witnesses = {}
    known = {}
    for level, name in names.items():
        for index, line in enumerate((HERE / name).read_text().splitlines(), 1):
            record = json.loads(line)
            if record['threshold'] == 87 and record.get('floor7', 104) == level:
                witnesses[level, tuple(record['n'])] = (name, index)
    with (HERE / 'root_certs/closed167.csv').open() as stream:
        for index, row in enumerate(csv.DictReader(line for line in stream if not line.startswith('#')), 2):
            key = tuple(int(row[f'n{degree}']) for degree in range(6, 10))
            assert int(row['farkas_rhs']) == -key[0] < 0
            known[key] = ('root_certs/closed167.csv', index)
    stats = Counter()
    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow(('e', 'n6', 'n7', 'n8', 'n9', 'status', 'local_evidence', 'evidence_line'))
    with (HERE / 'round3_cases.csv').open() as stream:
        for row in csv.DictReader(line for line in stream if not line.startswith('#')):
            key = tuple(int(row[f'n{degree}']) for degree in range(6, 10))
            status = row['round3_cut']
            if status == 'root6_at_167':
                witness = known[key]
            elif status.startswith('root7_floor'):
                witness = witnesses[int(status.removeprefix('root7_floor')), key]
            elif not status and row['t9_after'] == '88':
                status = 'open_if_U88_unproved'
                witness = ('round3_cases.csv', '')
            else:
                assert not status
                continue
            stats[status] += 1
            writer.writerow((row['e'], *key, status, *witness))
    assert stats == {'root6_at_167': 55, 'root7_floor105': 8, 'root7_floor106': 6,
                     'root7_floor107': 9, 'open_if_U88_unproved': 13}, stats


if __name__ == '__main__':
    main()
