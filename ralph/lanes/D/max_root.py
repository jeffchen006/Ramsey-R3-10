#!/usr/bin/env python3
"""Maximum-square edge cover and exact mask-projection rechecking."""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import sys
import time

from catalogue_m3 import covers, representative, swap

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'C'))
from kernel_projection import Projection, bits, by_edge, decode, independent_masks


def squares_floor(order, degree):
    return 2 * degree * (degree - 1) - 3 * (order - degree - 1)


def edge_floor(order, degree):
    return max(degree - 2, (2 * squares_floor(order, degree) + degree - 1) // degree)


def count_edges(kernel):
    return sum(mask.bit_count() for mask in kernel) // 2


def catalogue(order, degree):
    width = degree - 1
    signatures = sorted({min(sig, swap(sig)) for sig in covers(width, width - 1, 2 * width)},
                        key=lambda sig: (sum(left + right - (kind == 'path') for left, right, kind in sig), sig))
    for signature in signatures:
        if order < 6 * degree - 12 and (2, 2, 'cycle') in signature:
            continue
        if sum(left + right - (kind == 'path') for left, right, kind in signature) >= edge_floor(order, degree):
            yield representative(width, signature)


class MaxProjection(Projection):
    def __init__(self, kernel, order, degree, depth=3, strong=False, bounds='matching'):
        super().__init__(kernel, order, degree, 3, depth, strong)
        if not self.masks or bounds == 'base':
            return
        width = len(kernel)
        all_in = (1 << width) - 1
        sides = (1 << (degree - 1)) - 1, all_in ^ ((1 << (degree - 1)) - 1)
        adj = [mask | (1 << (width + (coord >= degree - 1))) for coord, mask in enumerate(kernel)]
        adj += [sides[0] | (1 << (width + 1)), sides[1] | (1 << width)]
        maximum = count_edges(kernel)
        max_singles = min(degree, (degree * maximum) // 2 - squares_floor(order, degree))
        covered = [tuple(col for col, mask in enumerate(self.masks) if mask >> coord & 1)
                   for coord in range(width + 2)]

        def add(terms, rhs, name):
            if terms or rhs < 0:
                self.rows.append((tuple(sorted(terms.items())), rhs, name))

        for side, part in enumerate(sides):
            single = {col: 1 for col, mask in enumerate(self.masks) if (mask & part).bit_count() == 1}
            isolated = sum(not kernel[coord] for coord in bits(sides[1 - side]))
            add(single, max_singles - isolated, f'max-singles:{side}')
        if max_singles == 0:
            for first, second in combinations(range(width), 2):
                if not adj[first] >> second & 1:
                    fixed = (adj[first] & adj[second]).bit_count()
                    add({col: -1 for col in covered[first] if self.masks[col] >> second & 1},
                        fixed - 2, f'no-singles:{first}:{second}')
        independent = (list(independent_masks(adj, (1 << len(adj)) - 1)) if bounds == 'padding' else [])
        for first, second in combinations(range(width + 2), 2):
            if not adj[first] >> second & 1:
                continue
            first_neigh = adj[first] ^ (1 << second)
            second_neigh = adj[second] ^ (1 << first)
            fixed = sum((adj[coord] & second_neigh).bit_count() for coord in bits(first_neigh))
            one_out = {col: (self.masks[col] & second_neigh).bit_count() for col in covered[first]}
            one_out.update({col: (self.masks[col] & first_neigh).bit_count() for col in covered[second]})
            one_out = {col: value for col, value in one_out.items() if value}
            add(one_out, maximum - fixed, f'max-square:{first}:{second}')
            if first >= width or second >= width:
                if 2 * squares_floor(order, degree) == degree * maximum:
                    add({col: -coeff for col, coeff in one_out.items()}, fixed - maximum,
                        f'every-square:{first}:{second}')
                continue
            if bounds == 'linear':
                continue
            outside_incident = covered[first] + covered[second]
            add(one_out, maximum - fixed - max(0, 2 * (degree - 1) - first_neigh.bit_count()
                                                - second_neigh.bit_count() - degree),
                f'max-square-matching:{first}:{second}')
            for seed in independent:
                if not seed or seed >> first & 1 or seed >> second & 1:
                    continue
                if seed.bit_count() < degree - 1:
                    continue
                alpha_slack = degree - seed.bit_count()
                if alpha_slack >= 2 * (degree - 1) - first_neigh.bit_count() - second_neigh.bit_count():
                    continue
                terms = one_out.copy()
                for col in outside_incident:
                    if not self.masks[col] & seed:
                        terms[col] = terms.get(col, 0) + 1
                add(terms, maximum - fixed + alpha_slack, f'max-square-padding:{first}:{second}:{seed}')


def calibration(path, args):
    total = 0
    cache = {}
    hg = set(catalogue(16, 5))
    from catalogue_m3 import signature_of

    assert hg
    accepted = {signature_of(4, line) for line in hg}
    frequencies = Counter()
    for line in path.read_text().splitlines():
        graph = decode(line)
        instances = [by_edge(graph, first, second) for first, row in enumerate(graph)
                     for second in bits(row) if second > first]
        maximum = max(count_edges(kernel) for kernel, _ in instances)
        frequencies[maximum] += 1
        for kernel, counts in instances:
            if count_edges(kernel) != maximum:
                continue
            key = tuple(kernel)
            if key not in cache:
                from kernel_projection import encode
                sig = signature_of(4, encode(kernel))
                assert min(sig, swap(sig)) in accepted
                cache[key] = MaxProjection(kernel, 16, 5, args.depth, args.strong, args.bounds)
            cache[key].replay(counts)
            total += 1
    assert sum(frequencies.values()) == 5
    print(f'PASS C16 all five classes: {total} maximum-root incidences, maxima {dict(sorted(frequencies.items()))}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('catalogue', 'calibrate', 'scan', 'verify'))
    parser.add_argument('--order', type=int, default=40)
    parser.add_argument('--degree', type=int, default=9)
    parser.add_argument('--depth', type=int, default=3, choices=range(1, 5))
    parser.add_argument('--strong', action='store_true')
    parser.add_argument('--bounds', choices=('base', 'linear', 'matching', 'padding'), default='matching')
    parser.add_argument('--sample-mod', type=int, default=1)
    parser.add_argument('--sample-rem', type=int, default=0)
    parser.add_argument('--control', type=Path)
    args = parser.parse_args()
    assert 0 <= args.sample_rem < args.sample_mod
    if args.mode == 'calibrate':
        calibration(args.control, args)
        return
    codes = list(catalogue(args.order, args.degree))
    selected = {index: code for index, code in enumerate(codes) if index % args.sample_mod == args.sample_rem}
    if args.mode == 'catalogue':
        for index, code in selected.items():
            print(index, count_edges(decode(code)), code, sep='\t')
        return
    start = time.process_time()
    results = Counter()
    if args.mode == 'scan':
        for index, code in selected.items():
            kernel = decode(code)
            model = MaxProjection(kernel, args.order, args.degree, args.depth, args.strong, args.bounds)
            status, proof = model.solve()
            edges = count_edges(kernel)
            record = dict(index=index, code=code, edges=edges, status=status, proof=proof,
                          rows=len(model.rows), columns=len(model.masks))
            print(json.dumps(record, separators=(',', ':')), flush=True)
            results[edges, status] += 1
    else:
        seen = set()
        for line in sys.stdin:
            record = json.loads(line)
            index = record['index']
            assert index not in seen and selected[index] == record['code']
            seen.add(index)
            kernel = decode(record['code'])
            assert count_edges(kernel) == record['edges']
            if record['status'] == 'cert':
                model = MaxProjection(kernel, args.order, args.degree, args.depth, args.strong, args.bounds)
                assert len(model.masks) == record['columns'] and len(model.rows) == record['rows']
                model.check(record['proof'])
            else:
                assert record['proof'] is None
            results[record['edges'], record['status']] += 1
        assert seen == set(selected)
    print(f'{args.mode} {sorted(results.items())}; CPU {time.process_time() - start:.3f}s', file=sys.stderr)


if __name__ == '__main__':
    main()
