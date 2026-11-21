#!/usr/bin/env python3
"""Materialize the critic's round-6 baseline and its scoped key lists."""

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
FIELDS = ('e', 'n6', 'n7', 'n8', 'n9')


def ledger():
    overlap = defaultdict(list)
    for line in (HERE / 'floor108_overlap.jsonl').read_text().splitlines():
        record = json.loads(line)
        assert record['floor7'] == 108
        overlap[(record['e'], *record['n'])].append(record)
    baseline = {}
    cut = {}
    with (HERE / 'round5_cases.csv').open() as stream:
        for row in csv.DictReader(line for line in stream if not line.startswith('#')):
            key = tuple(int(row[field]) for field in FIELDS)
            if row['round5_cut']:
                assert key not in overlap
                continue
            threshold = int(row['t9_after'])
            close = ''
            for record in overlap.pop(key, []):
                if record['kind'] == 't9':
                    threshold = min(threshold, record['floor9'] - 1)
                else:
                    assert not close and record['kind'] in {'unglued', 'glued'}
                    close = record['kind']
            if close:
                cut[key] = close
            else:
                baseline[key] = threshold
    assert not overlap and len(cut) == 5 and len(baseline) == 278
    assert sum(key[0] == 168 and key[1] > 0 for key in baseline) == 20
    assert list(baseline.values()).count(88) == 10
    return baseline, cut


if __name__ == '__main__':
    import sys

    baseline, cut = ledger()
    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow((*FIELDS, 't9', 'cut'))
    for key in sorted(baseline.keys() | cut.keys()):
        writer.writerow((*key, baseline.get(key, ''), cut.get(key, '')))
