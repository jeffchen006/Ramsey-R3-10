#!/usr/bin/env python3
"""An eager global cap on short edge-kernel components (codegree at most 3)."""

import argparse
from contextlib import redirect_stdout
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import time

from pysat.solvers import Cadical195

from compact_tight import SharedFormula, build_shared
from forest_score import components
from kernel_projection import bits, decode, encode
from mask_sat import independent_witness
from max_root import catalogue, count_edges, squares_floor
from tight_forest_sat import add_anchor_forests, add_blocked_arcs, add_pin, cyclic_kernel


def star_score_terms(formula, matrix, first_root, second_root, no_singletons):
    """Score edges at either fixed root without building unrelated terms."""
    true = formula.true
    order = len(matrix)

    @lru_cache(maxsize=None)
    def common(first, second):
        if matrix[first][second] == true:
            return ()
        return tuple((vertex, term) for vertex in range(order)
                     if (term := formula.both(matrix[first][vertex], matrix[second][vertex])) != -true)

    @lru_cache(maxsize=None)
    def counts(first, second):
        return formula.thresholds([term for _, term in common(first, second)], 3)

    @lru_cache(maxsize=None)
    def clean(first, second, vertex):
        shared = common(first, second)
        pivot = next((term for other, term in shared if other == vertex), -true)
        if pivot == -true:
            return pivot
        dirty = []
        for other, term in shared:
            if other != vertex:
                product = formula.both(term, counts(*sorted((vertex, other)))[2])
                if product == true:
                    return -true
                if product != -true:
                    dirty.append(product)
        return clean_term(formula, pivot, dirty)

    for first, second in combinations(range(order), 2):
        if first not in (first_root, second_root) and second not in (first_root, second_root):
            continue
        if matrix[first][second] != true:
            continue
        row = []
        for endpoint, vertex in ((first, second), (second, first)):
            for other in range(order):
                if other in (endpoint, vertex):
                    continue
                pair = sorted((endpoint, other))
                term = clean(*pair, vertex)
                if term == -true:
                    continue
                if endpoint > vertex:
                    term = formula.both(term, counts(*pair)[2])
                elif not no_singletons:
                    term = formula.both(term, counts(*pair)[1])
                if term != -true:
                    row.append(term)
        yield (first, second), row


def clean_term(formula, pivot, dirty):
    if not dirty:
        return pivot
    clean = formula.var()
    formula.add(-pivot, *dirty, clean)
    formula.add(-clean, pivot)
    for lit in dirty:
        formula.add(-clean, -lit)
    return clean


def score_terms(formula, matrix, no_singletons=False):
    order = len(matrix)
    true = formula.true
    common = {}
    twice = {}
    high = [[-true] * order for _ in matrix]
    for first, second in combinations(range(order), 2):
        if matrix[first][second] == true:
            continue
        shared = [(vertex, term) for vertex in range(order)
                  if (term := formula.both(matrix[first][vertex], matrix[second][vertex])) != -true]
        if not shared:
            continue
        common[first, second] = shared
        _, twice[first, second], thrice = formula.thresholds([term for _, term in shared], 3)
        high[first][second] = high[second][first] = thrice

    rows = {(first, second): [] for first, second in combinations(range(order), 2)
            if matrix[first][second] != -true}
    for (first, second), shared in common.items():
        for vertex, pivot in shared:
            dirty = [lit for other, term in shared if other != vertex
                     and (lit := formula.both(term, high[vertex][other])) != -true]
            if true in dirty:
                continue
            clean = clean_term(formula, pivot, dirty)
            for endpoint in (first, second):
                edge = tuple(sorted((vertex, endpoint)))
                if endpoint < vertex:
                    term = clean if no_singletons else formula.both(clean, twice[first, second])
                else:
                    term = formula.both(clean, high[first][second])
                if term != -true:
                    rows[edge].append(term)
    return rows


def add_cap(formula, matrix, cap):
    for (first, second), terms in score_terms(formula, matrix, no_singletons=True).items():
        formula.atmost(terms, cap, unless=(-matrix[first][second],))


def direct_scores(graph):
    return {(first, second): sum(part.bit_count() in (2, 3) for part in components(
                graph, (row ^ (1 << second)) | (graph[second] ^ (1 << first))))
            for first, row in enumerate(graph) for second in bits(row) if second > first}


def run(kernel, order, degree, output, cap=None, pin=None, chunk=None):
    start = time.process_time()
    assert degree * count_edges(kernel) == 2 * squares_floor(order, degree)
    with Cadical195() as solver:
        formula = SharedFormula(solver)
        matrix = build_shared(formula, kernel, order, degree, 'eager', False)
        add_anchor_forests(formula, matrix, degree)
        add_blocked_arcs(formula, matrix, kernel, degree)
        if pin is not None:
            add_pin(formula, matrix, degree, pin, True, True, kernel)
        base = formula.variables, formula.clauses
        if cap is not None:
            add_cap(formula, matrix, cap)
        print(f'built cpu={time.process_time()-start:.3f} vars={formula.variables} clauses={formula.clauses} '
              f'added_vars={formula.variables-base[0]} added_clauses={formula.clauses-base[1]}', flush=True)

        candidates = cycles = alpha = emitted = 0
        while True:
            if chunk is None:
                status = solver.solve()
            else:
                solver.conf_budget(chunk)
                status = solver.solve_limited()
            print(f'trace cpu={time.process_time()-start:.3f} result={status} candidates={candidates} '
                  f'cycles={cycles} alpha={alpha} emitted={emitted} clauses={formula.clauses} '
                  f'{solver.accum_stats()}', flush=True)
            if status is None:
                continue
            if status is False:
                return emitted

            candidates += 1
            positive = set(solver.get_model())
            graph = [sum((lit in positive) << coord for coord, lit in enumerate(row)) for row in matrix]
            if cap is not None:
                assert max(direct_scores(graph).values()) <= cap
            if cycle := cyclic_kernel(graph):
                formula.add(*(-matrix[first][second] for first, second in cycle))
                cycles += 1
                continue
            complement = [((1 << order) - 1) & ~(row | (1 << vertex)) for vertex, row in enumerate(graph)]
            if witness := independent_witness(complement, degree + 1):
                formula.add(*(matrix[first][second] for first, second in combinations(bits(witness), 2)))
                alpha += 1
                continue
            print(encode(graph), file=output, flush=True)
            emitted += 1
            formula.add(*(-matrix[first][second] for first, second in combinations(range(order), 2)
                          if graph[first] >> second & 1))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('key', type=int)
    parser.add_argument('output', type=Path)
    parser.add_argument('--log', type=Path, required=True)
    parser.add_argument('--cap', type=int, choices=(2, 3))
    parser.add_argument('--pin', type=int, choices=range(6, 15))
    parser.add_argument('--chunk', type=int)
    args = parser.parse_args()
    by_score = {2: (24, 25, 26, 28, 29, 32), 3: (21, 23, 27)}
    assert args.key in (by_score[args.cap] if args.cap is not None else by_score[2] + by_score[3])
    assert args.chunk is None or args.chunk > 0
    code = list(catalogue(40, 9))[args.key]
    kernel = decode(code)
    with args.output.open('w') as output, args.log.open('w') as log, redirect_stdout(log):
        print(f'key={args.key} kernel={code!r} pin={args.pin} cap={args.cap} chunk={args.chunk}', flush=True)
        run(kernel, 40, 9, output, args.cap, args.pin, args.chunk)


if __name__ == '__main__':
    main()
