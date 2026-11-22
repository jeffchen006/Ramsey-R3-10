#!/usr/bin/env python3
"""Extrapolate the measured pilot by rows and lifts; not tail bounds."""

from collections import Counter, defaultdict
import csv
from pathlib import Path
import re


def cost(log):
    matches = re.findall(r'cpu=(\d+\.\d+)\+(\d+\.\d+) RSS=', Path(log).read_text())
    user, system = matches[-1]
    return float(user) + float(system)


def extrapolate(value, samples, totals):
    return max(value * total / sample for sample, total in zip(samples, totals, strict=True))


def population(rows):
    return tuple(int(rows[f'{column}_end']) - int(rows[f'{column}_{start}'])
                 for column, start in (('row', 'begin'), ('lift', 'start')))


def sample_size(rows):
    return tuple(sum(int(row[column]) for row in rows) for column in ('rows', 'lifts'))


def estimate():
    by_branch = defaultdict(list)
    by_band = defaultdict(list)
    with Path('metrics.1.tsv').open() as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            by_branch[row['branch']].append(row)
            by_band[row['band']].append(row)
    totals = tuple(map(sum, zip(*(population(rows[0]) for rows in by_branch.values()), strict=True)))
    for key, mode in (('scan_cpu', 'scan'), ('native_cpu', 'native'), ('python_cpu', 'python'),
                      ('receipt_bytes', None), ('open', None)):
        whole_band = {}
        for band, rows in by_band.items():
            value = cost(f'pilot.1.{band}.{mode}.log') if mode else sum(float(row[key]) for row in rows)
            whole_band[band] = round(extrapolate(value, sample_size(rows), totals), 2)
        per_branch = [(max(extrapolate(float(row[key]), sample_size([row]), population(row)) for row in rows), label)
                      for label, rows in by_branch.items()]
        print(key, 'whole bands', whole_band, 'sum branch maxima', round(sum(value for value, _ in per_branch), 2),
              'branch top 3', [(round(value, 2), label) for value, label in sorted(per_branch, reverse=True)[:3]])

    with Path('pilot_opens.1.tsv').open() as stream:
        queue = list(csv.DictReader(stream, delimiter='\t'))
    for subset in (queue, [row for row in queue if row['selected'] == '1']):
        counts = Counter()
        for row in subset:
            index = int(row['projection'])
            branch, = (label for label, rows in by_branch.items()
                       if int(rows[0]['row_begin']) <= index < int(rows[0]['row_end']))
            counts[row['band'], branch] += 1
        print('open pilot subset', len(subset), sorted(counts.items()))

    for mode in ('narrow', 'wide'):
        sizes = Counter()
        for path in Path(f'matched.{mode}').iterdir():
            stem = path.name.split('.')[0].rsplit('_', 1)[0]
            sizes[stem] += path.stat().st_size
        assert len(sizes) == 16
        print(mode, 'CPU run and rebind:', cost(f'matched.{mode}.log'), cost(f'matched.{mode}.rebind.log'),
              'retained bytes after rebind:', sum(sizes.values()), 'maximum per ID:', max(sizes.values()))


if __name__ == '__main__':
    estimate()
