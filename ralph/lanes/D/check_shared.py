#!/usr/bin/env python3
"""Compare projected supports on identical baseline profiles, without regenerating them."""

from collections import Counter
import json
from pathlib import Path
import re
import sys

from pysat.solvers import Cadical195

from factor_sat import Formula, build_side, decode


def main():
    catalogue = Path(sys.argv[1]).read_text().splitlines()
    library = json.loads(Path(sys.argv[2]).read_text())
    print('kernel\tside\tprofiles\tbase\tsingletons\twidth3', flush=True)
    for path in map(Path, sys.argv[3:]):
        index, side = map(int, re.fullmatch(r'k(\d+)-([01])-local\.profiles', path.name).groups())
        kernel = decode(catalogue[index])
        minimum = sum(row.bit_count() for row in kernel) // 2
        profiles = [Counter(dict(tuple(map(int, entry.split(':'))) for entry in line.split()))
                    for line in path.read_text().splitlines()]
        survivors = [set() for _ in (0, 2, 3)]
        for shared, accepted in zip((0, 2, 3), survivors):
            with Cadical195() as solver:
                formula = Formula(solver)
                occupants, _, _ = build_side(formula, kernel, 40, 9, minimum, 4, side, library, True, shared)
                for pos, profile in enumerate(profiles):
                    if any(count > len(occupants.get(mask, [])) for mask, count in profile.items()):
                        continue
                    pin = [lit if slot < profile[mask] else -lit
                           for mask, levels in occupants.items() for slot, lit in enumerate(levels)]
                    if solver.solve(assumptions=pin):
                        accepted.add(pos)
        assert survivors[2] <= survivors[1] <= survivors[0]
        print(index, side, len(profiles), *(len(group) for group in survivors), sep='\t', flush=True)
        for name, group in zip(('singletons', 'width3'), survivors[1:]):
            for pos in sorted(survivors[0] - group):
                print(index, side, name, pos + 1, file=sys.stderr)


if __name__ == '__main__':
    main()
