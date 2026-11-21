#!/usr/bin/env python3
"""Verify the graph validity, degree census, and deficit arithmetic for low windows."""

import argparse
from collections import Counter
from pathlib import Path

from involution_cores import bits
from involution_sat import from_graph6, witnesses


def read_census(path, order, edges, count):
    raw = path.read_text(encoding='ascii').splitlines()
    assert len(raw) == len(set(raw)) == count
    hist = Counter()
    for row in raw:
        adj = from_graph6(row)
        assert len(adj) == order
        assert sum(mask.bit_count() for mask in adj) == 2 * edges
        assert not any(adj[left] & adj[right] for left in range(order) for right in bits(adj[left]))
        assert next(witnesses(adj, (1 << order) - 1, 8), None) is None
        hist[sum(mask.bit_count() == 7 for mask in adj)] += 1
    print(f'order={order} edges={edges} count={count} degree-seven histogram: {sorted(hist.items())}')
    return hist


def arithmetic():
    expected = [(8, 0, 0), (8, 0, 2), (9, 0, 0), (10, 0, 0), (11, 0, 0), (12, 0, 0)]
    survivors = []
    for core_edges in range(8, 13):
        for core_deficit in range(3):
            surplus = 24 - 2 * core_edges - core_deficit
            if surplus < 0:
                continue
            for group_deficit in range(5 - 2 * core_deficit):
                if (group_deficit + core_deficit) % 2:
                    continue
                lower_low_windows = group_deficit + 2 * core_deficit
                if lower_low_windows * (4 - core_deficit) <= surplus:
                    survivors.append((core_edges, core_deficit, group_deficit))
    assert survivors == expected
    print('surviving (e(W), core deficit, attachment deficit):', survivors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path)
    parser.add_argument('--control', action='store_true')
    args = parser.parse_args()
    if args.control:
        assert sum(read_census(args.file, 25, 65, 396).values()) == 396
    else:
        assert read_census(args.file, 26, 73, 62) == {0: 15, 1: 16, 2: 31}
        arithmetic()


if __name__ == '__main__':
    main()
