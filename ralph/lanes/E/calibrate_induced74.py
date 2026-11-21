#!/usr/bin/env python3
"""Exhaustive subset checks for the induced-window search."""

from collections import Counter
from itertools import combinations
from pathlib import Path
import subprocess
import sys

from calibrate_window74 import edge_set
from involution_sat import from_graph6, to_graph6
from pairlift74 import project


def calibrate(path):
    data = Path(path).read_text(encoding='ascii').splitlines()[::9]
    total = 0
    for row in data:
        adj = from_graph6(row)
        domain = range(len(adj))
        for root in (None, 0):
            expected = Counter()
            for remove in combinations(domain, 3):
                if root is not None and root not in remove:
                    continue
                sub = project(adj, remove)
                edges = edge_set(sub)
                if (12 <= len(edges) <= 14 and not any(
                        not (edges & set(combinations(tips, 2))) for tips in combinations(range(len(sub)), 4))):
                    expected[to_graph6(sub)] += 1
            actual = Counter()
            for edge_count in range(12, 15):
                args = ['./induced74', '3', '8', str(edge_count)]
                if root is not None:
                    args.append(str(root))
                run = subprocess.run(args, input=row+'\n', text=True, capture_output=True, check=True, timeout=5)
                actual.update(run.stdout.splitlines())
            assert actual == expected
            total += sum(actual.values())
    assert total > 0
    print(f'{2*len(data)} rooted/unrooted (3,4;8) controls; {total} exact labeled projections')


if __name__ == '__main__':
    calibrate(sys.argv[1])
