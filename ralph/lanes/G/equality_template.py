#!/usr/bin/env python3
"""Exact equality-root signature cover and bounded lazy SAT pilot."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations, permutations
from math import comb
from pathlib import Path
from random import Random
from time import process_time

from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195

from check_root_cover import graph, vertices
from check_rows import saturated
from etables import e3
from freeze_round6 import ledger
from root_glue import Formula, independent


def treesize(anchors, signatures):
    components = list(range(anchors))
    tree = []
    for left, right in sorted(combinations(range(anchors), 2),
                              key=lambda pair: (pair not in signatures, pair)):
        if components[left] != components[right]:
            tree.append((left, right))
            old, new = components[right], components[left]
            components = [new if component == old else component for component in components]
    result = []
    queue = [0]
    for left in queue:
        for edge in tree:
            if left in edge:
                right = edge[1 - edge.index(left)]
                if right not in queue:
                    result.append((left, right))
                    queue.append(right)
    assert len(queue) == anchors
    return result


def template_counts():
    possible = tuple(combinations(range(6), 2))
    permutations_of_pairs = []
    for perm in permutations(range(6)):
        permutations_of_pairs.append(tuple(1 << possible.index(tuple(sorted((perm[left], perm[right]))))
                                           for left, right in possible))
    attrition = Counter()
    canonical = {}
    for indices in combinations(range(15), 9):
        pairs = tuple(possible[index] for index in indices)
        degrees = tuple(5 + sum(anchor in pair for pair in pairs) for anchor in range(6))
        if min(degrees) < 6 or max(degrees) > 9:
            continue
        if any(degrees[left] + degrees[right] < 13 for left, right in pairs):
            continue
        rows = [counts for (edges, *counts), _ in ledger_cache.items()
                if edges == 168 and counts[0] and degrees.count(6) == counts[0] - 1
                and all(degrees.count(deg) + (deg == 6) <= counts[deg - 6] for deg in range(6, 10))]
        attrition['raw'] += 1
        if not rows:
            continue
        attrition['pinned'] += 1
        mask = sum(1 << index for index in indices)
        if any(sum(action[index] for index in indices) < mask for action in permutations_of_pairs):
            continue
        canonical[mask] = pairs, tuple(map(tuple, rows))
    return canonical, attrition


class Problem:
    def __init__(self, anchors, private, signatures):
        self.anchors = anchors
        self.private = private
        self.signatures = signatures
        self.alpha = private + anchors - 1
        self.first = 1 + anchors
        self.cells = [tuple(range(self.first + i * private, self.first + (i + 1) * private))
                      for i in range(anchors)]
        supports = [0] * self.first + [1 << i for i in range(anchors) for _ in range(private)]
        supports.extend((1 << left) | (1 << right) for left, right in signatures)
        self.supports = supports
        self.order = len(supports)
        self.formula = Formula(1)
        self.formula.add((1,))
        self.edge = {}
        pairs = set(signatures)
        fixed = {tuple(sorted((left, right))) for first, second in treesize(anchors, pairs)
                 if tuple(sorted((first, second))) in pairs
                 for left, right in zip(self.cells[first], self.cells[second])}
        for first, second in combinations(range(self.order), 2):
            if first == 0:
                value = 1 if second < self.first else -1
            elif first < self.first:
                value = 1 if supports[second] & (1 << (first - 1)) else -1
            elif supports[first] & supports[second]:
                value = -1
            elif (first, second) in fixed:
                value = 1
            else:
                value = self.formula.new()
            self.edge[first, second] = value

    def edgeof(self, first, second):
        return self.edge[min(first, second), max(first, second)]

    def add(self, literals):
        literals = tuple(literals)
        if 1 not in literals:
            self.formula.add(literal for literal in literals if literal != -1)

    def bound(self, literals, lower, upper):
        literals = tuple(literals)
        positive = literals.count(1)
        literals = [value for value in literals if abs(value) != 1]
        lower -= positive
        upper -= positive
        if upper < 0 or lower > len(literals) or upper < lower:
            self.formula.add(())
            return
        if lower > 0:
            encoding = CardEnc.atmost(lits=[-lit for lit in literals], bound=len(literals) - lower,
                                      top_id=self.formula.last, encoding=EncType.kmtotalizer)
            self.formula.last = max(self.formula.last, encoding.nv)
            self.formula.clauses.extend(map(tuple, encoding.clauses))
        if upper < len(literals):
            encoding = CardEnc.atmost(lits=literals, bound=upper, top_id=self.formula.last,
                                      encoding=EncType.kmtotalizer)
            self.formula.last = max(self.formula.last, encoding.nv)
            self.formula.clauses.extend(map(tuple, encoding.clauses))

    def and2(self, left, right):
        if left == -1 or right == -1:
            return -1
        if left == 1 or right == 1:
            return right if left == 1 else left
        value = self.formula.new()
        self.add((-value, left))
        self.add((-value, right))
        self.add((value, -left, -right))
        return value

    def structure(self, maximal):
        for points in combinations(range(self.order), 3):
            self.add(-self.edge[pair] for pair in combinations(points, 2))
        if maximal:
            for (first, second), edge in self.edge.items():
                if edge == 1 or self.supports[first] & self.supports[second] or second < self.first:
                    continue
                partial = [(self.edgeof(first, other), self.edgeof(second, other))
                           for other in range(self.order) if other not in (first, second)]
                if (1, 1) not in partial:
                    self.add([edge, *(self.and2(left, right) for left, right in partial)])

    def local_edges(self, count=0, prove_total=False):
        if prove_total:
            self.bound(self.edge.values(), count, count)
        for length in range(2, self.anchors + 1):
            for subset in combinations(range(self.anchors), length):
                support = sum(1 << anchor for anchor in subset)
                part = [vertex for vertex in range(self.first, self.order) if not self.supports[vertex] & ~support]
                required = sum(self.private - 1 + (pair in self.signatures) for pair in combinations(subset, 2))
                target_k = self.private + length
                lower = e3(target_k, len(part)) if 3 <= target_k <= 9 else 0
                if lower is None:
                    self.add(())
                    continue
                self.bound((self.edgeof(left, right) for left, right in combinations(part, 2)),
                           max(required, lower), comb(len(part), 2))

    def local_alpha(self, limit):
        latter = sum(self.cells, ())
        assert latter == tuple(range(self.first, self.first + self.anchors * self.private))
        known = [0] * self.order
        for (left, right), edge in self.edge.items():
            if edge == 1:
                known[left] |= 1 << right
                known[right] |= 1 << left
        clauses = set()
        for length in range(2, min(limit, self.anchors) + 1):
            for subset in combinations(range(self.anchors), length):
                mask = sum(1 << index for index in subset)
                allowed = sum(1 << index for index in range(self.first, self.order) if not self.supports[index] & ~mask)
                size = self.private + length
                for witness in independent(known, allowed, size, size):
                    clause = tuple(self.edge[pair] for pair in combinations(witness, 2) if self.edge[pair] != -1)
                    assert 1 not in clause
                    if clause not in clauses:
                        self.add(clause)
                        clauses.add(clause)
        return len(clauses)

    def companion(self, root, pin_leaf_neighbour=None):
        """Second equality decomposition at a fixed adjacent root of the same degree."""
        neighbours = [vertex for vertex in range(self.order) if vertex != root and self.edgeof(root, vertex) == 1]
        exterior = [vertex for vertex in range(self.order) if vertex != root and self.edgeof(root, vertex) == -1]
        assert len(neighbours) == self.anchors and len(exterior) + len(neighbours) + 1 == self.order
        private = defaultdict(list)
        pairs = defaultdict(list)
        for vertex in exterior:
            support = [self.edgeof(vertex, anchor) for anchor in neighbours]
            self.bound(support, 1, 2)
            for index, edge in enumerate(support):
                indicator = self.formula.new()
                self.add((-indicator, edge))
                self.add((indicator, -edge, *(other for offset, other in enumerate(support) if offset != index)))
                for offset, other in enumerate(support):
                    if offset != index:
                        self.add((-indicator, -other))
                private[neighbours[index]].append(indicator)
            for first, second in combinations(range(len(neighbours)), 2):
                pairs[neighbours[first], neighbours[second]].append(self.and2(support[first], support[second]))
        for cell in private.values():
            self.bound(cell, self.private, self.private)
        for incidences in pairs.values():
            self.bound(incidences, 0, 1)
        if pin_leaf_neighbour is not None:
            incident = [self.edgeof(pin_leaf_neighbour, vertex) for vertex in range(self.order) if vertex != pin_leaf_neighbour]
            self.bound(incident, self.alpha, self.alpha)

    def neighborhood_floors(self, by_vertex, vertices_in_window, total, alpha, residual=False):
        for vertex in vertices_in_window:
            indicator = by_vertex[vertex]
            deficits = [self.and2(self.edgeof(vertex, other), selection)
                        for other in vertices_in_window if other != vertex
                        for degree, selection in by_vertex[other].items()
                        for _ in range(alpha - degree + (self.supports[other].bit_count() if residual else 0))]
            for degree, selection in indicator.items():
                actual = degree - (self.supports[vertex].bit_count() if residual else 0)
                floor = e3(alpha, len(vertices_in_window) - 1 - actual) if residual else self.floors[degree]
                if floor is None:
                    self.add((-selection,))
                    continue
                low = alpha * actual - total + floor
                if low <= 0:
                    continue
                start = len(self.formula.clauses)
                self.bound(deficits, low, len(deficits))
                for index in range(start, len(self.formula.clauses)):
                    self.formula.clauses[index] += (-selection,)

    def distribution(self, counts, floors, residue_minimum=6, strengthen=False):
        by_class = defaultdict(list)
        by_vertex = []
        for vertex, support in enumerate(self.supports):
            incident = [self.edgeof(vertex, other) for other in range(self.order) if other != vertex]
            forced, possible = incident.count(1), len(incident) - incident.count(-1)
            minimum = max(forced, residue_minimum + support.bit_count()) if support else forced
            domain = [degree for degree, count in counts.items() if count and minimum <= degree <= possible]
            indicator = {degree: self.formula.new() for degree in domain}
            self.bound(indicator.values(), 1, 1)
            for degree, selection in indicator.items():
                by_class[degree].append(selection)
                start = len(self.formula.clauses)
                self.bound(incident, degree, degree)
                for index in range(start, len(self.formula.clauses)):
                    self.formula.clauses[index] += (-selection,)
            by_vertex.append(indicator)
        for degree, count in counts.items():
            self.bound(by_class[degree], count, count)

        total = sum(degree * count for degree, count in counts.items()) // 2
        self.floors = floors
        self.neighborhood_floors(by_vertex, range(self.order), total, self.alpha)
        if strengthen:
            exterior = range(self.first, self.order)
            boundary = self.anchors + sum(supp.bit_count() for supp in self.supports)
            self.neighborhood_floors(by_vertex, exterior, total - boundary, self.alpha - 1, residual=True)

    def adjacency(self, model):
        selected = set(model)
        result = [0] * self.order
        for (left, right), edge in self.edge.items():
            if edge in selected:
                result[left] |= 1 << right
                result[right] |= 1 << left
        return result

    def solve(self, seed, step, budget, alpha_limit, stream=None, omit_root=False):
        rng = Random(seed)
        order = list(range(self.order))
        counter = Counter()
        start = process_time()
        with Cadical195(bootstrap_with=self.formula.clauses) as solver:
            while counter['conflicts'] < budget:
                solver.conf_budget(min(step, budget - counter['conflicts']))
                result = solver.solve_limited()
                counter['conflicts'] = solver.accum_stats()['conflicts']
                if result is None:
                    print(f'progress {counter} cpu={process_time()-start:.3f}', flush=True)
                    continue
                if not result:
                    return 'UNSAT', dict(counter)
                counter['models'] += 1
                adj = self.adjacency(solver.get_model())
                assert graph.triangle_free(adj)
                if alpha_limit == 0:
                    return 'RELAXED_SAT', dict(counter)
                rng.shuffle(order)
                shuffled = [sum(1 << i for i, right in enumerate(order) if adj[left] >> right & 1) for left in order]
                allowed = ((1 << self.order) - 1) ^ ((1 << order.index(0)) if omit_root else 0)
                witnesses = independent(shuffled, allowed, self.alpha + 1, self.alpha + 1)
                bad = 0
                for witness in witnesses:
                    actual = tuple(sorted(order[i] for i in witness))
                    clause = tuple(self.edge[pair] for pair in combinations(actual, 2) if self.edge[pair] != -1)
                    assert 1 not in clause
                    if stream is not None:
                        print(*actual, file=stream)
                    solver.add_clause(clause)
                    counter['alpha_cuts'] += 1
                    bad += 1
                    if bad == alpha_limit:
                        break
                if not bad:
                    checked = adj if not omit_root else [neighbours >> 1 for neighbours in adj[1:]]
                    assert graph.alpha(checked) <= self.alpha
                    self.solution = adj
                    return 'FULL_SAT', dict(counter)
                if counter['models'] % 100 == 0:
                    print(f'progress {counter} cpu={process_time()-start:.3f}', flush=True)
        return 'CONFLICT_CAP', dict(counter)


def calibrated(adj, alpha):
    order = len(adj)
    accepted = 0
    assert graph.triangle_free(adj) and graph.alpha(adj) == alpha
    for root, nn in enumerate(adj):
        anchors = tuple(vertices(nn))
        private = alpha + 1 - len(anchors)
        if private < 1:
            continue
        external = tuple(vertices(((1 << order) - 1) & ~(nn | 1 << root)))
        counter = Counter(tuple(index for index, anchor in enumerate(anchors) if adj[vertex] >> anchor & 1)
                          for vertex in external)
        if sum(len(key) * multiplicity for key, multiplicity in counter.items()) != 2 * len(external) - len(anchors) * private:
            continue
        assert all(counter[(index,)] == private for index in range(len(anchors)))
        assert all(1 <= len(key) <= 2 and (len(key) != 2 or value == 1) for key, value in counter.items())
        signatures = tuple(sorted(key for key in counter if len(key) == 2))
        problem = Problem(len(anchors), private, signatures)
        problem.structure(True)
        count = sum(map(int.bit_count, adj)) // 2
        problem.local_edges(count, prove_total=True)
        problem.local_alpha(3)
        if order == 13:
            problem.distribution({4: 13}, {4: 10}, residue_minimum=2, strengthen=True)
            problem.companion(1)
        mapping = [root, *anchors, *([-1] * len(external))]
        groups = {support: [v for v in external if tuple(index for index, anchor in enumerate(anchors)
                                                        if adj[v] >> anchor & 1) == support] for support in counter}
        for first, second in treesize(len(anchors), signatures):
            if tuple(sorted((first, second))) not in signatures:
                continue
            first_cell, second_cell = problem.cells[first], problem.cells[second]
            size = private
            extensions = []
            for first_order in permutations(groups[(first,)]) if mapping[first_cell[0]] == -1 else [tuple(mapping[v] for v in first_cell)]:
                for second_order in permutations(groups[(second,)]) if mapping[second_cell[0]] == -1 else [tuple(mapping[v] for v in second_cell)]:
                    if all(adj[left] >> right & 1 for left, right in zip(first_order[:size], second_order)):
                        extensions.append((first_order, second_order))
            assert extensions
            first_order, second_order = extensions[0]
            for vertex, value in zip(first_cell + second_cell, first_order + second_order):
                mapping[vertex] = value
        for index, cell in enumerate(problem.cells):
            if mapping[cell[0]] == -1:
                for vertex, value in zip(cell, groups[(index,)]):
                    mapping[vertex] = value
        for index, signature in enumerate(signatures, problem.first + len(anchors) * private):
            mapping[index] = groups[signature][0]
        assert len(set(mapping)) == order and min(mapping) == 0
        assignment = []
        for (left, right), edge in problem.edge.items():
            value = edge if adj[mapping[left]] >> mapping[right] & 1 else -edge
            assert value != -1
            assignment.append(value)
        with Cadical195(bootstrap_with=problem.formula.clauses) as solver:
            assert solver.solve(assumptions=sorted(set(assignment)))
        accepted += 1
    return accepted


ledger_cache = ledger()[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', type=Path)
    parser.add_argument('--case', nargs=4, type=int)
    parser.add_argument('--mask', type=int)
    parser.add_argument('--conflicts', type=int, default=10000)
    parser.add_argument('--batch', type=int, default=96)
    parser.add_argument('--seed', type=int, default=611)
    parser.add_argument('--cnf', type=Path)
    parser.add_argument('--witnesses', type=Path)
    parser.add_argument('--graph', type=Path)
    parser.add_argument('--local-alpha', type=int, default=3)
    parser.add_argument('--strengthen', action='store_true')
    parser.add_argument('--no-mtf', action='store_true')
    args = parser.parse_args()
    if args.control is not None:
        for name, adj, alpha in [('C13', graph.parse_graph6(args.control.read_text().strip()), 4),
                                 ('C35', [sum(1 << ((v + step) % 35) for step in (1, -1, 7, -7, 11, -11, 16, -16))
                                          for v in range(35)], 8)]:
            print(name, 'checked equality roots:', calibrated(saturated(adj), alpha))
        positive = Problem(4, 1, ((0, 1), (0, 3), (1, 2), (2, 3)))
        positive.structure(True)
        positive.local_edges(26, prove_total=True)
        positive.local_alpha(3)
        result, counts = positive.solve(611, 300, 3000, 96)
        assert result == 'FULL_SAT', (result, counts)
        negative = Problem(4, 1, positive.signatures)
        negative.structure(True)
        negative.local_edges(25, prove_total=True)
        negative.local_alpha(3)
        result, counts = negative.solve(611, 300, 3000, 96)
        assert result == 'UNSAT', (result, counts)
        print('unconstrained C13 template SAT at 26, UNSAT at 25 edges')
        return
    templates, attrition = template_counts()
    print('templates', len(templates), dict(attrition), flush=True)
    if args.mask is None:
        for mask, (signatures, cases) in sorted(templates.items()):
            print(mask, signatures, len(cases), cases)
        return
    signatures, cases = templates[args.mask]
    assert tuple(args.case) in cases
    start = process_time()
    problem = Problem(6, 4, signatures)
    assert (problem.order, problem.alpha) == (40, 9)
    problem.structure(not args.no_mtf)
    problem.local_edges(168)
    problem.distribution(dict(zip(range(6, 10), args.case)), {6: 120, 7: 108, 8: 97, 9: 88}, strengthen=args.strengthen)
    if args.strengthen and args.case[0] == 2:
        degrees = [sum(1 for edge in signatures if index in edge) + 5 for index in range(6)]
        leaf = degrees.index(6)
        leaf_other = next(index for edge in signatures if leaf in edge for index in edge if index != leaf)
        assert degrees[leaf_other] in (8, 9)
        force = None
        if args.case[2] <= 2:
            assert degrees == [9, 9, 9, 8, 7, 6] and degrees[leaf_other] == 9
            force = problem.first + problem.anchors * problem.private + signatures.index(tuple(sorted((leaf, leaf_other))))
        problem.companion(1 + leaf, force)
    local_alpha = problem.local_alpha(args.local_alpha)
    print('built', problem.formula.last, len(problem.formula.clauses), f'local_alpha={local_alpha}',
          f'cpu={process_time()-start:.3f}', flush=True)
    if args.cnf is not None:
        problem.formula.write(args.cnf)
    if args.witnesses is not None:
        with args.witnesses.open('w', buffering=1) as stream:
            result, details = problem.solve(args.seed, 1000, args.conflicts, args.batch, stream)
    else:
        result, details = problem.solve(args.seed, 1000, args.conflicts, args.batch)
    print(result, details, f'cpu={process_time()-start:.3f}', flush=True)
    if result == 'FULL_SAT':
        bits = [problem.solution[second] >> first & 1 for second in range(problem.order) for first in range(second)]
        bits.extend([0] * (-len(bits) % 6))
        row = chr(63 + problem.order) + ''.join(chr(63 + sum(bit << (5 - offset) for offset, bit in enumerate(bits[index:index + 6])))
                                                       for index in range(0, len(bits), 6))
        if args.graph is not None:
            args.graph.write_text(row + '\n')
        print(row)


if __name__ == '__main__':
    main()
