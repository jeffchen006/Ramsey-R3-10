#!/usr/bin/env python3
"""Combine independent e168 exclusions and the updated t9 bounds."""

from collections import Counter
import csv
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def main():
    equality = {}
    tightening = {}
    for index, line in enumerate((HERE / 'private_equality_cuts.jsonl').read_text().splitlines(), 1):
        item = json.loads(line)
        assert item['floor8'] == 95 and item['threshold'] == 85
        equality[tuple(item['n'])] = index
    for line in (HERE / 'private_equality_t9.jsonl').read_text().splitlines():
        item = json.loads(line)
        key = tuple(item['n'])
        tightening[key] = min(item['threshold'], tightening.get(key, 99))
    packing = {(5, 0, 9, 26): 1, (6, 2, 2, 30): 2}
    assert len(equality) == 6 and not (equality.keys() & packing.keys())
    stats = Counter()
    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow(('e', 'n6', 'n7', 'n8', 'n9', 't9_previous', 't9_new', 'round4_cut', 'certificate'))
    with (HERE / 'round3_cases.csv').open() as stream:
        for row in csv.DictReader(line for line in stream if not line.startswith('#')):
            if row['round3_cut']:
                continue
            key = tuple(int(row[f'n{degree}']) for degree in range(6, 10))
            old = int(row['t9_after'])
            new = min(old, tightening.get(key, 99))
            status = locator = ''
            if key in equality:
                status = 'signature_graph_LP'
                locator = f'private_equality_cuts.jsonl:{equality[key]}'
            elif key in packing:
                status = 'private_pair_packing'
                locator = f'check_private_packing_cuts.py:case{packing[key]}'
            stats[status or 'open'] += 1
            stats['further_U88'] += int(not status and new == 88)
            writer.writerow((row['e'], *key, old, new, status, locator))
    assert stats == {'open': 368, 'signature_graph_LP': 6, 'private_pair_packing': 2, 'further_U88': 12}, stats
    print('# ' + ', '.join(f'{key}={value}' for key, value in sorted(stats.items())))


if __name__ == '__main__':
    main()
