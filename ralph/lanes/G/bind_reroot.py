#!/usr/bin/env python3
"""Bind a completed reroot proof schedule to dual-check receipts and traces."""

from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from pathlib import Path


def rows(path):
    return (tuple(line.split()) for line in path.read_text().splitlines())


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('selection', type=Path)
    parser.add_argument('traces', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('logs', type=Path, nargs='+')
    parser.add_argument('--partial', action='store_true')
    parser.add_argument('--also-traces', action='append', type=Path, default=[])
    args = parser.parse_args()
    stores = [args.traces, *args.also_traces]
    schedule = list(rows(args.selection))
    all_keys = set(schedule)
    assert len(all_keys) == len(schedule) and all(len(key) == 3 for key in schedule)
    results = {}
    for path in args.logs:
        for row in rows(path):
            key, status = row[:3], row[3]
            assert key in all_keys and key not in results, (path, row)
            assert status in ('CERT', 'RELAXED_SAT', 'CAP', 'CPU_CAP', 'TIMEOUT', 'SIGNAL')
            if status == 'CERT':
                formula, trace, size = row[4:7]
                assert len(formula) == len(trace) == 64 and all(c in '0123456789abcdef' for c in formula + trace)
                candidates = [store / ('_'.join(key) + '.lrat.gz') for store in stores]
                stored, = (candidate for candidate in candidates if candidate.is_file())
                data = stored.read_bytes()
                assert sha256(data).hexdigest() == trace and len(data) == int(size), (path, row)
            results[key] = row[3:-1]
    assert args.partial or len(results) == len(schedule), (len(results), len(schedule))
    counts = Counter()
    with args.output.open('w') as output:
        for key in schedule:
            evidence = results.get(key, ('MISSING',))
            print(*key, *evidence, sep='\t', file=output)
            counts[key[0], evidence[0]] += 1
    for key, count in sorted(counts.items()):
        print(*key, count)


if __name__ == '__main__':
    main()
