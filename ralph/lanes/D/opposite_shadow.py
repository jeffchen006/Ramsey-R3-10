#!/usr/bin/env python3
"""Pinned one-side relaxation using independent sets wholly inside the kernel."""

import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import time

from pysat.solvers import Cadical195

from factor_sat import Formula, bits, decode


def support(vertex, endpoints):
    return sum((vertex >> endpoint & 1) << index for index, endpoint in enumerate(endpoints))


def projected_kernel(kernel, side):
    width = len(kernel) // 2
    own = range(side * width, (side + 1) * width)
    opposite = range((1 - side) * width, (2 - side) * width)
    return tuple(support(kernel[vertex], opposite) for vertex in own)


@lru_cache(maxsize=4096)
def independent_shadows(forbidden, blocked_left, target):
    width = len(forbidden)
    universe = (1 << width) - 1
    eligible_left = universe ^ blocked_left
    found = set()
    left = eligible_left
    while True:
        needed = target - left.bit_count()
        if needed <= 0:
            return (0,)
        eligible_right = universe
        for coord in bits(left):
            eligible_right &= ~forbidden[coord]
        for subset in combinations(bits(eligible_right), needed):
            found.add(sum(1 << coord for coord in subset))
        if not left:
            break
        left = (left - 1) & eligible_left
    minimal = []
    for state in sorted(found, key=lambda item: (item.bit_count(), item)):
        if not any(prior & state == prior for prior in minimal):
            minimal.append(state)
    return tuple(minimal)


def build(formula, forbidden, left, width_three):
    width = len(forbidden)
    right = [[formula.var() if all(not (forbidden[coord] >> other & 1) for coord in bits(mask or 0))
              else -formula.true for other in range(width)] for mask in left]
    pinned = [index for index, mask in enumerate(left) if mask is not None]
    for row in right:
        formula.atleast(row, 1)
        formula.atmost(row, 3)
    for coord in range(width):
        formula.exactly([row[coord] for row in right], width - sum(mask >> coord & 1 for mask in forbidden))
        for other in range(width):
            formula.atmost([right[index][coord] for index in pinned if left[index] >> other & 1], 3)
    for first, second in combinations(range(width), 2):
        pair = (1 << first) | (1 << second)
        formula.atmost([formula.both(row[first], row[second]) for row in right],
                       2 - sum(mask & pair == pair for mask in forbidden))
    if len(left) + 2 * (width + 1) < 6 * (width + 1) - 12:
        fixed_triples = [mask for mask in forbidden if mask.bit_count() == 2]
        if len(set(fixed_triples)) != len(fixed_triples):
            formula.add()
        for first, second, third in combinations(range(width), 3):
            formula.atmost([formula.both(formula.both(row[first], row[second]), row[third]) for row in right], 1)
    for index in pinned:
        for shadow in independent_shadows(forbidden, left[index], width + 1):
            formula.add(*(right[index][coord] for coord in bits(shadow)))
    for first, second in combinations(pinned, 2):
        for shadow in independent_shadows(forbidden, left[first] | left[second], width):
            hitters = [right[row][coord] for row in (first, second) for coord in bits(shadow)]
            if left[first] & left[second]:
                formula.add(*hitters)
            else:
                for coord in range(width):
                    if not (shadow >> coord & 1):
                        formula.add(-right[first][coord], -right[second][coord], *hitters)
    if width_three:
        for rows in combinations(pinned, 3):
            if all(left[first] & left[second] for first, second in combinations(rows, 2)):
                for shadow in independent_shadows(forbidden, left[rows[0]] | left[rows[1]] | left[rows[2]],
                                                  width - 1):
                    formula.add(*(right[row][coord] for row in rows for coord in bits(shadow)))
    return right


def solve(kernel, left, mode, known=()):
    with Cadical195() as solver:
        formula = Formula(solver)
        right = build(formula, kernel, left, mode == 3)
        assumptions = [literal if mask >> coord & 1 else -literal for row, mask in zip(right, known)
                       for coord, literal in enumerate(row)]
        return solver.solve(assumptions=assumptions), formula.variables, formula.clauses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('--control', type=Path)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--minimize', choices=(2, 3), type=int)
    args = parser.parse_args()
    catalog = [decode(row) for row in args.catalogue.read_text().splitlines()]
    start = time.process_time()
    if args.control:
        checked = 0
        for index, kernel in enumerate(catalog):
            forbidden = projected_kernel(kernel, 0)
            width = len(forbidden)
            for graph6 in (args.control / f'k{index}.g6').read_text().splitlines():
                graph = decode(graph6)
                outer = graph[2 * (width + 1):]
                left = [support(vertex, range(1, width + 1)) for vertex in outer]
                right = [support(vertex, range(width + 2, 2 * (width + 1))) for vertex in outer]
                assert solve(forbidden, left, 2, right)[0]
                assert solve(forbidden, left, 3, right)[0]
                assert solve(forbidden, [mask if index % 2 else None for index, mask in enumerate(left)], 3, right)[0]
                checked += 1
        print(f'PASS labelled controls={checked} for both widths cpu={time.process_time()-start:.5f}')
        return
    assert args.manifest
    if args.minimize:
        print('kernel\tside\tline\tmode\tslots\tmatched\tcpu\tcore', flush=True)
    else:
        print('kernel\tside\tline\tmode\tfeasible\tvars\tclauses\tcpu', flush=True)
    for index, row in enumerate(args.manifest.read_text().splitlines(), 1):
        kernel, side, line, name = row.split()
        kernel, side, line = map(int, (kernel, side, line))
        forbidden = projected_kernel(catalog[kernel], side)
        profiles = [Counter(dict(tuple(map(int, entry.split(':'))) for entry in value.split()))
                    for value in Path(name).read_text().splitlines()]
        pins = sorted(profiles[line - 1].elements())
        for mode in ((args.minimize,) if args.minimize else (2, 3)):
            before = time.process_time()
            state, variables, clauses = solve(forbidden, pins, mode)
            if args.minimize:
                if state:
                    print(kernel, side, line, mode, '-', '-', f'{time.process_time()-before:.5f}', '-',
                          sep='\t', flush=True)
                    continue
                for slot in range(len(pins)):
                    trial = pins[:]
                    trial[slot] = None
                    if not solve(forbidden, trial, mode)[0]:
                        pins = trial
                core = Counter(mask for mask in pins if mask is not None)
                assert not solve(forbidden, pins, mode)[0]
                matches = sum(core <= profile for profile in profiles)
                print(kernel, side, line, mode, sum(core.values()), matches, f'{time.process_time()-before:.5f}',
                      ' '.join(f'{mask}:{count}' for mask, count in sorted(core.items())), sep='\t', flush=True)
                continue
            print(kernel, side, line, mode, int(state), variables, clauses, f'{time.process_time()-before:.5f}',
                  sep='\t', flush=True)
        if index == args.limit:
            break


if __name__ == '__main__':
    main()
