#!/usr/bin/env python3
"""Opposite-side incidence relaxation when the rooted kernel is a perfect matching."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path
import time

from pysat.solvers import Cadical195

from factor_sat import Formula, bits, decode


def perfect_matching(kernel, side):
    width = len(kernel) // 2
    shift = (1 - side) * width
    pairing = [tuple(bits(row >> shift)) for row in kernel[side * width:(side + 1) * width]]
    assert all(len(match) == 1 for match in pairing)
    return tuple(match[0] for match in pairing)


def build(formula, width, masks, unique_triple):
    right = [[-formula.true if mask >> coord & 1 else formula.var() for coord in range(width)] for mask in masks]
    for row in right:
        formula.atleast(row, 1)
        formula.atmost(row, 3)
    for coord in range(width):
        formula.exactly([row[coord] for row in right], width - 1)
        for other in range(width):
            if coord != other:
                formula.atmost([row[other] for mask, row in zip(masks, right) if mask >> coord & 1], 3)
    for first, second in combinations(range(width), 2):
        formula.atmost([formula.both(row[first], row[second]) for row in right], 2)
    if unique_triple:
        for first, second, third in combinations(range(width), 3):
            formula.atmost([formula.both(formula.both(row[first], row[second]), row[third]) for row in right], 1)
    for first, second in combinations(range(len(masks)), 2):
        cross = [right[first][coord] for coord in bits(masks[second])] + \
                [right[second][coord] for coord in bits(masks[first])]
        if masks[first] & masks[second]:
            formula.add(*cross)
        else:
            for coord in range(width):
                formula.add(-right[first][coord], -right[second][coord], *cross)
    return right


def solve(degree, masks, known_right=()):
    with Cadical195() as solver:
        formula = Formula(solver)
        right = build(formula, degree - 1, masks, len(masks) + 2 * degree < 6 * degree - 12)
        pins = [literal if mask >> coord & 1 else -literal for row, mask in zip(right, known_right)
                for coord, literal in enumerate(row)]
        start = time.process_time()
        feasible = solver.solve(assumptions=pins)
        return feasible, formula.variables, formula.clauses, time.process_time() - start


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('degree', type=int)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('index', type=int)
    parser.add_argument('side', type=int, choices=(0, 1))
    parser.add_argument('input', type=Path)
    parser.add_argument('--control-graphs', type=Path)
    parser.add_argument('--limit', type=int, default=0)
    args = parser.parse_args()
    start = time.process_time()
    kernel = decode(args.catalogue.read_text().splitlines()[args.index])
    pairing = perfect_matching(kernel, args.side)
    if args.control_graphs:
        assert args.side == 0
        for case in args.control_graphs.read_text().splitlines():
            graph = decode(case)
            outer = list(range(2 * args.degree, len(graph)))
            opposite = list(range(args.degree + 1, 2 * args.degree))
            left = [sum(bool(graph[vertex] >> (coord + 1) & 1) << coord for coord in range(args.degree - 1))
                    for vertex in outer]
            right = [sum(bool(graph[vertex] >> opposite[target] & 1) << coord for coord, target in enumerate(pairing))
                     for vertex in outer]
            assert all(graph[coord + 1] >> opposite[target] & 1 for coord, target in enumerate(pairing))
            assert solve(args.degree, left, right)[0]
        print(f'PASS pinned labeled completions={len(args.control_graphs.read_text().splitlines())}', flush=True)
    states = Counter()
    for number, row in enumerate(args.input.read_text().splitlines(), 1):
        counts = Counter(dict(tuple(map(int, entry.split(':'))) for entry in row.split()))
        masks = sorted(counts.elements())
        feasible, variables, clauses, cpu = solve(args.degree, masks)
        states[feasible] += 1
        print(f'row={number} feasible={int(feasible)} variables={variables} clauses={clauses} solver_cpu={cpu:.6f}',
              flush=True)
        if number == args.limit:
            break
    print(f'END feasible={states[True]} rejected={states[False]} process_cpu={time.process_time()-start:.6f}')


if __name__ == '__main__':
    main()
