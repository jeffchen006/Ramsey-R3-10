#!/usr/bin/env python3
"""Deterministic necessary independent-set cuts for fixed MTF gluing."""

import argparse
from itertools import combinations
from pathlib import Path

from root_glue import encode, graph, independent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--max-columns', type=int, default=3)
    args = parser.parse_args()
    assert 2 <= args.max_columns <= 6
    for index, line in enumerate(args.catalogue.read_text().splitlines(), 1):
        residual = graph.parse_graph6(line)
        formula, incident = encode(residual, 6, 9, 6, None, False)
        for columns in range(2, args.max_columns + 1):
            size = 10 - columns
            for exterior in independent(residual, (1 << len(residual)) - 1, size, size):
                for selected in combinations(incident, columns):
                    formula.add(attachment[vertex] for attachment in selected for vertex in exterior)
        formula.write(args.output / f'{index:04d}.cnf')
        print(index, formula.last, len(formula.clauses), flush=True)


if __name__ == '__main__':
    main()
