#!/usr/bin/env python3
"""Bind deterministic summaries and compare the pilot against full enumeration."""

from ast import literal_eval
from collections import Counter
from pathlib import Path
from sys import argv

from panel18_bind import read_integer_rows


def budget(path, exhaustive):
    result = {}
    for line in path.read_text().splitlines()[1:]:
        left, right, mask, state, *fields = line.split()
        key = tuple(map(int, (left, right, mask)))
        assert key not in result
        if state == 'pins':
            assert fields == ['-'] * 4
            result[key] = state, None
            continue
        domains, capacity, profiles, overload = map(literal_eval, fields)
        if exhaustive:
            profiles = tuple(profile if count else () for count, profile in zip(domains, profiles, strict=True))
        flags = tuple(int(bool(count)) for count in domains)
        result[key] = state, (flags, capacity, profiles, overload)
    return result


def main(work, original):
    chosen = [case[:2] for case in read_integer_rows(work / 'chosen.tsv', 14)]
    sample = [case[:2] for case in read_integer_rows(work / 'sample.tsv', 14)]
    assert len(chosen) == len(set(chosen)) == 8 and sample == chosen[:2]
    rows = budget(work / 'opt-sample.rows.tsv', False)
    assert rows == budget(original / 'sample.rows.tsv', True)
    assert Counter(key[:2] for key in rows) == dict.fromkeys(sample, 48)
    states = Counter(state for state, _ in rows.values())
    assert states == {'card': 34, 'live': 62}
    for state, data in rows.values():
        if state == 'live':
            flags, capacity, profiles, overload = data
            assert flags == (1,) * 5 and profiles == ((0,) * 12,) * 5
            assert capacity == (5, 4, 4, 3, 4, 3, 3, 3, 3, 2, 3, 3) and overload == ()
    print('exact focus vs exhaustive agreement', len(rows), 'zero all minima', states['live'],
          'empty-domain', states['card'], 'budget', states['budget'])
    print('right pre_domains post_domains raw_probes arc_probes terminals')
    table = (work / 'old.stats').read_text().splitlines()[1:]
    assert not (work / 'old.fills').read_text()
    seen = []
    raw_probes = sample_raw_probes = 0
    for line in table:
        fields = line.split()
        pair = tuple(map(int, fields[:2]))
        seen.append(pair)
        assert len(fields) == 22 and fields[13:15] == ['no', 'no']
        assert set(fields[17:]) == {'0'} and int(fields[12]) == 0
        assert '0' not in fields[15].split(',') and '0' in fields[16].split(',')
        raw_probes += int(fields[11])
        if pair in sample:
            sample_raw_probes += int(fields[11])
        print(fields[1], *fields[15:17], *fields[11:13], sum(map(int, fields[17:])))
    assert seen == chosen
    print('original join exclusions', len(seen), 'raw probes', raw_probes, 'same two pilot raw probes', sample_raw_probes,
          'arc probes 0, terminal calls 0')


if __name__ == '__main__':
    main(*map(Path, argv[1:]))
