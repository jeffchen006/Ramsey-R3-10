#!/usr/bin/env python3
import argparse
import csv
import math
import re
from collections import Counter
from pathlib import Path


def counts_table(filepath):
    with filepath.open() as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            values = {key: int(value) for key, value in row.items()}
            profile = (values['core_edges'], *(values[f'c{i}'] for i in range(1, 7)))
            columns = Counter(profile[1:])
            assert values['C_maps'] == math.prod(math.factorial(size) for size in columns.values())
            assert values['raw_maps'] == values['C_maps'] * values['h19_packs'] * values['h21_packs']
            assert 0 < values['h19_marks'] <= values['h19_packs']
            assert 0 < values['h21_marks'] <= values['h21_packs']
            yield profile, values


def read_transcript(logfile, profile, raw_maps):
    text = logfile.read_text()
    assert 'required profile ' + ' '.join(map(str, profile)) + '\n' in text
    expected = re.findall(r'^expected raw maps=(\d+) left input=(\d+) right input=(\d+) profiles=1$', text, re.M)
    assert len(expected) == 1 and int(expected[0][0]) == raw_maps
    stage = re.findall(r'^token-compatible pack maps=(\d+) column-compatible mark maps=(\d+) tested pack maps=(\d+)$', text, re.M)
    assert len(stage) == 1
    actual_raw, column_maps, tested = map(int, stage[0])
    assert actual_raw == raw_maps and tested <= raw_maps
    assert column_maps <= tested
    finish = re.findall(r'^cached base=(\d+) single=(\d+) pair=(\d+) pass=(\d+) defer=(\d+) .* relaxed wing counts=0$', text, re.M)
    assert len(finish) == 1
    base, single, pair, passed, deferred = map(int, finish[0])
    assert base + single + pair + passed + deferred == tested
    times = re.findall(r'^cpu_s=(\S+)$', text, re.M)
    assert len(times) == 1 and float(times[0]) >= 0
    return tested, passed, deferred, float(times[0])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('projection', type=Path)
    parser.add_argument('counts', type=Path)
    parser.add_argument('--runs', type=Path)
    parser.add_argument('--budget', type=int, default=0)
    args = parser.parse_args()

    projection = {}
    for line in args.projection.read_text().splitlines():
        *profile, right_count = map(int, line.split())
        assert len(profile) == 7 and tuple(profile) not in projection
        projection[tuple(profile)] = right_count
    counts = {}
    for profile, row in counts_table(args.counts):
        assert profile not in counts and row['h21_packs'] == projection[profile]
        counts[profile] = row
    empty = sorted(projection.keys() - counts.keys())
    print(f'profiles={len(projection)} present={len(counts)} without H19={len(empty)} '
          f'exact raw maps={sum(row["raw_maps"] for row in counts.values())}')
    print('absent', ' '.join(','.join(map(str, profile)) for profile in empty))
    eligible = sorted((row['raw_maps'], profile) for profile, row in counts.items() if row['raw_maps'] <= args.budget)
    print('bounded', ' '.join(f'{raw_maps}:{",".join(map(str, profile))}' for raw_maps, profile in eligible))

    if not args.runs:
        return
    print('profile\traw_maps\ttested\tpass\tdefer\tcpu_s\tresult')
    for logfile in sorted(args.runs.glob('*.log')):
        profile = tuple(map(int, logfile.stem.split(',')))
        raw_maps = counts[profile]['raw_maps']
        tested, passed, deferred, cpu = read_transcript(logfile, profile, raw_maps)
        pins = logfile.with_suffix('.tsv')
        with pins.open() as stream:
            pin_count = Counter(int(line.split()[4]) for line in stream)
        assert pin_count == Counter({status: size for status, size in [(3, passed), (4, deferred)] if size})
        print(f'{logfile.stem}\t{raw_maps}\t{tested}\t{passed}\t{deferred}\t{cpu:g}\t'
              + ('OPEN' if passed or deferred else 'ENUM-ZERO'))


if __name__ == '__main__':
    main()
