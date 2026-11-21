#!/usr/bin/env python3
"""Check every local score on C16/C20 and replay the complete C16 corpus."""

import argparse
from collections import Counter
from contextlib import redirect_stdout
from io import StringIO
from itertools import combinations
from pathlib import Path

from pysat.solvers import Cadical195

from check_tight_forest import forest
from compact_tight import SharedFormula
from forest_score import circulant, square_score
from kernel_projection import bits, decode
from max_root import catalogue, count_edges, squares_floor
from score_sat import run, score_terms


def direct_score(graph, first, second):
    remaining = (graph[first] ^ (1 << second)) | (graph[second] ^ (1 << first))
    count = 0
    while remaining:
        cell = remaining & -remaining
        while True:
            closure = cell
            for vertex in bits(cell):
                closure |= graph[vertex] & remaining
            if closure == cell:
                break
            cell = closure
        count += cell.bit_count() in (2, 3)
        remaining ^= cell
    return count


def local(graph):
    hist = Counter()
    codegrees = [(graph[first] & graph[second]).bit_count()
                 for first, second in combinations(range(len(graph)), 2) if not graph[first] >> second & 1]
    assert all(1 <= value <= 3 for value in codegrees)
    with Cadical195() as solver:
        formula = SharedFormula(solver)
        matrix = [[-formula.true for _ in graph] for _ in graph]
        pinned = []
        for first, second in combinations(range(len(graph)), 2):
            matrix[first][second] = matrix[second][first] = lit = formula.var()
            pinned.append(lit if graph[first] >> second & 1 else -lit)
        expected = {}
        selectors = []
        bound = max(row.bit_count() for row in graph) - 1
        for (first, second), terms in score_terms(formula, matrix, no_singletons=min(codegrees) >= 2).items():
            if not graph[first] >> second & 1:
                continue
            expected[first, second] = score = direct_score(graph, first, second)
            thresholds = formula.thresholds(terms, bound + 1)
            selectors.extend((threshold, cap < score) for cap, threshold in enumerate(thresholds))
            hist[score] += 1
        if min(codegrees) >= 2:
            assert sum(expected.values()) == square_score(graph)[-1]
        assert solver.solve(assumptions=pinned)
        model = set(solver.get_model())
        for threshold, wanted in selectors:
            assert (threshold in model) == wanted
            assert not solver.solve(assumptions=pinned + [-threshold if wanted else threshold])
    return hist, len(selectors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('controls', type=Path)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    controls = [decode(text) for path in sorted(args.controls.glob('eager-*.g6'))
                for text in path.read_text().splitlines()]
    assert len(controls) == 13
    for graph in controls + [circulant(20, (-6, -5, -2, 2, 5, 6))]:
        print(f'order={len(graph)} forest={forest(graph)[0]} local={local(graph)}', flush=True)

    counts = Counter()
    stats = Counter()
    for index, code in enumerate(catalogue(16, 5)):
        kernel = decode(code)
        if count_edges(kernel) * 5 != 2 * squares_floor(16, 5):
            continue
        texts = (args.controls / f'eager-{index}.g6').read_text().splitlines()
        clean = {text: max(direct_score(graph, first, second) for first, row in enumerate(graph)
                           for second in bits(row) if second > first)
                 for text in texts if forest(graph := decode(text))[0]}
        for cap in (None, 0, 1, 2, 3, 4):
            prefix = args.directory / f'{index:02}-{cap}'
            with prefix.with_suffix('.log').open('w') as log, redirect_stdout(log):
                output = StringIO()
                run(kernel, 16, 5, output, cap)
            prefix.with_suffix('.g6').write_text(output.getvalue())
            got = output.getvalue().splitlines()
            expect = {text for text, score in clean.items() if cap is None or score <= cap}
            assert len(got) == len(set(got)) and set(got) == expect, (index, cap, got, expect)
            counts[cap] += len(got)
            stats[cap] += 1
    assert counts[None] == 1 and counts[0] < counts[4] == 1
    print(f'PASS exact forest sets on all tight C16 keys: solves={dict(stats)} kept={dict(counts)}')


if __name__ == '__main__':
    main()
