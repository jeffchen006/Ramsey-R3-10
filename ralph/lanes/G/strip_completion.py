#!/usr/bin/env python3
"""Complete paired 27-vertex windows with all core edges fixed."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations, islice, product
from pathlib import Path
from time import process_time

from pysat.solvers import Cadical195

from check_root_cover import graph, vertices
from equality_template import Problem
from root_glue import Formula, independent


class Completion(Problem):
    def __init__(self, order, fixed):
        self.formula = Formula(1)
        self.formula.add((1,))
        self.order = order
        self.edge = {pair: (1 if fixed[pair] else -1) if pair in fixed else self.formula.new()
                     for pair in combinations(range(order), 2)}

    def incident(self, vertex, exclude=()):
        return [self.edgeof(vertex, other) for other in range(self.order)
                if vertex != other and other not in exclude]

    def and_all(self, literals):
        result = 1
        for literal in literals:
            result = self.and2(result, literal)
        return result

    def triangles(self):
        for left, middle, right in combinations(range(self.order), 3):
            self.add((-self.edge[left, middle], -self.edge[left, right], -self.edge[middle, right]))

    def maximal(self):
        for (left, right), edge in self.edge.items():
            if edge == 1:
                continue
            contacts = [(self.edgeof(left, other), self.edgeof(right, other))
                        for other in range(self.order) if other not in (left, right)]
            if (1, 1) not in contacts:
                self.add((edge, *(self.and2(first, second) for first, second in contacts)))

    def exact_degree(self, vertex, choices):
        degree_clause = self.incident(vertex)
        selectors = {choice: self.formula.new() for choice in choices}
        self.bound(selectors.values(), 1, 1)
        for choice, selector in selectors.items():
            start = len(self.formula.clauses)
            self.bound(degree_clause, choice, choice)
            for index in range(start, len(self.formula.clauses)):
                self.formula.clauses[index] += (-selector,)
        return selectors

    def independent_clause(self, witness):
        return tuple(self.edge[pair] for pair in combinations(sorted(witness), 2) if self.edge[pair] != -1)


def finish_pins(fixed, adj, active, exclusive, survived):
    for index, anchors in enumerate(active):
        wanted = Counter({(anchor,): 4 for anchor in anchors})
        wanted.update(combinations(anchors, 2))
        seen = Counter(tuple(anchor for anchor in anchors if adj[vertex] >> anchor & 1) for vertex in survived)
        assert seen and all(0 < count <= wanted[part] for part, count in seen.items())
        missing = sorted((wanted - seen).elements())
        for vertex, part in zip(exclusive[1-index], missing, strict=True):
            for anchor in anchors:
                fixed[anchor, vertex] = anchor in part

    present = [0] * 40
    for (left, right), value in fixed.items():
        if value:
            present[left] |= 1 << right
            present[right] |= 1 << left
    for left, right in combinations(range(40), 2):
        if present[left] & present[right] and (left, right) not in fixed:
            fixed[left, right] = False


def window(line, first_mask, second_mask, eager, optimized, cut_budget=False, overlays=False):
    adj = graph.parse_graph6(line)
    core = len(adj)
    shared = core - 24
    assert 1 <= shared <= 3
    assert not first_mask & second_mask and first_mask.bit_count() == second_mask.bit_count() == 4
    roots = (core, core+1)
    centers = (core+2, core+3)
    active = (tuple(vertices(first_mask)), tuple(vertices(second_mask)))
    stars, = [(left, right) for left, right in product(*active) if adj[left] >> right & 1]
    sides = tuple((*anchors, center) for anchors, center in zip(active, centers, strict=True))
    common = tuple(range(core+4, core+4+shared))
    first_exclusive = core+4+shared
    exclusive = (tuple(range(first_exclusive, first_exclusive+6-shared)),
                 tuple(range(first_exclusive+6-shared, 40)))
    removed = common + exclusive[0] + exclusive[1]
    survived = tuple(vertices(((1 << core) - 1) & ~(first_mask | second_mask)))
    exterior = survived + removed

    fixed = {(left, right): bool(adj[left] >> right & 1) for left, right in combinations(range(core), 2)}
    for side_idx, (root, center, side) in enumerate(zip(roots, centers, sides, strict=True)):
        for other in range(40):
            if root != other:
                fixed[tuple(sorted((root, other)))] = other in side or other in roots
            if center != other and other not in roots:
                fixed[tuple(sorted((center, other)))] = other in (*common, *exclusive[side_idx])
    for left, right in combinations(removed, 2):
        if left not in exclusive[0] or right not in exclusive[1]:
            fixed[left, right] = False
    if optimized:
        finish_pins(fixed, adj, active, exclusive, survived)
    problem = Completion(40, fixed)
    problem.triangles()
    problem.maximal()

    all_doubles = {vertex: [] for vertex in exterior}
    for side, center, star in zip(sides, centers, stars, strict=True):
        support = {vertex: {anchor: problem.edgeof(vertex, anchor) for anchor in side} for vertex in exterior}
        for incident in support.values():
            problem.bound(incident.values(), 1, 2)
        for anchor in side:
            singles = [problem.and_all(lit if other == anchor else -lit for other, lit in incident.items())
                       for incident in support.values()]
            problem.bound(singles, 4, 4)
        centered_doubles = []
        for left, right in combinations(side, 2):
            doubles = [problem.and2(incident[left], incident[right]) for incident in support.values()]
            for vertex, literal in zip(support, doubles, strict=True):
                all_doubles[vertex].append(literal)
            if right != center:
                problem.bound(doubles, 1, 1)
            elif left == star:
                problem.bound(doubles, 0, 0)
            else:
                problem.bound(doubles, 0, 1)
                centered_doubles.extend(doubles)
        problem.bound(centered_doubles, 2, 2)
        if not optimized:
            for vertex in exterior:
                problem.bound(problem.incident(vertex, (*roots, *side)), 6, 8)

    d7, d8, cut_terms = [], [], []
    for vertex in exterior:
        classes = problem.exact_degree(vertex, (7, 8, 9))
        d7.append(classes[7])
        d8.append(classes[8])
        if cut_budget and vertex in removed:
            copy = problem.formula.new()
            problem.add((-copy, classes[7]))
            problem.add((copy, -classes[7]))
            cut_terms.extend((copy, classes[7], classes[8]))
        if optimized:
            for is_double in all_doubles[vertex]:
                problem.add((-classes[7], -is_double))
    if optimized:
        choice = problem.formula.new()
        for unique, low, middle in ((choice, 6, 0), (-choice, 5, 2)):
            start = len(problem.formula.clauses)
            problem.bound(d7, low, low)
            problem.bound(d8, middle, middle)
            for index in range(start, len(problem.formula.clauses)):
                problem.formula.clauses[index] += (-unique,)
    else:
        problem.bound(d7, 5, 6)
        problem.bound(d8, 0, 2)
        problem.bound(problem.edge.values(), 168, 168)
    if cut_budget:
        target = sum(neighbors.bit_count() for neighbors in adj) // 2 - 49 - 9*shared
        cut_terms.extend(problem.edgeof(left, right) for left, right in product(*exclusive))
        problem.bound(cut_terms, target, target)
    if overlays:
        assert optimized
        from strip_overlay import overlay_terms
        selectors = []
        for assignment in overlay_terms(adj, sides, stars, centers, common, exclusive, survived):
            selector = problem.formula.new()
            selectors.append(selector)
            for vertex, anchor, value in assignment:
                edge = problem.edgeof(vertex, anchor)
                problem.add((-selector, edge if value else -edge))
        problem.add(selectors)
        problem.overlay_count = len(selectors)
    if eager:
        for count in (7, 6):
            for chosen in islice(independent(adj, (1 << core) - 1, count, count), eager):
                for side_idx, trio in enumerate(exclusive):
                    for selected in combinations(trio, 9-count):
                        problem.add(problem.independent_clause((*chosen, *selected, centers[1-side_idx])))
    return problem


def solve(problem, alpha, limit, batch=64):
    counter = Counter()
    cuts = []
    with Cadical195(bootstrap_with=problem.formula.clauses) as solver:
        while counter['conflicts'] < limit:
            solver.conf_budget(limit - counter['conflicts'])
            answer = solver.solve_limited()
            counter['conflicts'] = solver.accum_stats()['conflicts']
            if answer is None:
                return 'CAP', counter, cuts
            if not answer:
                return 'UNSAT', counter, cuts
            counter['models'] += 1
            adj = problem.adjacency(solver.get_model())
            assert graph.triangle_free(adj)
            witnesses = tuple(islice(independent(adj, (1 << len(adj)) - 1, alpha+1, alpha+1), batch))
            if not witnesses:
                assert graph.alpha(adj) <= alpha
                return graph.to_graph6(adj), counter, cuts
            for witness in witnesses:
                solver.add_clause(problem.independent_clause(witness))
                cuts.append(witness)
    return 'CAP', counter, cuts


def control(file):
    for line in file.read_text().splitlines():
        adj = graph.parse_graph6(line)
        order = len(adj)
        alpha = graph.alpha(adj)
        fixed = {(left, right): bool(adj[left] >> right & 1) for left, right in combinations(range(order), 2)
                 if left not in (0, 1) or right not in (2, 3, 4, 5, 6)}
        problem = Completion(order, fixed)
        problem.triangles()
        problem.maximal()
        for vertex, neighbors in enumerate(adj):
            problem.exact_degree(vertex, (neighbors.bit_count(),))
        result, _, _ = solve(problem, alpha, 100000)
        assert result not in ('CAP', 'UNSAT'), result
        result, _, _ = solve(problem, alpha-1, 100000)
        assert result == 'UNSAT', result
        print('completion control n', order, 'alpha', alpha, 'positive; tighter alpha negative')


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--conflicts', type=int, default=20000)
    parser.add_argument('--eager', type=int, default=0)
    parser.add_argument('--optimized', action='store_true')
    parser.add_argument('--cut-budget', action='store_true')
    parser.add_argument('--rebuild', nargs=2, type=Path, metavar=('CUTS', 'CNF'))
    parser.add_argument('--cuts', type=Path)
    args = parser.parse_args()
    if args.control:
        return control(args.input)
    if args.cuts:
        args.cuts.mkdir(exist_ok=True, parents=True)
    start = process_time()
    for row in args.input.read_text().splitlines():
        rowid, first, second, line = row.split()
        key = '_'.join((rowid, first, second))
        problem = window(line, int(first), int(second), args.eager, args.optimized, args.cut_budget)
        if args.rebuild:
            for raw in args.rebuild[0].read_text().splitlines():
                witness = tuple(map(int, raw.split()))
                if len(witness) != 10 or len(set(witness)) != 10 or min(witness) < 0 or max(witness) >= 40:
                    raise ValueError('bad independent-set cut')
                problem.add(problem.independent_clause(witness))
            problem.formula.write(args.rebuild[1])
            return
        result, stats, cuts = solve(problem, 9, args.conflicts)
        if result == 'UNSAT' and args.cuts:
            (args.cuts / key).write_text(''.join(' '.join(map(str, chosen)) + '\n' for chosen in cuts))
        print(key, result, stats['conflicts'], stats['models'], len(cuts), f'{process_time()-start:.5f}', flush=True)


if __name__ == '__main__':
    main()
