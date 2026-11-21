#!/usr/bin/env python3
"""Run the singleton-codegree cut on matched control and target inputs."""

import argparse
from collections import Counter
import json
from pathlib import Path
import re

from pysat.solvers import Cadical195

from factor_sat import Formula, bits, build_side, decode
from pair_match import encode_matching, matches
from opposite_shadow import projected_kernel
from small_shadow_blocks import tests


def solve_profile(solver, occupants, profile):
    if any(count > len(occupants.get(mask, [])) for mask, count in profile.items()):
        return False
    pin = [lit if slot < profile[mask] else -lit
           for mask, levels in occupants.items() for slot, lit in enumerate(levels)]
    return solver.solve(assumptions=pin)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('library', type=Path)
    parser.add_argument('profile', type=Path, nargs='*')
    parser.add_argument('--control', type=Path)
    parser.add_argument('--shadow-blocks', action='store_true')
    args = parser.parse_args()
    catalogue = [decode(row) for row in args.catalogue.read_text().splitlines()]
    library = json.loads(args.library.read_text())
    if args.control:
        profiles = [args.control / f'k{index}.profiles' for index in range(len(catalogue))]
        degree, order = 5, 16
    else:
        profiles = args.profile
        degree, order = 9, 40
    print('kernel\tside\tprofiles\tbaseline\tsurviving\tlabelled_completion_count'
          + ('\tpair_surviving\ttransversal_surviving' if args.shadow_blocks else ''), flush=True)
    for path in profiles:
        match = re.fullmatch(r'k(\d+)-([01])-local\.profiles', path.name)
        index, side = (int(path.stem[1:]), 0) if args.control else tuple(map(int, match.groups()))
        kernel = catalogue[index]
        minimum = sum(row.bit_count() for row in kernel) // 2
        projected = projected_kernel(kernel, side)
        counts = [0, 0]
        base, surviving = [], []
        with Cadical195() as original, Cadical195() as strengthened:
            original_formula = Formula(original)
            strengthened_formula = Formula(strengthened)
            occupants, _, _ = build_side(original_formula, kernel, order, degree, minimum, 4, side, library, True)
            new_occupants, _, _ = build_side(strengthened_formula, kernel, order, degree, minimum, 4, side,
                                              library, True)
            encode_matching(strengthened_formula, kernel, degree, side, new_occupants)
            lines = path.read_text().splitlines()
            for row, line in enumerate(lines, 1):
                profile = Counter(dict(tuple(map(int, entry.split(':'))) for entry in line.split()))
                if solve_profile(original, occupants, profile):
                    base.append(row)
                    if args.shadow_blocks:
                        for test, passed in enumerate(tests(projected, profile)):
                            counts[test] += passed
                    accepted = solve_profile(strengthened, new_occupants, profile)
                    assert accepted == matches(kernel, degree, side, profile)
                    if accepted:
                        surviving.append(profile)
        known = 0
        if args.control:
            for row in (args.control / f'k{index}.g6').read_text().splitlines():
                graph = decode(row)
                width_mask = (1 << degree) - 1
                profile = Counter((row >> 1) & width_mask for row in graph[2 * degree:])
                assert profile in surviving
                if args.shadow_blocks:
                    assert all(tests(projected, profile))
                assert all(sum((graph[left] & graph[right]).bit_count() == 1
                               for right in bits(graph[0]) if right != left) <= 1 for left in bits(graph[0]))
                known += 1
        print(index, side, len(lines), len(base), len(surviving), known, *(counts if args.shadow_blocks else ()),
              sep='\t', flush=True)


if __name__ == '__main__':
    main()
