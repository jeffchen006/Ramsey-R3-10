#!/usr/bin/env python3
import argparse
from collections import Counter
from pathlib import Path

from panel18_bind import read_integer_rows


def canonical_report(path):
    return [line for line in path.read_text().splitlines() if not line.startswith('timing_ns ')]


def rows(path):
    with path.open() as stream:
        assert next(stream).split() == ['frame16', 'frame17', 'row', 'pole_mask', '(k,z)0', '(k,z)1', '(k,z)2', '(k,z)3']
        for line in stream:
            left, right, row, flag, *counts = line.split()
            yield tuple(map(int, (left, right, row, flag))), tuple(tuple(map(int, item.split(','))) for item in counts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('base', type=Path)
    args = parser.parse_args()
    path = args.base
    cases = {row[:2] for row in read_integer_rows(path / 'pilot.tsv', 14)}
    assert len(cases) == 12 and {left for left, _ in cases} == {42679}
    assert (path / 'indexed.rows.tsv').read_bytes() == (path / 'literal.rows.tsv').read_bytes()
    assert (path / 'indexed.cards.tsv').read_bytes() == (path / 'literal.cards.tsv').read_bytes()
    assert canonical_report(path / 'indexed.log') == canonical_report(path / 'literal.log')
    counts = Counter()
    distinct_rows = set()
    prior = set()
    case_sizes = Counter()
    for (left, right, row, flag), card_sizes in rows(path / 'indexed.rows.tsv'):
        identity = (left, right)
        assert identity in cases and (identity, row) not in prior
        prior.add((identity, row))
        distinct_rows.add(row)
        assert flag == 15 and row.bit_count() == 3
        case_sizes[identity] += 1
        counts.update(count for count, contact in card_sizes if contact == -1)
    assert set(case_sizes) == cases and sum(case_sizes.values()) == 578
    assert sum(counts.values()) == 4 * 578
    with (path / 'indexed.cards.tsv').open() as stream:
        assert next(stream).startswith('core_neutral -1 core_rows ')
        cards = Counter(int(line.split()[0]) for line in stream)
    assert cards[3] and cards[4]
    with (path / 'baseline.stats').open() as stream:
        columns = next(stream).split()
        old_cases = set()
        calls = probes = 0
        elapsed = Counter()
        for line in stream:
            record = dict(zip(columns, line.split(), strict=True))
            identity = int(record['left']), int(record['right'])
            assert identity not in old_cases and identity in cases
            old_cases.add(identity)
            assert record['literal_cap'] == record['filtered_cap'] == 'no'
            assert 0 in map(int, record['after'].split(','))
            probes += int(record['literal_probes'])
            calls += sum(int(record[status]) for status in ('degree', 'triangle', 'codegree', 'I', 'live'))
            for key in columns:
                if key.endswith('_ms'):
                    elapsed[key] += float(record[key])
            print(*identity, case_sizes[identity], int(record['literal_probes']))
    assert old_cases == cases and calls == 0
    assert not (path / 'baseline.fills').read_bytes()
    print('index vs literal all row, card, binding checks agree')
    print('restored card counts', sorted(cards.items()), 'old singleton allocation frequencies', sorted(counts.items()))
    print('header/row count', len(cases), len(prior), 'numerical row masks across disjoint header labels', len(distinct_rows))
    print('baseline: arc-empty', len(old_cases), 'uncapped', len(old_cases), 'literal probes', probes, 'terminal calls', calls)
    print('timing_ms', ' '.join(f'{name}={value:.3f}' for name, value in sorted(elapsed.items())))
    print('explicitly signed-untested', 2542514376-len(old_cases), 'structural-only previous', 56,
          'neither covered', 2542514320-len(old_cases))


if __name__ == '__main__':
    main()
