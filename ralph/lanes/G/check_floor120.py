#!/usr/bin/env python3
"""Check the complete e<=119 cover and tabulate consequences on pinned cases."""

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import subprocess
import sys

from check_root_cover import graph

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EDGES = range(6, 10)


def checked_catalogue(catalogue, labelg):
    rows = catalogue.read_text().splitlines()
    count = Counter()
    minimum = []
    for line in rows:
        adj = graph.parse_graph6(line)
        assert len(adj) == 33 and graph.triangle_free(adj) and graph.alpha(adj) == 8, line
        edges = sum(map(int.bit_count, adj)) // 2
        count[edges] += 1
        if edges == 118:
            minimum.append(line)
    def canon(lines):
        result = subprocess.run([labelg, '-q'], input='\n'.join(lines) + '\n', check=True, capture_output=True, text=True)
        return set(result.stdout.splitlines())
    assert len(canon(rows)) == len(rows), 'nonisomorphic cover required'
    reference = (HERE / 'root_certs/hog33_118.g6').read_text().splitlines()
    assert canon(reference) == canon(minimum)
    assert dict(count) == {118: 5, 119: 69}, count
    print(f'Exact GR Table 14 cover: {sorted(count.items())}')


def rows119():
    tightened = {}
    for line in (HERE / 'root_floor_certs.jsonl').read_text().splitlines():
        item = json.loads(line)
        assert item['floor6'] == 119
        key, threshold = tuple(item['n']), item['threshold']
        tightened[key] = min(tightened.get(key, threshold), threshold)
    with (HERE / 't9_round1.csv').open() as stream:
        records = list(csv.DictReader(stream))
    assert len(records) == 524
    seen = set()
    for row in records:
        counts = tuple(int(row[f'n{degree}']) for degree in EDGES)
        edge_count = int(row['e'])
        assert min(counts) >= 0 and sum(counts) == 40 and sum(a * b for a, b in zip(counts, EDGES)) == 2 * edge_count
        assert counts not in seen
        seen.add(counts)
        bound = min(int(row['certified_t9_upper']), tightened.get(counts, 99))
        if bound >= 88 and not (edge_count == 166 and counts[0] > 0):
            yield edge_count, counts, bound


def cuts():
    before = tuple(rows119())
    assert len(before) == 454 and sum(bound == 88 for _, _, bound in before) == 20
    print('e,n6,n7,n8,n9,farkas_rhs,t9_upper_floor119')
    count = overlap88 = 0
    for edges, counts, bound in before:
        if edges != 167 or not counts[0]:
            continue
        terms = ((1, 0), (-1, -counts[0]))
        assert sum(coefficient for coefficient, _ in terms) == 0
        rhs = sum(rhs for _, rhs in terms)
        assert rhs == -counts[0] < 0
        print(edges, *counts, rhs, bound, sep=',')
        count += 1
        overlap88 += bound == 88
    assert count == 55
    print(f'# {count} incremental cuts; {len(before)-count} remain; {20-overlap88} further U88 before the floor-120 LP')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalogue', type=Path)
    parser.add_argument('--labelg', default=str(ROOT / 'opt/bin/labelg'))
    args = parser.parse_args()
    if args.catalogue is None:
        cuts()
    else:
        checked_catalogue(args.catalogue, args.labelg)


if __name__ == '__main__':
    main()
