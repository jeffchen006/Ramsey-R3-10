#!/usr/bin/env python3
"""Check the private-signature equality and scan the e168 degree profiles."""

import argparse
from collections import Counter
from fractions import Fraction
from functools import cache
from itertools import combinations
import json
from pathlib import Path

from check_rows import graph, members, saturated
from scan import solve, verify
from typed_lp import PRESENT, build

HERE = Path(__file__).resolve().parent


@cache
def signatures():
    possible = set()
    matches = 0
    for joined in combinations(tuple(combinations(range(6), 2)), 9):
        degree = Counter(vertex for edge in joined for vertex in edge)
        counts = [degree[vertex] for vertex in range(6)]
        if not all(1 <= item <= 4 for item in counts):
            continue
        if any(counts[left] == counts[right] == 1 for left, right in joined):
            continue
        matches += 1
        possible.add(tuple(sorted(item + 5 for item in counts)))
    assert matches and possible
    return possible, matches


def equality_check(adj, alpha, ramsey_lower):
    assert graph.triangle_free(adj) and graph.alpha(adj) == alpha
    count = shared = 0
    n = len(adj)
    for root, neighbours in enumerate(adj):
        zone = [other for other in range(n) if other != root and not (neighbours >> other & 1)]
        classes = Counter(adj[other] & neighbours for other in zone)
        assert 0 not in classes
        d = neighbours.bit_count()
        private_limit = alpha + 1 - d
        totals = sum(adj[other].bit_count() for other in members(neighbours))
        lower = d + 2 * len(zone) - d * private_limit
        assert totals >= lower
        if totals != lower:
            continue
        count += 1
        for vertex in members(neighbours):
            assert classes[1 << vertex] == private_limit
        for attach, size in classes.items():
            assert 1 <= attach.bit_count() <= 2
            if attach.bit_count() == 2:
                shared += 1
                left, right = tuple(members(attach))
                assert size == 1
                assert (adj[left] & adj[right]).bit_count() == 2
                assert 2 <= adj[left].bit_count() + adj[right].bit_count() + ramsey_lower + 1 - n
    return count, shared


def make(counts, threshold, with_equality, floor8=97):
    current = build(dict(zip(range(6, 10), counts)), {6: 120, 7: 107, 8: floor8, 9: threshold + 1},
                    40, 9, True, PRESENT['combined'])
    if with_equality:
        allowed, _ = signatures()
        forbidden = {key: 1 for key in current.bounds if key[:2] == ('x', 6) and key[2] not in allowed}
        current.le(forbidden, 0, 'degree6_signature_graph_at_e168')
    return current


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--control', type=Path)
    parser.add_argument('--scan', type=Path)
    parser.add_argument('--verify', type=Path)
    parser.add_argument('--unglued', type=Path)
    args = parser.parse_args()
    if args.control:
        rev = graph.parse_matrix(args.control.read_text().splitlines())
        exoo = [mask ^ ((1 << 39) - 1) ^ (1 << vertex) for vertex, mask in enumerate(rev)]
        circ = lambda n, jumps: [sum(1 << ((vertex + sign * jump) % n) for jump in jumps for sign in (-1, 1))
                                 for vertex in range(n)]
        assert equality_check(circ(13, (1, 5)), 4, 6) == (13, 52)
        for name, rows, alpha, rams in (('C13', circ(13, (1, 5)), 4, 6), ('C35', circ(35, (1, 7, 11, 16)), 8, 23),
                                         ('Exoo39-MTF', saturated(exoo), 9, 28)):
            print(name, equality_check(rows, alpha, rams))
        allowed, constructors = signatures()
        print(f'{len(allowed)} admissible degree-six profiles from {constructors} labelled signatures: {sorted(allowed)}')
    if args.verify:
        count = 0
        for line in args.verify.read_text().splitlines():
            item = json.loads(line)
            assert sum(item['n']) == 40 and sum(deg * val for deg, val in enumerate(item['n'], 6)) == 336
            assert item.get('floor8', 97) in (95, 97)
            assert verify(make(item['n'], item['threshold'], True, item.get('floor8', 97)),
                          {int(i): Fraction(val) for i, val in item['y'].items()})
            count += 1
        print(f'Exact Farkas replay: {count} certificates')
    if args.scan or args.unglued:
        cases = []
        for line in (HERE / 'round3_cases.csv').read_text().splitlines()[1:]:
            if line.startswith('168,'):
                e, n6, n7, n8, n9, before, after, cut = line.split(',')
                if int(n6) and not cut:
                    cases.append((list(map(int, (n6, n7, n8, n9))), int(after)))
        assert len(cases) == 47
        stats = Counter()
        target = args.scan or args.unglued
        with target.open('w') as stream:
            for counts, current in cases:
                for threshold, floor8 in ([(85, 95), (85, 97), (87, 95)] if args.unglued else
                                          [(item, 97) for item in sorted({87, current - 1})]):
                    state, weights = solve(make(counts, threshold, True, floor8))
                    stats[threshold == 87, state] += 1
                    if state == 'cert':
                        baseline, _ = solve(make(counts, threshold, False, floor8))
                        stats[threshold == 87, 'previous_' + baseline] += 1
                        print(json.dumps({'n': counts, 'threshold': threshold, 'floor8': floor8, 'y': weights}), file=stream)
                        if args.unglued:
                            break
                print(counts, current, flush=True)
        print(dict(stats))


if __name__ == '__main__':
    main()
