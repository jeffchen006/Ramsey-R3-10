#!/usr/bin/env python3
"""Tabulate the dispersed mixed-core bands by branch and terminal difficulty."""

import argparse
from collections import Counter, defaultdict
import csv
from itertools import groupby, zip_longest
from pathlib import Path
import json


FIELDS = ('rows', 'lifts', 'first_window', 'later_window', 'hard_rows', 'hard_lifts',
          'fused_degree', 'fused_triangle', 'fused_window', 'fused_edge', 'marked', 'open', 'open_rows',
          'max_hard_per_row', 'max_open_per_row')
REASONS = {'degree conflict': 'fused_degree', 'global triangle': 'fused_triangle',
           'window conflict': 'fused_window', 'cross-window edge conflict': 'fused_edge'}
NAMES = ('front', 'interior', 'tail')


def add(total, counts):
    for key, value in counts.items():
        total[key] = max(total[key], value) if key.startswith('max_') else total[key] + value


def read_band(cover, receipt):
    with cover.open(encoding='ascii') as rows, receipt.open(encoding='ascii') as traces:
        for index, (source, batch) in enumerate(zip_longest(map(json.loads, rows),
                                                           groupby(map(json.loads, traces), key=lambda row: row[0]))):
            assert source is not None and batch is not None and batch[0] == index
            items = list(batch[1])
            lifts = len(source[3])
            first = items[0]
            counts = Counter(rows=1, lifts=lifts)
            if first[1] == -1:
                assert len(items) == 1 and first[2:4] == ['graph', 3]
                counts['first_window'] = lifts
            else:
                assert [row[1] for row in items] == list(range(lifts))
                for _, _, status, *tail in items:
                    if status == 'graph':
                        counts['later_window'] += 1
                    elif status == 'fused':
                        counts[REASONS[tail[0]]] += 1
                    else:
                        assert not tail and status in ('incompatible', 'open')
                        counts['marked' if status == 'incompatible' else 'open'] += 1
                hard = lifts - counts['later_window']
                assert hard == sum(counts[key] for key in (*REASONS.values(), 'open', 'marked'))
                counts['hard_rows'] = bool(hard)
                counts['hard_lifts'] = counts['max_hard_per_row'] = hard
                counts['open_rows'] = bool(counts['open'])
                counts['max_open_per_row'] = counts['open']
            yield ','.join(map(str, source[2][0])), counts


def table(prefix, output):
    with Path(f'{prefix}.branches.tsv').open(encoding='ascii') as stream:
        branches = list(csv.DictReader(stream, delimiter='\t'))
    with output.open('x', encoding='ascii') as out:
        print('band', 'branch', *FIELDS, sep='\t', file=out)
        for name in NAMES:
            stats = defaultdict(Counter)
            for branch, counts in read_band(Path(f'{prefix}.{name}.jsonl'), Path(f'{prefix}.{name}.receipt.jsonl')):
                add(stats[branch], counts)
            total = Counter()
            for row in branches:
                branch = row['branch']
                counts = stats.pop(branch, Counter())
                assert (counts['rows'], counts['lifts']) == (int(row[name]), int(row[f'{name}_lifts']))
                print(name, branch, *(int(counts[key]) for key in FIELDS), sep='\t', file=out)
                add(total, counts)
            assert not stats
            print(name, 'TOTAL', *(int(total[key]) for key in FIELDS), sep='\t', file=out)
            print(name, dict((key, int(total[key])) for key in FIELDS), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prefix', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    table(args.prefix, args.output)
