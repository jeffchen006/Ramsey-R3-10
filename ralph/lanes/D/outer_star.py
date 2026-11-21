#!/usr/bin/env python3
"""An outer-neighborhood relaxation at one pinned attachment mask."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
import sys
import time

from pysat.solvers import Cadical195

from factor_sat import Formula
from max_root import MaxProjection, catalogue, count_edges, squares_floor
from kernel_projection import bits, decode, independent_masks


class Star:
    def __init__(self, kernel, order, degree):
        self.degree = degree
        width = len(kernel)
        self.interior = (1 << width) - 1
        left = (1 << (degree - 1)) - 1
        right = self.interior ^ left
        self.adj = [row | (1 << (width + (vertex >= degree - 1))) for vertex, row in enumerate(kernel)]
        self.adj += [left | (1 << (width + 1)), right | (1 << width)]
        self.floor = 2 if degree * count_edges(kernel) == 2 * squares_floor(order, degree) else 1
        self.masks = [mask for mask in MaxProjection(kernel, order, degree, depth=1, bounds='base').masks
                      if all((mask & side).bit_count() >= self.floor for side in (left, right))]
        self.independent = []
        for seed in independent_masks(self.adj, (1 << len(self.adj)) - 1):
            blocked = 0
            for coord in bits(seed):
                blocked |= self.adj[coord]
            self.independent.append((seed, blocked))

    def rows(self, mask, seeds):
        candidates = [other for other in self.masks if not other & mask]
        size = self.degree - mask.bit_count()
        yield candidates, size, size
        stars, pairs, triples = defaultdict(list), defaultdict(list), defaultdict(list)
        for other in candidates:
            for coord in bits(other):
                stars[coord].append(other)
            for coords in combinations(bits(other), 2):
                pairs[coords].append(other)
            for coords in combinations(bits(other), 3):
                triples[coords].append(other)
        for coord in bits(self.interior ^ mask):
            fixed = (self.adj[coord] & mask).bit_count()
            yield stars[coord], max(0, self.floor - fixed), 3 - fixed
        for (first, second), choices in pairs.items():
            yield choices, 0, 3 - (self.adj[first] & self.adj[second]).bit_count()
        for choices in triples.values():
            yield choices, 0, 1
        if seeds:
            best = {}
            for seed, blocked in self.independent:
                bound = self.degree - (seed | (mask & ~blocked)).bit_count()
                effective = seed & (self.interior ^ mask)
                if bound < best.get(effective, size):
                    best[effective] = bound
            for seed, bound in best.items():
                yield [other for other in candidates if not seed & other], 0, bound

    def generators(self):
        import pynauty

        width = self.interior.bit_length()
        bipartite = [row & self.interior for row in self.adj[:width]]
        graph = pynauty.Graph(width, adjacency_dict={coord: list(bits(row))
                                                     for coord, row in enumerate(bipartite)},
                              vertex_coloring=[set(range(width // 2)), set(range(width // 2, width))])
        generators = pynauty.autgrp(graph)[0]

        def image(mask, generator):
            return sum(1 << generator[coord] for coord in bits(mask))

        for generator in generators:
            assert sorted(generator) == list(range(width))
            assert all(coord // (width // 2) == generator[coord] // (width // 2) for coord in range(width))
            assert all(bipartite[generator[coord]] == image(row, generator)
                       for coord, row in enumerate(bipartite))
        return generators

    def orbits(self):
        generators = self.generators()

        remaining = set(self.masks)
        for representative in self.masks:
            if representative not in remaining:
                continue
            block = {representative}
            todo = [representative]
            for mask in todo:
                for generator in generators:
                    partner = sum(1 << generator[coord] for coord in bits(mask))
                    if partner not in block:
                        block.add(partner)
                        todo.append(partner)
            assert block <= remaining
            remaining -= block
            yield representative, sorted(block)
        assert not remaining

    def compile(self, formula, mask, seeds):
        rows = iter(self.rows(mask, seeds))
        candidates, low, high = next(rows)
        chosen = {other: formula.var() for other in candidates}
        assert low == high
        formula.exactly(list(chosen.values()), low)
        for masks, low, high in rows:
            lits = [chosen[other] for other in masks]
            formula.atleast(lits, low)
            formula.atmost(lits, high)
        return chosen

    def solve(self, mask, seeds, known=None):
        with Cadical195() as solver:
            formula = Formula(solver)
            chosen = self.compile(formula, mask, seeds)
            assumptions = [] if known is None else [lit if other in known else -lit for other, lit in chosen.items()]
            if not solver.solve(assumptions=assumptions):
                return None
            positives = set(solver.get_model())
            witness = [other for other, lit in chosen.items() if lit in positives]
            for masks, low, high in self.rows(mask, seeds):
                assert low <= sum(other in witness for other in masks) <= high
            assert known is None or set(witness) == set(known)
            return witness


def calibrate(directory, seeds):
    cases = 0
    for path in sorted(directory.glob('eager-*.g6')):
        index = int(path.stem.split('-')[-1])
        star = Star(decode(list(catalogue(16, 5))[index]), 16, 5)
        representative_of = {mask: representative for representative, block in star.orbits() for mask in block}
        assert set(representative_of) == set(star.masks)
        for line in path.read_text().splitlines():
            graph = decode(line)
            for row in graph[10:]:
                mask = row & star.interior
                neighbors = [graph[neighbor] & star.interior for neighbor in bits(row) if neighbor >= 10]
                assert len(set(neighbors)) == len(neighbors) and set(neighbors) <= set(star.masks)
                assert mask in star.masks and star.solve(mask, seeds, known=neighbors) is not None
                assert star.solve(representative_of[mask], seeds) is not None
                cases += 1
    assert cases == 78
    print(f'PASS {cases} known outside stars from exact C16 max-root control')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('order', type=int)
    parser.add_argument('degree', type=int)
    parser.add_argument('index', type=int)
    parser.add_argument('--seeds', action='store_true')
    parser.add_argument('--orbits', action='store_true')
    parser.add_argument('--fixpoint', action='store_true')
    parser.add_argument('--projection-log', type=Path)
    parser.add_argument('--sample-mod', type=int, default=1)
    parser.add_argument('--sample-rem', type=int, default=0)
    parser.add_argument('--control', type=Path)
    args = parser.parse_args()
    assert 0 <= args.sample_rem < args.sample_mod
    if args.control:
        calibrate(args.control, args.seeds)
        return
    code = list(catalogue(args.order, args.degree))[args.index]
    star = Star(decode(code), args.order, args.degree)
    assert not args.fixpoint or (args.orbits and args.sample_mod == 1)
    assert not args.projection_log or args.fixpoint
    blocks = list(star.orbits()) if args.orbits else [(mask, [mask]) for mask in star.masks]
    blocks = [(mask, block) for index, (mask, block) in enumerate(blocks)
              if index % args.sample_mod == args.sample_rem]
    start = time.process_time()
    witnesses = {}
    for iteration in range(1, len(blocks) + 2):
        summary = Counter()
        removed = set()
        survivors = []
        universe = set(star.masks)
        for mask, block in blocks:
            if mask not in witnesses or not set(witnesses[mask]) <= universe:
                neighbors = star.solve(mask, args.seeds)
                if neighbors is not None:
                    witnesses[mask] = neighbors
            else:
                neighbors = witnesses[mask]
            status = 'viable' if neighbors is not None else 'unsat'
            summary[status, mask.bit_count()] += len(block)
            if neighbors is None:
                removed.update(block)
            else:
                survivors.append((mask, block))
            print(json.dumps(dict(iteration=iteration, mask=mask, block=block, status=status, neighbors=neighbors),
                             separators=(',', ':')), flush=True)
        print(f'iteration={iteration} total={len(star.masks)} orbits={len(blocks)} checked={sorted(summary.items())} '
              f'cpu={time.process_time()-start:.3f}', file=sys.stderr, flush=True)
        if not args.fixpoint or not removed:
            break
        star.masks = [mask for mask in star.masks if mask not in removed]
        blocks = survivors
    if args.projection_log:
        model = MaxProjection(decode(code), args.order, args.degree)
        surviving = set(star.masks)
        deleted = tuple((col, 1) for col, mask in enumerate(model.masks) if mask not in surviving)
        model.rows.append((deleted, 0, 'outer-star-fixed-point'))
        status, proof = model.solve()
        with args.projection_log.open('w') as stream:
            print(json.dumps(dict(index=args.index, code=code, status=status, proof=proof,
                                  kept=sorted(surviving), deleted=len(deleted)), separators=(',', ':')), file=stream)
        print(f'projection={status} cpu={time.process_time()-start:.3f}', file=sys.stderr)


if __name__ == '__main__':
    main()
