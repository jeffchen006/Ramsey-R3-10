#!/usr/bin/env python3
import argparse
from collections import Counter, defaultdict
from pathlib import Path

from panel18_bind import SLICES, read_integer_rows
from panel16_summary import read_rows


REASONS = ('degree', 'triangle', 'codegree', 'I', 'live')


def id_key(row):
    return int(row['left']), int(row['right'])


def directions(before):
    domains = tuple(count != '0' for count in before.split(','))
    return tuple(all(domains[side::2]) for side in range(2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('pilot', type=Path)
    parser.add_argument('work', type=Path)
    args = parser.parse_args()
    previous = {id_key(row): row for row in read_rows(args.pilot/'pilot.stats')}
    stats = {id_key(row): row for row in read_rows(args.work/'target.stats')}
    slots = {(int(row['frame16']), int(row['frame17'])):
             (int(row['D16']), int(row['d16']), '2333', '3334')
             for row in read_rows(args.source/'survivors.tsv')}
    assert stats.keys() == slots.keys() and len(slots) == 70
    summaries = defaultdict(Counter)
    raw_pilot = set()
    both_pilot = set()
    for row in read_rows(args.source/'pilot-overlap.tsv'):
        key = int(row['D16']), int(row['d16']), '2333', '3334'
        identity = int(row['frame16']), int(row['frame17'])
        assert identity in previous and identity not in raw_pilot
        raw_pilot.add(identity)
        summaries[key]['old_raw'] += 1
        before = tuple(count != '0' for count in previous[identity]['before'].split(','))
        assert tuple(map(int, row['forward_groups'])) == before[0::2]
        assert tuple(map(int, row['reverse_groups'])) == before[1::2]
        assert (row['both'] == '1') == (identity in slots) == all(before)
        if identity in slots:
            assert slots[identity] == key and stats[identity]['before'] == previous[identity]['before']
            assert all(stats[identity][reason] == previous[identity][reason] for reason in REASONS)
            both_pilot.add(identity)
            summaries[key]['old_joint'] += 1
    assert len(raw_pilot) == 32 and both_pilot == {(2501780, 31298)} == stats.keys() & previous.keys()
    with (args.source/'buckets.tsv').open() as parent, (args.work/'marginal-target.buckets.tsv').open() as child:
        next(parent)
        next(child)
        bucket_count = 0
        for first, second in zip(parent, child, strict=True):
            assert first.split() == second.split()
            bucket_count += 1
    assert bucket_count == 11250
    positives = []
    native_fills = defaultdict(Counter)
    for row in read_integer_rows(args.work/'target.fills', 3 + 11 + 13):
        assert row[:2] in slots and 0 <= row[2] < len(REASONS)
        native_fills[row[:2]][row[2]] += 1
        if row[2] == 4:
            positives.append(row)
    audited = {}
    with (args.work/'audit-target.log').open() as stream:
        for line in stream:
            fields = line.split()
            if len(fields) == 5 and fields[2] == 'join':
                identity = tuple(map(int, fields[:2]))
                assert identity not in audited
                audited[identity] = int(fields[-1])
            elif line.startswith('70 verified IDs:'):
                break
        else:
            raise AssertionError('independent audit did not complete')
    assert audited.keys() == slots.keys()
    max_sizes, literal_caps, probe_max = 0, 0, 0
    with (args.work/'keyed.tsv').open('w') as stream:
        print('frame16 frame17 D16 d16 status before after independent_probes', file=stream)
        for identity, key in slots.items():
            row = stats[identity]
            assert row['filtered_cap'] == 'no' and directions(row['before']) == (True, True)
            assert tuple(key[2:]) == (row['shape_l'], row['shape_r'])
            literal_caps += row['literal_cap'] != 'no'
            probe_max = max(probe_max, int(row['literal_probes']))
            max_sizes = max(max_sizes, *map(int, row['before'].split(',')))
            dispositions = tuple(int(row[reason]) for reason in REASONS)
            assert dispositions == tuple(native_fills[identity][index] for index in range(len(REASONS)))
            status = 'live-local' if dispositions[-1] else 'joint-terminal-reject' if any(dispositions) else 'no-joint'
            summaries[key][status] += 1
            summaries[key]['arc-empty'] += '0' in row['after'].split(',')
            print(*identity, *key[:2], status, row['before'], row['after'], audited[identity], file=stream)
    with (args.work/'first-live.tsv').open('w') as stream:
        if positives:
            print(*min(positives), file=stream)
    for key, (raw, forward, reverse, both) in SLICES.items():
        row = summaries[key]
        assert row['old_raw'] == 16
        assert row['no-joint'] + row['joint-terminal-reject'] + row['live-local'] == both
        print(*key, 'raw', raw, 'marginal rejects', raw-both, 'marginal survivors', both,
              'no-joint', row['no-joint'], 'joint-terminal-reject', row['joint-terminal-reject'],
              'live-local', row['live-local'], 'arc-empty', row['arc-empty'],
              'old-raw', row['old_raw'], 'old-joint', row['old_joint'], 'new-joint-tests', both-row['old_joint'])
    print('all', bucket_count, 'host products; all 32 old margin vectors, 1 old joint rechecked')
    print('largest original domain', max_sizes, 'largest native literal probes', probe_max,
          'native literal caps', literal_caps, 'largest independent probes', max(audited.values()))


if __name__ == '__main__':
    main()
