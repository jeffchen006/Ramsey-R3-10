#!/usr/bin/env python3
"""Bind round-5 keys to the accepted round-4 baseline."""

from collections import Counter
import csv
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent


def main():
    certificates = {}
    for index, line in enumerate((HERE / 'd5_global_cuts.jsonl').read_text().splitlines(), 1):
        certificate = json.loads(line)
        key = certificate['e'], *certificate['n']
        certificates.setdefault(key, []).append((certificate, index))
    counts = Counter()
    closed_by_edges = Counter()
    result = csv.writer(sys.stdout, lineterminator='\n')
    result.writerow(('e', 'n6', 'n7', 'n8', 'n9', 't9_before', 't9_after', 'round5_cut', 'certificate'))
    with (HERE / 'round4_cases.csv').open() as stream:
        for row in csv.DictReader(line for line in stream if not line.startswith('#')):
            if row['round4_cut']:
                continue
            key = tuple(int(row[name]) for name in ('e', 'n6', 'n7', 'n8', 'n9'))
            before = after = int(row['t9_new'])
            status = locator = ''
            for certificate, index in certificates.pop(key, []):
                if certificate['kind'] == 't9':
                    assert certificate['floor9'] - 1 < before
                    after = min(after, certificate['floor9'] - 1)
                else:
                    assert not status
                    status = certificate['kind']
                    locator = f'd5_global_cuts.jsonl:{index}'
            if status:
                closed_by_edges[key[0]] += 1
            counts[status or 'open'] += 1
            counts['t9_improved'] += int(after < before)
            counts['further_U88'] += int(not status and after == 88)
            result.writerow((*key, before, after, status, locator))
    assert not certificates
    assert counts == {'direct': 84, 'unglued': 1, 'open': 283, 't9_improved': 5, 'further_U88': 10}, counts
    print('# ' + ', '.join(f'{name}={count}' for name, count in sorted(counts.items())))
    print('# exclusions by edge level: ' + ', '.join(f'{edges}:{count}' for edges, count in sorted(closed_by_edges.items())))


if __name__ == '__main__':
    main()
