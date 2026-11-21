#!/usr/bin/env python3
"""Replay incompatibility-clique witnesses; no search in the verifier."""

import argparse
from itertools import combinations
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
import check_graph as graph


def verify(rows, degree, masks):
    assert len(masks) == degree + 1 and len(set(masks)) == len(masks)
    demands = []
    for mask in masks:
        assert 0 < mask < 1 << len(rows)
        endpoints = tuple(vertex for vertex in range(len(rows)) if mask >> vertex & 1)
        assert len(endpoints) in (1, 2)
        if len(endpoints) == 2:
            first, second = endpoints
            assert not (rows[first] & (1 << second)) and not (rows[first] & rows[second]), endpoints
        demands.append(endpoints)
    for left, right in combinations(demands, 2):
        assert any(rows[first] & (1 << second) for first in left for second in right), (left, right)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('trace', type=Path)
    parser.add_argument('--degree', type=int, required=True)
    parser.add_argument('--unproved', type=Path)
    parser.add_argument('--published-edges', type=int, choices=(104, 105, 106))
    parser.add_argument('--labelg', default=str(Path(__file__).resolve().parents[3] / 'opt/bin/labelg'))
    parser.add_argument('--parent', type=Path)
    args = parser.parse_args()
    lines = args.catalogue.read_text().splitlines()
    if args.published_edges is not None:
        expected = {104: 39, 105: 952, 106: 18598}[args.published_edges]
        assert args.degree == 7 and len(lines) == expected
        def canon(data):
            canonical = subprocess.run([args.labelg, '-q'], input=''.join(line + '\n' for line in data),
                                       text=True, capture_output=True, check=True)
            return set(canonical.stdout.splitlines())

        target = canon(lines)
        assert len(target) == expected
        for line in lines:
            rows = graph.parse_graph6(line)
            assert len(rows) == 32 and sum(map(int.bit_count, rows)) == 2 * args.published_edges
            assert graph.triangle_free(rows)
            if args.parent is None:
                assert graph.alpha(rows) == 8
        if args.parent is not None:
            def additions():
                for line in args.parent.read_text().splitlines():
                    rows = graph.parse_graph6(line)
                    assert len(rows) == 32 and sum(map(int.bit_count, rows)) == 2 * (args.published_edges - 1)
                    for first, second in combinations(range(32), 2):
                        if rows[first] & ((1 << second)) or rows[first] & rows[second]:
                            continue
                        rows[first] ^= 1 << second
                        rows[second] ^= 1 << first
                        yield graph.to_graph6(rows)
                        rows[first] ^= 1 << second
                        rows[second] ^= 1 << first
            grown = canon(additions())
            assert grown == target, (len(grown), len(target), len(grown - target))
            print(f'Exact alpha-preserving canonical addition equality from {args.parent.name}')
        print(f'Exact GR Table 14 cover at {args.published_edges}: {expected} valid nonisomorphic inputs')
    checked = set()
    for row in args.trace.read_text().splitlines():
        index, *fields = row.split()
        index = int(index)
        assert 1 <= index <= len(lines) and index not in checked
        verify(graph.parse_graph6(lines[index - 1]), args.degree, tuple(int(mask, 16) for mask in fields))
        checked.add(index)
    missing = [f'{index}\t{line}\n' for index, line in enumerate(lines, 1) if index not in checked]
    if args.unproved is not None:
        assert ''.join(missing) == args.unproved.read_text(), 'unproved input complement mismatch'
    print(f'{len(checked)}/{len(lines)} clique witnesses checked, {len(missing)} require another proof')


if __name__ == '__main__':
    main()
