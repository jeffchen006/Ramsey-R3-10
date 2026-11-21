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

DEGS = (6, 7, 8, 9)


def model(distribution, threshold, floor6):
    return build(dict(zip(DEGS, distribution)), {6: floor6, 7: 104, 8: 97, 9: threshold + 1},
                 40, 9, True, PRESENT['combined'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).with_name('t9_round1.csv'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--edges', type=int, nargs='+', default=list(range(167, 180)))
    parser.add_argument('--sample', type=int)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.verify:
        checked = 0
        for line in args.output.read_text().splitlines():
            record = json.loads(line)
            assert record['floor6'] in (118, 119)
            assert verify(model(record['n'], record['threshold'], record['floor6']),
                          {int(key): Fraction(value) for key, value in record['y'].items()}), record
            checked += 1
        print(f'{checked} exact Farkas certificates passed')
        return
    with args.source.open() as stream:
        rows = [(int(row['e']), [int(row[f'n{degree}']) for degree in DEGS], int(row['certified_t9_upper']))
                for row in csv.DictReader(stream)]
    rows = [(edges, distribution, threshold) for edges, distribution, threshold in rows
            if edges in args.edges and edges >= 167 and distribution[0] > 0 and threshold > 87]
    if args.sample:
        rows = rows[::max(1, len(rows) // args.sample)][:args.sample]
    start = process_time()
    with args.output.open('w') as stream:
        stats = Counter()
        for edges, distribution, old in rows:
            def trial(threshold, floor6):
                status, multiplier = solve(model(distribution, threshold, floor6))
                if status == 'cert':
                    record = {'n': distribution, 'e': edges, 'threshold': threshold,
                              'floor6': floor6, 'y': multiplier}
                    print(json.dumps(record, separators=(',', ':')), file=stream)
                return status == 'cert'

            stats['sample'] += 1
            if trial(old - 1, 119):
                if trial(old - 1, 118):
                    stats['improvement_without_floor'] += 1
                else:
                    stats['improvement_only_with_floor'] += 1
                best = old - 1
                low = 87
                while low < best:
                    mid = (low + best) // 2
                    if trial(mid, 119):
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
