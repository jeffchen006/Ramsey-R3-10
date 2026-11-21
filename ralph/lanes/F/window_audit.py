#!/usr/bin/env python3
"""Recount the anchor's bad sets and bind four-window logs to their exact cover."""

import argparse
from itertools import combinations
from pathlib import Path
import re

from orbit_extend import image, independent, independent_sets, parse_graph6, perm_for


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('seed', type=Path)
    parser.add_argument('logs', nargs='+', type=Path)
    args = parser.parse_args()
    seed = parse_graph6(args.seed.read_text().strip())
    cycles = [3] * 10 + [1] * 10
    permutation = perm_for(cycles)
    assert len(seed) == 40 and all(mask.bit_count() == 9 and independent(mask, seed) and
                                   image(mask, permutation) == seed[permutation[index]]
                                   for index, mask in enumerate(seed))
    bad = list(independent_sets(seed, (1 << 40) - 1, 10))
    assert len(bad) == 44
    blocks = [7 << base for base in range(0, 30, 3)] + [1 << base for base in range(30, 40)]
    levels = []
    for width in range(1, 5):
        masks = ((indices, sum(blocks[index] for index in indices))
                 for indices in combinations(range(20), width))
        covers = {indices for indices, mask in masks if all(mask & witness for witness in bad)}
        print(width, len(covers))
        levels.append(covers)
    assert not any(levels[:3]) and len(levels[3]) == 175
    observed = set()
    for path in sorted(args.logs):
        text = path.read_text()
        assert text.splitlines()[-1].startswith("END {'model': 0, 'cap': 0,")
        queries = [tuple(map(int, indices.split(', '))) for indices in
                   re.findall(r'cycles=\((.*?)\) size=\d+ frozen=0 goal=0 unsat', text)]
        assert len(queries) == len(set(queries)) and observed.isdisjoint(queries)
        observed.update(queries)
        print(path, len(queries))
    assert observed == levels[3]
    print('PASS: exact cover and all returned UNSAT (not proof checked)')


if __name__ == '__main__':
    main()
