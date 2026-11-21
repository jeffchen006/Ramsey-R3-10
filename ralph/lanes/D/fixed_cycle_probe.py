#!/usr/bin/env python3
"""Matched C16 positive-control replay and pinned R(3) CPU comparison."""

import argparse
from collections import Counter
from contextlib import redirect_stdout
from io import StringIO
from itertools import combinations
from pathlib import Path
import time

from pysat.solvers import Cadical195

from factor_sat import Formula, bits, decode
from pinned_side import enumerate_profile, pinned_graph


def profile_of(line):
    return Counter(dict(tuple(map(int, entry.split(':'))) for entry in line.split()))


def minimum_cycles(adjacency, degree):
    return min(sum((adjacency[other] & adjacency[endpoint]).bit_count() - 1
                   for other in bits(adjacency[coord]) if endpoint != other)
               for coord in range(1, degree + 1) for endpoint in bits(adjacency[coord]))


def control(catalogue, base, directory, variant):
    kernels = [decode(graph) for graph in catalogue.read_text().splitlines()]
    all_profiles = 0
    total = 0
    for index, kernel in enumerate(kernels):
        previous = (base / f'k{index}.g6').read_text().splitlines()
        edge_minimum = sum(row.bit_count() for row in kernel) // 2
        expected = {line for line in previous if minimum_cycles(decode(line), 5) >= edge_minimum}
        seen = StringIO()
        for profile in (base / f'k{index}.profiles').read_text().splitlines():
            all_profiles += 1
            with redirect_stdout(StringIO()):
                enumerate_profile(5, kernel, 0, profile_of(profile), False, 'all', seen, fixed_min_cycles=variant)
        found = seen.getvalue().splitlines()
        assert len(set(found)) == len(found) and set(found) == expected, index
        assert all(minimum_cycles(decode(line), 5) >= edge_minimum for line in found)
        (directory / f'k{index}.g6').write_text(seen.getvalue())
        total += len(found)
        print(f'kernel={index} fixed_minimum={edge_minimum} baseline={len(previous)} expected=actual={len(found)}')
    print(f'PASS labelled graphs kernels={len(kernels)} profiles={all_profiles} graphs={total}')


def probe(degree, catalogue, index, side, profiles, line, variant):
    kernel = decode(catalogue.read_text().splitlines()[index])
    profile = profile_of(profiles.read_text().splitlines()[line - 1])
    start = time.process_time()
    with Cadical195() as solver:
        formula = Formula(solver)
        pinned_graph(formula, degree, kernel, side, profile, False, False, False,
                     fixed_min_cycles=variant if variant != 'base' else False)
        before = time.process_time()
        feasible = solver.solve()
        end = time.process_time()
        print(f'kernel={index} side={side} line={line} variant={variant} feasible={int(feasible)} '
              f'build_cpu={before-start:.6f} solve_cpu={end-before:.6f} '
              f'vars={formula.variables} clauses={formula.clauses} {solver.accum_stats()}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    calibration = commands.add_parser('control')
    calibration.add_argument('catalogue', type=Path)
    calibration.add_argument('base', type=Path)
    calibration.add_argument('directory', type=Path)
    calibration.add_argument('--variant', choices=('direct', 'deficit'), required=True)
    sample = commands.add_parser('probe')
    sample.add_argument('degree', type=int)
    sample.add_argument('catalogue', type=Path)
    sample.add_argument('index', type=int)
    sample.add_argument('side', type=int)
    sample.add_argument('profiles', type=Path)
    sample.add_argument('line', type=int)
    sample.add_argument('--variant', choices=('base', 'direct', 'deficit'), required=True)
    args = vars(parser.parse_args())
    command = args.pop('command')
    (control if command == 'control' else probe)(**args)


if __name__ == '__main__':
    main()
