#!/usr/bin/env python3
"""Fixed-side CNF with exact independent-set separation and witness replay."""

import argparse
from collections import Counter
from itertools import combinations
import json

from involution_cores import RAMSEY, bits, independent_extensions


def from_graph6(line):
    order = ord(line[0]) - 63
    assert len(line) == 1 + (order * (order - 1) // 2 + 5) // 6
    adj = [0] * order
    pairs = ((right, left) for right in range(order) for left in range(right))
    for index, (right, left) in enumerate(pairs):
        if ((ord(line[1 + index // 6]) - 63) >> (5 - index % 6)) & 1:
            adj[left] |= 1 << right
            adj[right] |= 1 << left
    return adj


def to_graph6(adj):
    digits = [len(adj) + 63]
    pairs = ((right, left) for right in range(len(adj)) for left in range(right))
    for index, (right, left) in enumerate(pairs):
        if not index % 6:
            digits.append(63)
        if (adj[left] >> right) & 1:
            digits[-1] += 1 << (5 - index % 6)
    return ''.join(map(chr, digits))


def witnesses(adj, domain, need):
    def walk(pending, picked, left):
        if not left:
            yield picked
            return
        while pending.bit_count() >= left:
            bit = pending & -pending
            pending ^= bit
            yield from walk(pending & ~adj[bit.bit_length() - 1], picked | bit, left - 1)

    return walk(domain, 0, need)


class Encoding:
    def __init__(self, profile, bound, core=None, use_degrees=True, use_lex=True):
        self.bound = bound
        self.moved = tuple(profile['adj'])
        self.fixed = sum(profile['counts'])
        self.fixed_mask = (1 << self.fixed) - 1
        self.order = self.fixed + len(self.moved)
        self.known = [0] * self.order
        self.variables = {}
        self.clauses = []
        self.next = 0
        self.residues = {}
        self.degree_rows = {}
        self.memberships = tuple(membership for membership, count in zip(profile['groups'], profile['counts'])
                                 for _ in range(count))
        parts = [tuple(index for index, membership in enumerate(self.memberships) if membership == value)
                 for value in profile['groups']]
        if core is not None:
            assert len(core) == profile['counts'][0] and profile['groups'][0] == 0
            self.known[:len(core)] = core
        for vertex, row in enumerate(self.moved):
            self.known[self.fixed + vertex] = row << self.fixed
        for vertex, membership in enumerate(self.memberships):
            for orbit in bits(membership):
                for moved in (self.fixed + 2 * orbit, self.fixed + 2 * orbit + 1):
                    self.known[vertex] |= 1 << moved
                    self.known[moved] |= 1 << vertex
        for left, right in combinations(range(self.fixed), 2):
            if core is not None and right < len(core):
                continue
            if not self.memberships[left] & self.memberships[right]:
                self.next += 1
                self.variables[left, right] = self.next
        for triple in combinations(range(self.order), 3):
            clause = []
            for left, right in combinations(triple, 2):
                if (left, right) in self.variables:
                    clause.append(-self.variables[left, right])
                elif not self.known[left] & (1 << right):
                    break
            else:
                self.clauses.append(tuple(clause))
        self.record_residues(use_degrees)
        if use_degrees:
            for row, (lower, upper) in sorted(self.degree_rows.items()):
                self.at_most(row, upper)
                self.at_most(tuple(-literal for literal in row), len(row) - lower)
        if use_lex:
            anchor = parts[0] if core is not None else max(parts, key=len)
            for part in parts:
                if part == anchor:
                    continue
                for left, right in zip(part, part[1:]):
                    word = [(self.variable(left, vertex), self.variable(right, vertex)) for vertex in anchor]
                    self.lex([(first, second) for first, second in word if first and second])

    def variable(self, left, right):
        return self.variables.get((min(left, right), max(left, right)), 0)

    def record_residues(self, degrees):
        for picked, anti in independent_extensions(self.moved):
            limit = self.bound - picked.bit_count()
            hit = 0
            for index in bits(picked):
                hit |= 1 << (index // 2)
            fixed = sum(1 << vertex for vertex, member in enumerate(self.memberships) if not member & hit)
            self.residues[fixed] = min(self.residues.get(fixed, self.bound), limit)
            if not degrees:
                continue
            residue = fixed | (anti << self.fixed)
            if limit < 0 or residue.bit_count() >= RAMSEY[limit + 1]:
                self.clauses.append(())
                continue
            lower = max(0, residue.bit_count() - RAMSEY[limit])
            for vertex in bits(residue):
                constant = (residue & self.known[vertex]).bit_count()
                row = tuple(sorted(self.variable(vertex, other) for other in bits(fixed)
                                   if self.variable(vertex, other)))
                old_min, old_max = self.degree_rows.get(row, (0, len(row)))
                self.degree_rows[row] = (max(old_min, lower - constant), min(old_max, limit - constant))
        compressed = []
        for domain, alpha in sorted(self.residues.items(), key=lambda item: (item[1], -item[0].bit_count(), item[0])):
            if not any(domain & ~other == 0 and smaller <= alpha for other, smaller in compressed):
                compressed.append((domain, alpha))
        self.residues = tuple(compressed)

    def at_most(self, row, limit):
        if limit < 0:
            self.clauses.append(())
            return
        if limit >= len(row):
            return
        if limit == 0:
            self.clauses.extend((-literal,) for literal in row)
            return
        if len(row) == limit + 1:
            self.clauses.append(tuple(-literal for literal in row))
            return
        previous = ()
        for literal in row:
            current = tuple(range(self.next + 1, self.next + 1 + limit))
            self.next += limit
            self.clauses.append((-literal, current[0]))
            for offset, threshold in enumerate(previous):
                self.clauses.append((-threshold, current[offset]))
                if offset + 1 < limit:
                    self.clauses.append((-literal, -threshold, current[offset + 1]))
            if previous:
                self.clauses.append((-literal, -previous[-1]))
            previous = current

    def lex(self, word):
        prefix = ()
        for left, right in word:
            self.next += 1
            self.clauses.extend((prefix + (-left, right), prefix + (left, right, self.next),
                                 prefix + (-left, -right, self.next)))
            prefix = (-self.next,)

    def cut(self, picked):
        assert picked & ~self.fixed_mask == 0
        assert any(picked & ~domain == 0 and picked.bit_count() > alpha for domain, alpha in self.residues)
        assert not any(self.known[vertex] & picked for vertex in bits(picked))
        return tuple(self.variables[left, right] for left, right in combinations(bits(picked), 2)
                     if (left, right) in self.variables)

    def seed(self, size):
        done = set()
        for domain, alpha in self.residues:
            if alpha + 1 > size:
                continue
            for picked in witnesses(self.known, domain, max(0, alpha + 1)):
                cut = self.cut(picked)
                if cut not in done:
                    done.add(cut)
                    self.clauses.append(cut)

    def extend(self, assignment):
        result = list(self.known)
        for (left, right), number in self.variables.items():
            if number in assignment:
                result[left] |= 1 << right
                result[right] |= 1 << left
        return result

    def output(self, filename):
        with open(filename, 'w', encoding='ascii') as stream:
            print('p cnf', self.next, len(self.clauses), file=stream)
            for row in self.clauses:
                print(*row, 0, file=stream)

    def solve(self, trace, cap, model_cap=1, solver_name='cadical195'):
        from pysat.solvers import Solver

        seen = set()
        models = []
        with Solver(name=solver_name, bootstrap_with=self.clauses) as solver:
            for index in range(1, cap + 1):
                if not solver.solve():
                    print(f'EXHAUSTED models={len(models)} calls={index} cuts={len(seen)}', flush=True)
                    return models
                assignment = {literal for literal in solver.get_model() if literal > 0}
                adj = self.extend(assignment)
                old = len(seen)
                for domain, alpha in self.residues:
                    for picked in witnesses(adj, domain, max(0, alpha + 1)):
                        clause = self.cut(picked)
                        if clause not in seen:
                            seen.add(clause)
                            if trace:
                                print(picked, file=trace)
                            solver.add_clause(clause)
                        if len(seen) >= old + 48:
                            break
                    if len(seen) >= old + 48:
                        break
                if old == len(seen):
                    candidate = to_graph6(adj)
                    models.append(candidate)
                    print(f'MODEL calls={index} cuts={len(seen)} {candidate}', flush=True)
                    if len(models) == model_cap:
                        return models
                    solver.add_clause([-number if number in assignment else number for number in self.variables.values()])
                if index % 200 == 0:
                    print(f'PROGRESS calls={index} cuts={len(seen)}', flush=True)
        print(f'OPEN calls={cap} cuts={len(seen)}', flush=True)
        return models


def control():
    petersen = {'adj': (40, 20, 34, 17, 10, 5), 'groups': (0, 1, 2, 4), 'counts': (1, 1, 1, 1)}
    c5 = {'adj': (4, 8, 9, 6), 'groups': (0, 1), 'counts': (0, 1)}
    cases = [(petersen, 4, None), (petersen, 3, None), (petersen, 4, [0]), (c5, 2, None)]
    counts = []
    for profile, alpha, core in cases:
        instance = Encoding(profile, alpha, core=core, use_lex=False)
        expected = set()
        for pattern in range(1 << len(instance.variables)):
            positives = {number for number in instance.variables.values() if pattern & (1 << (number - 1))}
            adj = instance.extend(positives)
            if any((adj[right] >> left) & 1 and adj[right] & adj[left]
                   for left, right in combinations(range(len(adj)), 2)):
                continue
            if not any(all(not adj[left] & (1 << right) for left, right in combinations(row, 2))
                       for row in combinations(range(len(adj)), alpha + 1)):
                expected.add(to_graph6(adj))
        actual = instance.solve(None, 1000, model_cap=1000)
        assert set(actual) == expected
        counts.append(len(actual))
    assert counts == [22, 0, 22, 1]
    print('Direct completion calibration:', counts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--profiles')
    parser.add_argument('--index', type=int, default=1)
    parser.add_argument('--core')
    parser.add_argument('--trace')
    parser.add_argument('--trace-input')
    parser.add_argument('--cnf')
    parser.add_argument('--cap', type=int, default=3000)
    parser.add_argument('--seed', type=int, default=4)
    parser.add_argument('--no-degrees', action='store_true')
    parser.add_argument('--no-lex', action='store_true')
    parser.add_argument('--solver', default='cadical195')
    args = parser.parse_args()
    if args.control:
        control()
        return
    with open(args.profiles, encoding='ascii') as stream:
        profiles = [json.loads(row) for row in stream]
    profile = profiles[args.index - 1]
    instance = Encoding(profile, 9, core=from_graph6(args.core) if args.core else None,
                        use_degrees=not args.no_degrees, use_lex=not args.no_lex)
    blocks = Counter(alpha for _, alpha in instance.residues)
    before = len(instance.clauses)
    instance.seed(args.seed)
    if args.trace_input:
        with open(args.trace_input, encoding='ascii') as stream:
            for row in stream:
                instance.clauses.append(instance.cut(int(row)))
    print(f'INSTANCE {args.index} fixed={instance.fixed} core={args.core} base={before} '
          f'nv={instance.next} edge={len(instance.variables)} clauses={len(instance.clauses)} residues={sorted(blocks.items())}',
          flush=True)
    if args.cnf:
        instance.output(args.cnf)
    if args.cap:
        if args.trace:
            with open(args.trace, 'w', encoding='ascii', buffering=1) as trace:
                instance.solve(trace, args.cap, solver_name=args.solver)
        else:
            instance.solve(None, args.cap, solver_name=args.solver)


if __name__ == '__main__':
    main()
