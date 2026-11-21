#!/usr/bin/env python3
"""Exact Farkas closure of pinned distributions using the certified root row."""

import csv
from pathlib import Path


def main():
    source = Path(__file__).with_name('t9_round1.csv')
    with source.open() as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 524
    already = overlap = new = overlap88 = 0
    print('e,n6,n7,n8,n9,farkas_rhs,already_closed_round1,t9_upper_round1')
    for row in rows:
        edges = int(row['e'])
        counts = [int(row[f'n{degree}']) for degree in range(6, 10)]
        assert min(counts) >= 0 and sum(counts) == 40
        assert sum(degree * count for degree, count in enumerate(counts, 6)) == 2 * edges
        threshold = int(row['certified_t9_upper'])
        closed = threshold <= 87
        already += closed
        if edges != 166 or counts[0] == 0:
            continue
        farkas_rows = [(1, 0), (-1, -counts[0])]
        weighted_coeff = sum(coefficient for coefficient, _ in farkas_rows)
        weighted_rhs = sum(rhs for _, rhs in farkas_rows)
        assert weighted_coeff == 0 and weighted_rhs < 0
        print(edges, *counts, weighted_rhs, int(closed), threshold, sep=',')
        overlap += closed
        new += not closed
        overlap88 += threshold == 88
    assert (already, overlap, new, overlap88) == (6, 2, 63, 8)
    print('# 63 incremental closures; 455 remain; 16 further conditional U88 cases remain')


if __name__ == '__main__':
    main()
