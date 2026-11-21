#!/usr/bin/env python3
"""Get transferable partial-support conflicts from a non-specialized rooted CNF."""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import time

from pysat.solvers import Cadical195

from factor_sat import Formula, decode, graph_matrix
from pinned_side import pinned_graph


def build(solver, kernel, order, degree):
    formula = Formula(solver)
    matrix, outer = graph_matrix(formula, kernel, order, degree)
    for neighbors in matrix:
        formula.exactly(neighbors, degree)
    for first, second, third in combinations(range(order), 3):
        row = (matrix[first][second], matrix[first][third], matrix[second][third])
        if -formula.true not in row:
            formula.add(*(-edge for edge in row))
    for first, second in combinations(range(order), 2):
        if matrix[first][second] == formula.true:
            continue
        common = [formula.both(matrix[first][item], matrix[second][item]) for item in range(order)
                  if matrix[first][item] != -formula.true and matrix[second][item] != -formula.true]
        formula.atmost(common, 3)
    return matrix, outer


def solve(solver, matrix, outer, side, degree, masks):
    variables = {matrix[vertex][coord + side * (degree - 1)]: (local, 1 << coord)
                 for local, vertex in enumerate(outer) for coord in range(degree - 1)}
    assumptions = [edge if masks[local] & bit else -edge for edge, (local, bit) in variables.items()]
    if solver.solve(assumptions=assumptions):
        return None
    core = solver.get_core() or []
    assert set(core) <= set(assumptions)
    assert not solver.solve(assumptions=core)
    requirements = [[0, 0] for _ in outer]
    for literal in core:
        local, bit = variables[abs(literal)]
        requirements[local][literal < 0] |= bit
    return sorted(row for row in requirements if row != [0, 0])


def covers(masks, requirements):
    """Injectively assign actual support occurrences to the prescribed partial patterns."""
    choices = [[i for i, value in enumerate(masks) if value & need == need and not value & forbid]
               for need, forbid in requirements]
    owner = {}

    def augment(item, seen):
        for index in choices[item]:
            if index in seen:
                continue
            seen.add(index)
            if index not in owner or augment(owner[index], seen):
                owner[index] = item
                return True
        return False

    return all(augment(item, set()) for item in sorted(range(len(choices)), key=lambda i: len(choices[i])))


def parse(line):
    return Counter(dict(tuple(map(int, entry.split(':'))) for entry in line.split()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('order', type=int)
    parser.add_argument('degree', type=int)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('index', type=int)
    parser.add_argument('side', type=int, choices=(0, 1))
    parser.add_argument('profiles', type=Path)
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--line', type=int, default=0)
    parser.add_argument('--compare-pinned', action='store_true')
    args = parser.parse_args()
    kernel = decode(args.catalogue.read_text().splitlines()[args.index])
    profiles = [parse(line) for line in args.profiles.read_text().splitlines()]
    start = time.process_time()
    with Cadical195() as solver:
        matrix, outer = build(solver, kernel, args.order, args.degree)
        outcomes = 0
        for pos, profile in enumerate(profiles, 1):
            if args.line and args.line != pos:
                continue
            masks = sorted(profile.elements())
            assert len(masks) == len(outer)
            requirements = solve(solver, matrix, outer, args.side, args.degree, masks)
            if args.compare_pinned:
                with Cadical195() as control:
                    pinned_graph(Formula(control), args.degree, kernel, args.side, profile, False, False, False)
                    assert control.solve() == (requirements is None)
            matches = None
            if requirements is not None:
                assert covers(masks, requirements)
                matches = sum(covers(sorted(candidate.elements()), requirements) for candidate in profiles)
            print(json.dumps(dict(index=args.index, side=args.side, line=pos, requirements=requirements,
                                  profiles=len(profiles), matches=matches, cpu=time.process_time() - start)), flush=True)
            outcomes += 1
            if args.limit == outcomes:
                break


if __name__ == '__main__':
    main()
