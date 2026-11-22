#!/usr/bin/env python3
"""Test both orientations of the opposite-pivot caps on one pure-window lift."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations
from pathlib import Path
from time import process_time

from pysat.solvers import Cadical195

from check_root_cover import graph, vertices
from strip_completion import Completion, window


def contacts(problem, first, second, outside):
    return [problem.and2(problem.edgeof(first, vertex), problem.edgeof(second, vertex))
            for vertex in outside]


def impose(problem, first, second, outside, easier_cap, extra_allowance):
    problem.bound((*contacts(problem, first, second, outside), -extra_allowance), 0, easier_cap)


def pure_caps(problem, order, first, second, direction='both'):
    active = tuple(tuple(vertices(mask)) for mask in (first, second))
    exterior = (*vertices(((1 << order) - 1) & ~(first | second)), *range(order+4, 40))
    centers = order+2, order+3
    for side, anchors in enumerate(active):
        if direction != 'both' and str(side) != direction:
            continue
        for anchor in anchors:
            if any(problem.edgeof(anchor, opposite) == 1 for opposite in active[1-side]):
                continue
            full = -problem.and_all(-literal for literal in contacts(problem, centers[side], anchor, exterior))
            impose(problem, centers[1-side], anchor, exterior, 4, full)


def witness_check(problem, model, order, first, second):
    positive = {literal for literal in model if literal > 0}
    adjacency = [set() for _ in range(40)]
    for (left, right), literal in problem.edge.items():
        if literal in positive or -literal not in positive and literal < 0:
            adjacency[left].add(right)
            adjacency[right].add(left)
    masks = ({index for index in range(order) if first >> index & 1},
             {index for index in range(order) if second >> index & 1})
    bad = 0
    for side, center in enumerate((order+2, order+3)):
        for anchor in masks[side]:
            if adjacency[anchor] & masks[1-side]:
                continue
            opposite = order+3-side
            degree = len(adjacency[anchor])
            assert degree in (8, 9) and opposite not in adjacency[anchor]
            bad += len(adjacency[anchor] & adjacency[opposite]) > degree-5
    return bad


def controls(path):
    visits = 0
    for line in path.read_text().splitlines():
        adj = graph.parse_graph6(line)
        degree = [neighbor.bit_count() for neighbor in adj]
        alpha = graph.alpha(adj)
        upper = {4: 5, 8: 22, 9: 27}[alpha]
        assert sum(degree) % 2 == 0
        for first, second in combinations(range(len(adj)), 2):
            if adj[first] >> second & 1:
                continue
            outside = tuple(vertex for vertex in range(len(adj)) if vertex not in (first, second))
            fixed = {(left, right): bool(adj[left] >> right & 1)
                     for left, right in combinations(range(len(adj)), 2)}
            base_cap = upper - len(adj) + 2 + degree[first] + degree[second]
            common = (adj[first] & adj[second]).bit_count()
            assert common <= base_cap
            for allow in (False, True):
                for cap in (base_cap+1, common+int(not allow), common-int(allow)):
                    problem = Completion(len(adj), fixed)
                    impose(problem, first, second, outside, cap, 1 if allow else -1)
                    with Cadical195(bootstrap_with=problem.formula.clauses) as solver:
                        assert solver.solve() == (common+int(not allow) <= cap)
                    visits += 1
        print('CONTROL', len(adj), 'alpha', alpha, 'passed', flush=True)
    for mask_left in range(16):
        for mask_right in range(16):
            for allow in (False, True):
                problem = Completion(6, {})
                allowance = problem.edgeof(0, 1)
                impose(problem, 0, 1, tuple(range(2, 6)), 2, allowance)
                pins = [allowance if allow else -allowance]
                for vertex in range(2, 6):
                    for index, mask in enumerate((mask_left, mask_right)):
                        literal = problem.edgeof(index, vertex)
                        pins.append(literal if mask >> (vertex-2) & 1 else -literal)
                with Cadical195(bootstrap_with=problem.formula.clauses) as solver:
                    assert solver.solve(assumptions=pins) == ((mask_left & mask_right).bit_count()+int(not allow) <= 2)
                visits += 1
    print('CONTROL exact literal tests', visits, flush=True)


def sample(path, conflicts):
    stats = Counter()
    for row in path.read_text().splitlines():
        row_id, first, second, encoded = row.split()
        first, second, order = int(first), int(second), ord(encoded[0])-63
        assert order in (25, 26)
        key = f'{row_id}_{first}_{second}'
        base = window(encoded, first, second, 0, True, cut_budget=True)
        for direction in ('base', 'both'):
            start = process_time()
            added = 0
            if direction != 'base':
                length = len(base.formula.clauses)
                pure_caps(base, order, first, second, direction)
                added = len(base.formula.clauses) - length
            with Cadical195(bootstrap_with=base.formula.clauses) as solver:
                solver.conf_budget(conflicts)
                answer = solver.solve_limited()
                label = {True: 'RELAXED_SAT', False: 'UNSAT', None: 'CAP'}[answer]
                count = solver.accum_stats()['conflicts']
                bad = witness_check(base, solver.get_model(), order, first, second) if answer else '-'
                if direction == 'both' and answer:
                    assert bad == 0
            stats[direction, label] += 1
            print(key, order, direction, label, count, added, bad, f'{process_time()-start:.5f}', flush=True)
            if direction == 'base' and answer is False:
                break
    print('TOTAL', dict(stats), flush=True)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('keys', type=Path, nargs='?')
    parser.add_argument('--controls', type=Path)
    parser.add_argument('--conflicts', type=int, default=150000)
    args = parser.parse_args()
    if args.controls:
        controls(args.controls)
    if args.keys:
        sample(args.keys, args.conflicts)
