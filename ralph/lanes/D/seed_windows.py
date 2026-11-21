#!/usr/bin/env python3
"""Independent boundary seeds, exact small residual bounds, and transport pilots."""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import subprocess
import time

from kernel_projection import decode, independent_masks
from max_root import catalogue, count_edges, squares_floor
from q22_root import append_q22, check_pair_formula, exact_square_counts
from transport_root import Transport


FLOORS = ((0,), (0, 0, 1), (0, 0, 0, 1, 2, 5),
          (0, 0, 0, 0, 1, 2, 3, 6, 10))


def check_floors(geng):
    for alpha, floors in enumerate(FLOORS):
        for order in range(1, len(floors) + 1):
            lines = subprocess.check_output([geng, '-tq', str(order)], text=True).splitlines()
            found = []
            for line in lines:
                graph = decode(line)
                if not any(seed.bit_count() > alpha for seed in independent_masks(graph, (1 << order) - 1)):
                    found.append(sum(row.bit_count() for row in graph) // 2)
            if order < len(floors):
                assert min(found) == floors[order], (order, alpha, min(found))
            else:
                assert not found, (order, alpha)
    print('PASS small triangle-free windows: exact minima and next-order emptiness', FLOORS)


def effective_seeds(kernel, degree, largest_slack=3):
    width = len(kernel)
    left = (1 << (degree - 1)) - 1
    interior = (1 << width) - 1
    right = interior ^ left
    adj = [mask | (1 << (width + (coord >= degree - 1))) for coord, mask in enumerate(kernel)]
    adj += [left | (1 << (width + 1)), right | (1 << width)]
    effective = {}
    for seed in independent_masks(adj, (1 << len(adj)) - 1):
        slack = degree - seed.bit_count()
        if slack > largest_slack:
            continue
        if slack < 0:
            return [(0, -1)]
        pattern = seed & interior
        effective[pattern] = min(slack, effective.get(pattern, slack))
    return sorted((pattern, slack) for pattern, slack in effective.items()
                  if not any((other & pattern == other) and bound <= slack
                             for other, bound in effective.items() if other != pattern))


def supporting_lines(alpha):
    floors = FLOORS[alpha]
    lines = []
    for slope in range(1, 6):
        intercept = min(edges - slope * order for order, edges in enumerate(floors))
        if any(edges == slope * order + intercept and edges > 0 for order, edges in enumerate(floors)):
            lines.append((slope, intercept))
    return lines


def append_windows(model, kernel, degree, per_mask):
    seen = {(terms, bound) for terms, bound, _ in model.rows}

    def add(terms, bound, name):
        row = tuple(sorted((column, coeff) for column, coeff in terms.items() if coeff))
        if (row or bound < 0) and (row, bound) not in seen:
            seen.add((row, bound))
            model.rows.append((row, bound, name))

    patterns = 0
    for seed, slack in effective_seeds(kernel, degree):
        avoid = {mask: col for mask, col in model.p.items() if not mask & seed}
        if not avoid:
            continue
        patterns += 1
        if slack < 0:
            add({}, -1, 'window:forbidden-boundary-seed')
            break
        have = Counter(avoid.values())
        add(have, len(FLOORS[slack]) - 1, f'window-order:{seed}:{slack}')
        have_edges = Counter()
        stars = {mask: Counter() for mask in avoid} if per_mask else {}
        pairs = combinations(sorted(avoid), 2)
        for pair in pairs:
            column = model.arcs.get(pair)
            if column is None:
                continue
            have_edges[column] += 1
            if per_mask:
                first, second = pair
                stars[first][column] += 1
                stars[second][column] += 1
        for slope, intercept in supporting_lines(slack):
            row = Counter({col: coeff * slope for col, coeff in have.items()})
            row.subtract(have_edges)
            add(row, -intercept, f'window-edge-floor:{seed}:{slack}:{slope}')
        for mask, terms in stars.items():
            terms[avoid[mask]] -= slack
            add(terms, 0, f'window-neighbor-cap:{seed}:{slack}:{mask}')
    return patterns


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('index', type=int, nargs='?', default=34)
    parser.add_argument('--forest', action='store_true')
    parser.add_argument('--q22', action='store_true')
    parser.add_argument('--variant', choices=('base', 'windows', 'stars'), default='windows')
    parser.add_argument('--pin', type=int)
    parser.add_argument('--control', type=Path)
    parser.add_argument('--verify', type=Path)
    parser.add_argument('--geng')
    parser.add_argument('--seconds', type=float, default=20)
    parser.add_argument('--method', choices=('highs', 'highs-ipm'), default='highs')
    args = parser.parse_args()
    start = time.process_time()
    if args.geng:
        check_floors(args.geng)
        return
    if args.q22:
        check_pair_formula()
    order, degree = (16, 5) if args.control else (40, 9)
    codes = list(catalogue(order, degree))
    indices = (sorted(int(path.stem.split('-')[1]) for path in args.control.glob('eager-*.g6')
                      if path.stat().st_size) if args.control else [args.index])
    count = 0
    for index in indices:
        kernel = decode(codes[index])
        tight = degree * count_edges(kernel) == 2 * squares_floor(order, degree)
        assert args.control or tight and 19 <= index <= 34
        model = Transport(kernel, order, degree, forest=args.forest and tight, pinned_twos=args.pin)
        previous = len(model.rows)
        t_value = append_q22(model, kernel, degree) if args.q22 and tight else None
        q22_added = len(model.rows) - previous
        patterns = (0 if args.variant == 'base' else
                    append_windows(model, kernel, degree, per_mask=args.variant == 'stars'))
        if args.control:
            for line in (args.control / f'eager-{index}.g6').read_text().splitlines():
                graph = decode(line)
                if t_value is not None:
                    counts = exact_square_counts(graph)
                    assert counts[2 * degree - 2, 2 * degree - 1] == t_value == max(counts.values())
                model.replay_graph(graph, degree)
                count += 1
            continue
        build = time.process_time() - start
        first_unit = model.append_unit_bounds()
        identity = dict(code=codes[index], index=index, variant=args.variant, forest=args.forest,
                        pin=args.pin, q22=t_value, q22_added=q22_added, added=first_unit - previous, patterns=patterns,
                        rows=len(model.rows), columns=len(model.masks))
        if args.verify:
            record = json.loads(args.verify.read_text())
            assert all(value == record[key] for key, value in identity.items()) and record['status'] == 'cert'
            model.check(record['proof'])
            print('PASS exact Farkas', identity)
            return
        status, proof = model.solve_bounded(first_unit, args.method, args.seconds)
        print(json.dumps(dict(**identity, status=status, proof=proof, build_cpu=round(build, 3),
                              cpu=round(time.process_time() - start, 3)), separators=(',', ':')))
    if args.control:
        assert count == 13
        print(f'PASS {count} exact rational C16 projections {args.variant} forest={args.forest} '
              f'cpu={time.process_time()-start:.3f}')


if __name__ == '__main__':
    main()
