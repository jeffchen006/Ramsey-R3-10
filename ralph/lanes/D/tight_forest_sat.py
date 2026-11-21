#!/usr/bin/env python3
"""Exact maximum-root SAT with optional forest constraints and a count pin."""

import argparse
from itertools import combinations
from pathlib import Path
import time

from pysat.solvers import Cadical195

from compact_tight import SharedFormula, build_shared
from factor_sat import Formula
from forest_root import blocked_arcs
from kernel_projection import bits, decode, encode
from mask_sat import independent_witness
from max_root import catalogue, count_edges, squares_floor
from max_root_sat import build, excess_square_edges
from q22_root import exact_square_counts


def either(formula, literals):
    literals = tuple(literals)
    if formula.true in literals:
        return formula.true
    literals = tuple(lit for lit in literals if lit != -formula.true)
    if len(literals) < 2:
        return literals[0] if literals else -formula.true
    out = formula.var()
    for lit in literals:
        formula.add(-lit, out)
    formula.add(-out, *literals)
    return out


def atleast_indicator(formula, literals, bound):
    out = formula.var()
    formula.atleast(literals, bound, unless=(-out,))
    formula.atmost(literals, bound - 1, unless=(out,))
    return out


def add_anchor_forests(formula, matrix, degree):
    width = 2 * (degree - 1)
    for anchor in range(width):
        root = width + (anchor >= degree - 1)
        fixed_side = tuple(coord for coord in range(width + 2)
                           if coord != anchor and matrix[root][coord] == formula.true)
        predecessors = {coord: [] for coord in fixed_side}
        earlier = {(first, second): formula.var() for first, second in combinations(fixed_side, 2)}
        for first, second, third in combinations(fixed_side, 3):
            formula.add(-earlier[first, second], -earlier[second, third], earlier[first, third])
            formula.add(earlier[first, second], earlier[second, third], -earlier[first, third])
        for (first, second), comparison in earlier.items():
            copies = [formula.both(matrix[anchor][other], formula.both(matrix[first][other], matrix[second][other]))
                      for other in range(len(matrix)) if other != root]
            formula.atmost(copies, 1)
            edge = either(formula, copies)
            predecessors[second].append(formula.both(edge, comparison))
            predecessors[first].append(formula.both(edge, -comparison))
        for terms in predecessors.values():
            formula.atmost(terms, 1)


def add_blocked_arcs(formula, matrix, kernel, degree):
    for left, right in blocked_arcs(kernel):
        for first, second in combinations(range(2 * degree, len(matrix)), 2):
            for first_mask, second_mask in ((left, right), (right, left)):
                formula.add(-matrix[first][second], *(-matrix[first][coord] for coord in bits(first_mask)),
                            *(-matrix[second][coord] for coord in bits(second_mask)))


def add_pin(formula, matrix, degree, count, signed, tight, kernel):
    width = degree - 1
    outer = range(2 * degree, len(matrix))
    both_twos = []
    for vertex in outer:
        left = [matrix[vertex][coord] for coord in range(width)]
        right = [matrix[vertex][coord] for coord in range(width, 2 * width)]
        parts = []
        for row in (left, right):
            below_three = -atleast_indicator(formula, row, 3)
            parts.append(below_three if tight else formula.both(atleast_indicator(formula, row, 2), below_three))
        both_twos.append(formula.both(*parts))
    formula.exactly(both_twos, count)
    if not signed or not tight:
        return
    terms = []
    for first, second in combinations(outer, 2):
        shared = [formula.both(matrix[first][other], matrix[second][other]) for other in outer
                  if other not in (first, second)]
        terms.append(atleast_indicator(formula, shared, 2))
        terms.extend([atleast_indicator(formula, shared, 3)] * 2)
    if (len(matrix), degree) == (16, 5):
        formula.atmost(terms, 0)
        return
    assert (len(matrix), degree) == (40, 9)
    for first, second in combinations(range(2 * width), 2):
        if first // width == second // width and (kernel[first] & kernel[second]).bit_count() == 1:
            for other in outer:
                terms.extend([formula.both(matrix[first][other], matrix[second][other])] * 2)
    formula.exactly(terms, 4 * count - 8)


def cyclic_kernel(adj):
    def search(vertex, parent, available, visited):
        visited.add(vertex)
        for neighbor in bits(adj[vertex] & available):
            if neighbor == parent:
                continue
            if neighbor in visited:
                return [neighbor, vertex], neighbor
            result = search(neighbor, vertex, available, visited)
            if result:
                cycle, end = result
                if end < 0:
                    return result
                if vertex == end:
                    return cycle, -1
                return cycle + [vertex], end
        return None

    for first, row in enumerate(adj):
        for second in bits(row & ~((1 << (first + 1)) - 1)):
            available = (row ^ (1 << second)) | (adj[second] ^ (1 << first))
            visited = set()
            for vertex in bits(available):
                if vertex in visited:
                    continue
                result = search(vertex, -1, available, visited)
                if result:
                    cycle, end = result
                    assert end == -1 and len(cycle) >= 4
                    edges = [(first, second)] + list(zip(cycle, cycle[1:] + cycle[:1]))
                    edges += [(first if row >> vertex & 1 else second, vertex) for vertex in cycle]
                    return tuple(sorted({tuple(sorted(edge)) for edge in edges}))
    return ()


def run(kernel, order, degree, variant, pin, output, base='eager', bare=False, conflicts=None, compact=False, no22=False):
    start = time.process_time()
    maximum = count_edges(kernel)
    tight = degree * maximum == 2 * squares_floor(order, degree)
    with Cadical195() as solver:
        formula = SharedFormula(solver) if compact or no22 else Formula(solver)
        matrix = (build_shared(formula, kernel, order, degree, base, no22) if compact or no22 else
                  build(formula, kernel, order, degree, base))
        if variant != 'plain':
            add_anchor_forests(formula, matrix, degree)
            add_blocked_arcs(formula, matrix, kernel, degree)
        if pin is not None:
            add_pin(formula, matrix, degree, pin, variant == 'signed', tight, kernel)
        print(f'built cpu={time.process_time()-start:.4f} vars={formula.variables} clauses={formula.clauses}', flush=True)
        counters = dict(candidates=0, alpha=0, square=0, forest=0, emitted=0)
        while True:
            if conflicts is None:
                status = solver.solve()
            else:
                solver.conf_budget(conflicts)
                status = solver.solve_limited()
            print(f'trace cpu={time.process_time()-start:.4f} result={status} {counters} {solver.accum_stats()}', flush=True)
            if status is False:
                print(f'exhausted cpu={time.process_time()-start:.4f} {counters}', flush=True)
                return
            if status is None:
                return
            counters['candidates'] += 1
            positive = set(solver.get_model())
            adj = [sum((edge in positive) << vertex for vertex, edge in enumerate(row)) for row in matrix]
            if no22:
                assert not any(exact_square_counts(adj).values())
            if variant != 'plain' and (cycle := cyclic_kernel(adj)):
                assert all(adj[first] >> second & 1 for first, second in cycle)
                formula.add(*(-matrix[first][second] for first, second in cycle))
                counters['forest'] += 1
                continue
            if squares := excess_square_edges(adj, maximum):
                assert base != 'eager'
                formula.add(*(-matrix[first][second] for first, second in sorted(squares)))
                counters['square'] += 1
                continue
            if not bare:
                complement = [((1 << order) - 1) & ~(row | (1 << vertex)) for vertex, row in enumerate(adj)]
                if witness := independent_witness(complement, degree + 1):
                    formula.add(*(matrix[first][second] for first, second in combinations(bits(witness), 2)))
                    counters['alpha'] += 1
                    continue
            print(encode(adj), file=output, flush=True)
            counters['emitted'] += 1
            if bare:
                return
            formula.add(*(-matrix[first][second] for first, second in combinations(range(order), 2)
                          if adj[first] >> second & 1))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('order', type=int)
    parser.add_argument('degree', type=int)
    parser.add_argument('index', type=int)
    parser.add_argument('variant', choices=('plain', 'forest', 'signed'))
    parser.add_argument('output', type=Path)
    parser.add_argument('--pin', type=int)
    parser.add_argument('--base', choices=('baseline', 'fixed', 'eager'), default='eager')
    parser.add_argument('--bare', action='store_true')
    parser.add_argument('--conflicts', type=int)
    parser.add_argument('--compact', action='store_true')
    parser.add_argument('--no22', action='store_true')
    args = parser.parse_args()
    assert args.variant != 'signed' or args.pin is not None
    code = list(catalogue(args.order, args.degree))[args.index]
    kernel = decode(code)
    if (args.order, args.degree) == (40, 9):
        assert 19 <= args.index <= 34 and count_edges(kernel) == 12
        assert args.pin is None or 6 <= args.pin <= 14
        assert args.variant == 'plain' or 2 * (args.degree - 1) == len(kernel) and args.index not in (19, 20, 22)
        assert not args.no22 or args.index in (32, 33, 34)
    print(f'index={args.index} kernel={code!r} variant={args.variant} pin={args.pin} base={args.base} '
          f'compact={args.compact} no22={args.no22}', flush=True)
    with args.output.open('w') as output:
        run(kernel, args.order, args.degree, args.variant, args.pin, output, args.base, args.bare, args.conflicts,
            args.compact, args.no22)


if __name__ == '__main__':
    main()
