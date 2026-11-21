#!/usr/bin/env python3
"""Combine incremental round-3 LP bounds without double-counting closures."""

from collections import Counter
import json
from pathlib import Path

from check_floor120 import rows119

HERE = Path(__file__).resolve().parent


def bounds(name, degree7):
    result = {}
    for line in (HERE / name).read_text().splitlines():
        record = json.loads(line)
        assert record['floor6'] == 120
        if record.get('floor7', 104) != degree7:
            continue
        key = tuple(record['n'])
        result[key] = min(result.get(key, 99), record['threshold'])
    return result


def main():
    initial = tuple(rows119())
    levels = [(104, 'root_floor120_certs.jsonl'), (105, 'root_floor7_certs.jsonl'),
              (106, 'root_floor7_106_certs.jsonl'), (107, 'root_floor7_107_certs.jsonl')]
    new = [(level, bounds(name, level)) for level, name in levels]
    statistics = Counter()
    print('e,n6,n7,n8,n9,t9_before,t9_after,round3_cut')
    for edges, counts, original in sorted(initial):
        if edges == 167 and counts[0]:
            cut = 'root6_at_167'
            current = original
        else:
            cut = ''
            current = original
            for level, table in new:
                current = min(current, table.get(counts, 99))
                if current <= 87:
                    cut = f'root7_floor{level}'
                    break
        print(edges, *counts, original, current, cut, sep=',')
        statistics[cut or 'open'] += 1
        statistics['further_U88'] += int(not cut and current == 88)
    assert len(initial) == 454
    assert [statistics[key] for key in ('root6_at_167', 'root7_floor105', 'root7_floor106', 'root7_floor107', 'open')] == [55, 8, 6, 9, 376]
    print('# ' + ', '.join(f'{key}={value}' for key, value in sorted(statistics.items())))


if __name__ == '__main__':
    main()
