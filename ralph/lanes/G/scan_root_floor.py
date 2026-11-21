#!/usr/bin/env python3
"""Measure incremental exact degree-six floor reductions against round 1."""

import argparse
import csv
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
from time import process_time

from scan import solve, verify
from typed_lp import PRESENT, build
from check_floor120 import rows119

DEGS = (6, 7, 8, 9)


def model(distribution, threshold, floor6, floor7=104):
    return build(dict(zip(DEGS, distribution)), {6: floor6, 7: floor7, 8: 97, 9: threshold + 1},
                 40, 9, True, PRESENT['combined'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).with_name('t9_round1.csv'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--edges', type=int, nargs='+', default=list(range(167, 180)))
    parser.add_argument('--sample', type=int)
    parser.add_argument('--floor', type=int, choices=(119, 120), default=119)
    parser.add_argument('--floor7', type=int, choices=(105, 106, 107), default=None)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.verify:
        checked = 0
        for line in args.output.read_text().splitlines():
            record = json.loads(line)
            assert record['floor6'] in (118, 119, 120)
            assert record.get('floor7', 104) in (104, 105, 106, 107)
            assert verify(model(record['n'], record['threshold'], record['floor6'], record.get('floor7', 104)),
                          {int(key): Fraction(value) for key, value in record['y'].items()}), record
            checked += 1
        print(f'{checked} exact Farkas certificates passed')
        return
    if args.floor7:
        old_bounds = {}
        filenames = ('root_floor120_certs.jsonl', 'root_floor7_certs.jsonl', 'root_floor7_106_certs.jsonl')
        for name in filenames[:args.floor7 - 104]:
            for line in Path(__file__).with_name(name).read_text().splitlines():
                record = json.loads(line)
                counts, threshold = tuple(record['n']), record['threshold']
                old_bounds[counts] = min(threshold, old_bounds.get(counts, threshold))
        rows = [(edges, counts, min(threshold, old_bounds.get(counts, 99))) for edges, counts, threshold in rows119()
                if edges in args.edges and counts[1] and not (edges == 167 and counts[0])]
    elif args.floor == 120:
        rows = [(edges, counts, threshold) for edges, counts, threshold in rows119() if edges >= 168]
    else:
        with args.source.open() as stream:
            rows = [(int(row['e']), [int(row[f'n{degree}']) for degree in DEGS], int(row['certified_t9_upper']))
                    for row in csv.DictReader(stream)]
    rows = [(edges, distribution, threshold) for edges, distribution, threshold in rows
            if edges in args.edges and (args.floor7 or (edges >= 167 and distribution[0] > 0)) and threshold > 87]
    if args.sample:
        rows = rows[::max(1, len(rows) // args.sample)][:args.sample]
    start = process_time()
    with args.output.open('w') as stream:
        stats = Counter()
        for edges, distribution, old in rows:
            def trial(threshold, floor):
                floor6 = 120 if args.floor7 else floor
                floor7 = floor if args.floor7 else 104
                status, multiplier = solve(model(distribution, threshold, floor6, floor7))
                if status == 'cert':
                    record = {'n': distribution, 'e': edges, 'threshold': threshold,
                              'floor6': floor6, 'y': multiplier}
                    if args.floor7:
                        record['floor7'] = floor7
                    print(json.dumps(record, separators=(',', ':')), file=stream)
                return status == 'cert'

            stats['sample'] += 1
            floor = args.floor7 or args.floor
            if trial(old - 1, floor):
                if trial(old - 1, floor - 1):
                    stats['improvement_without_floor'] += 1
                else:
                    stats['improvement_only_with_floor'] += 1
                best = old - 1
                low = 87
                while low < best:
                    mid = (low + best) // 2
                    if trial(mid, floor):
                        best = mid
                    else:
                        low = mid + 1
                stats['closed_87'] += int(best == 87)
                stats['new_U88'] += int(best <= 88 < old)
                stats['improved_edges'] += old - best
                print(f'{edges},{distribution}: {old}->{best}', flush=True)
        print(f'{dict(stats)} CPU-s={process_time()-start:.3f}', flush=True)


if __name__ == '__main__':
    main()
