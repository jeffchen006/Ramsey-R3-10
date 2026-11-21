#!/usr/bin/env python3
"""Check member validity, edge levels, distinctness, and the Angeltveit count."""

import argparse
from collections import Counter
from pathlib import Path
import subprocess

from check_root_cover import graph

HERE = Path(__file__).resolve().parent
PUBLISHED_TOTAL = 14395


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('e120', type=Path)
    parser.add_argument('e121', type=Path)
    parser.add_argument('--allow-gap', action='store_true')
    parser.add_argument('--labelg', type=Path, default=HERE.parents[2] / 'opt/bin/labelg')
    args = parser.parse_args()
    known = Counter()
    groups = [(None, HERE / 'root_certs/complete33_le119.g6'), (120, args.e120), (121, args.e121)]
    for expected, path in groups:
        lines = path.read_text().splitlines()
        steps = ('-q', '-S')
        canonical = subprocess.run([args.labelg, *steps, path], capture_output=True, text=True, check=True)
        assert len(set(canonical.stdout.splitlines())) == len(lines), (path, 'isomorphic duplicates')
        for line in lines:
            adj = graph.parse_graph6(line)
            edges = sum(map(int.bit_count, adj)) // 2
            assert len(adj) == 33 and (edges in (118, 119) if expected is None else edges == expected), line
            assert graph.triangle_free(adj) and graph.alpha(adj) == 8, line
            known[edges] += 1
        print(f'{path.name}: {len(lines)} independently checked roots', flush=True)
    assert known[118] == 5 and known[119] == 69
    gap = PUBLISHED_TOTAL - sum(known.values())
    assert 0 <= gap and (gap == 0 or args.allow_gap), (known, gap)
    print(f'{dict(sorted(known.items()))}; combined gap={gap}')


if __name__ == '__main__':
    main()
