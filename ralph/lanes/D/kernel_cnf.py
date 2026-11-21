#!/usr/bin/env python3
"""Fixed-kernel Ramsey CNFs; variable order matches SMS (row-major)."""

from itertools import combinations
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
MODES = ('base', 'fused', 'local', 'profile', 'minedge')


def decode(line):
    size = ord(line[0]) - 63
    bits = [(ord(ch) - 63) >> shift & 1 for ch in line[1:] for shift in range(5, -1, -1)]
    assert size < 63 and len(bits) >= size * (size - 1) // 2
    return {(left, right) for (left, right), bit in zip(
        ((left, right) for right in range(size) for left in range(right)), bits) if bit}


def kernel_fixed(n, degree, line):
    side = degree - 1
    assert ord(line[0]) - 63 == 2 * side
    cross = decode(line)
    assert all(left < side <= right for left, right in cross)
    edges = {(0, 1)} | {(0, a) for a in range(2, degree + 1)} | {
        (1, b) for b in range(degree + 1, 2 * degree)
    } | {(left + 2, right + 2) for left, right in cross}
    return {(left, right): (left, right) in edges for left, right in combinations(range(n), 2)
            if right < 2 * degree or left < 2}


def neg(lit):
    return not lit if isinstance(lit, bool) else -lit


class Cnf:
    def __init__(self, n, fixed):
        self.n = n
        self.fixed = fixed
        self.nvars = n * (n - 1) // 2
        self.clauses = [[self.edge(*edge, simplify=False) * (1 if val else -1)]
                        for edge, val in fixed.items()]

    def edge(self, left, right, simplify=True):
        left, right = min(left, right), max(left, right)
        if simplify and (left, right) in self.fixed:
            return self.fixed[left, right]
        return left * self.n - left * (left + 1) // 2 + right - left

    def add(self, *lits):
        if any(lit is True for lit in lits):
            return
        self.clauses.append([lit for lit in lits if lit is not False])

    def new(self):
        self.nvars += 1
        return self.nvars

    def conjunction(self, left, right):
        if left is False or right is False:
            return False
        if left is True:
            return right
        if right is True:
            return left
        out = self.new()
        self.add(-out, left)
        self.add(-out, right)
        self.add(neg(left), neg(right), out)
        return out

    def totalizer(self, leaves, cap):
        if cap <= 0 or not leaves:
            return []
        if len(leaves) == 1:
            return leaves
        mid = len(leaves) // 2
        left = self.totalizer(leaves[:mid], cap)
        right = self.totalizer(leaves[mid:], cap)
        outs = [self.new() for _ in range(min(len(left) + len(right), cap))]
        for p in range(len(left) + 1):
            for q in range(len(right) + 1):
                count = p + q
                if 0 < count <= len(outs):
                    self.add(neg(left[p - 1]) if p else False, neg(right[q - 1]) if q else False, outs[count - 1])
                if count < len(outs):
                    self.add(left[p] if p < len(left) else False, right[q] if q < len(right) else False, -outs[count])
        return outs

    def thresholds(self, lits, cap):
        constants = sum(lit is True for lit in lits)
        leaves = [lit for lit in lits if not isinstance(lit, bool)]
        outs = ([True] * min(cap, constants)) + self.totalizer(leaves, cap - constants)
        return outs + [False] * (cap - len(outs))

    def cardinality(self, lits, lower, upper):
        constants = sum(lit is True for lit in lits)
        lower, upper = lower - constants, upper - constants
        leaves = [lit for lit in lits if not isinstance(lit, bool)]
        if lower > len(leaves) or upper < 0 or lower > upper:
            self.add()
            return
        if upper == 0 or lower == len(leaves):
            for lit in leaves:
                self.add(lit if lower == len(leaves) else neg(lit))
            return
        if upper >= len(leaves):
            upper = len(leaves)
        direct_cap = max(lower, upper + 1 if upper < len(leaves) else 0)
        reverse_cap = max(len(leaves) - upper, len(leaves) - lower + 1 if lower else 0)
        if reverse_cap < direct_cap:
            leaves = [neg(lit) for lit in leaves]
            lower, upper = len(leaves) - upper, len(leaves) - lower
        outs = self.totalizer(leaves, min(direct_cap, reverse_cap))
        if lower > 0:
            self.add(outs[lower - 1])
        if upper < len(leaves):
            self.add(neg(outs[upper]))

    def write(self, path):
        with path.open('w') as stream:
            stream.write(f'p cnf {self.nvars} {len(self.clauses)}\n')
            stream.writelines(' '.join(map(str, clause + [0])) + '\n' for clause in self.clauses)


def kernel_is(cnf, degree, k):
    inner = range(2 * degree)
    outer = range(2 * degree, cnf.n)
    for missing, cap in ((1, 0), (2, 2), (3, 5)):
        if k < missing:
            continue
        for seed in combinations(inner, k - missing):
            if any(cnf.edge(left, right) for left, right in combinations(seed, 2)):
                continue
            hits = [[cnf.edge(pos, vertex) for pos in seed] for vertex in outer]
            if missing == 1:
                for row in hits:
                    cnf.add(*row)
                continue
            avoids = []
            for row in hits:
                if any(lit is True for lit in row):
                    avoids.append(False)
                    continue
                avoid = cnf.new()
                avoids.append(avoid)
                cnf.add(avoid, *row)
                for lit in row:
                    cnf.add(-avoid, neg(lit))
            cnf.cardinality(avoids, 0, cap)
            if missing == 2:
                for left, right in combinations(outer, 2):
                    cnf.add(neg(avoids[left - len(inner)]), neg(avoids[right - len(inner)]), cnf.edge(left, right))


def write(n, degree, k, maximum, line, mode, path):
    fixed = kernel_fixed(n, degree, line)
    cnf = Cnf(n, fixed)
    if mode == 'base':
        original = path.parent / 'original.cnf'
        if not original.exists():
            subprocess.run([sys.executable, '-B', str(ROOT / 'sms/gen_ramsey.py'), '-n', str(n), '-k', str(k),
                            '--dmin', str(degree), '--dmax', str(degree), '--mtf',
                            '--codeg-max', str(maximum), '-o', str(original)], check=True)
        with original.open() as inp, path.open('w') as out:
            _, _, nv, nc = inp.readline().split()
            out.write(f'p cnf {nv} {int(nc) + len(cnf.clauses)}\n')
            for record in inp:
                out.write(record)
            out.writelines(f'{unit[0]} 0\n' for unit in cnf.clauses)
        return
    vertices = range(n)
    for left, middle, right in combinations(vertices, 3):
        cnf.add(neg(cnf.edge(left, middle)), neg(cnf.edge(left, right)), neg(cnf.edge(middle, right)))
    for vertex in vertices:
        cnf.cardinality([cnf.edge(vertex, other) for other in vertices if other != vertex], degree, degree)
    codegs = {}
    for left, right in combinations(vertices, 2):
        if cnf.edge(left, right) is True:
            continue
        common = [cnf.conjunction(cnf.edge(left, mid), cnf.edge(right, mid))
                  for mid in vertices if mid not in (left, right)]
        outs = cnf.thresholds(common, maximum + 1)
        cnf.add(neg(outs[maximum]))
        cnf.add(cnf.edge(left, right), outs[0])
        codegs[left, right] = outs
    if mode in ('local', 'profile', 'minedge'):
        kernel_is(cnf, degree, k)
    if mode in ('profile', 'minedge'):
        assert k == degree + 1 and maximum >= 2
        target = degree * (degree - 1) - (n - degree - 1)
        root_count = len(decode(line))
        singleton_lower = 0
        if mode == 'minedge' and maximum == 3:
            cycle_floor = 2 * degree * (degree - 1) - 3 * (n - degree - 1)
            singleton_lower = max(0, (degree * root_count + 1) // 2 - cycle_floor)
        for vertex in vertices:
            incident = [(tuple(sorted((vertex, other))), other) for other in vertices if other != vertex]
            incident = [(codegs[pair], other) for pair, other in incident if pair in codegs]
            cnf.cardinality([lit for outs, _ in incident for lit in outs[1:maximum]], target, target)
            singles = [(cnf.conjunction(outs[0], neg(outs[1])), other) for outs, other in incident]
            cnf.cardinality([lit for lit, _ in singles], singleton_lower, degree)
            for mid in vertices:
                if mid == vertex or cnf.edge(mid, vertex) is False:
                    continue
                leaves = [cnf.conjunction(lit, cnf.edge(mid, other)) for lit, other in singles if other != mid]
                conflicts = cnf.thresholds(leaves, 2)
                cnf.add(neg(cnf.edge(mid, vertex)), neg(conflicts[1]))
    if mode == 'minedge':
        for center in (0, 1):
            for vertex in range(2, 2 * degree):
                if cnf.edge(center, vertex) is not True:
                    continue
                contributions = [cnf.conjunction(cnf.edge(vertex, other), threshold)
                                 for other in vertices if other not in (center, vertex)
                                 for threshold in codegs.get(tuple(sorted((center, other))), [])[1:maximum]]
                cnf.cardinality(contributions, root_count, len(contributions))
    cnf.write(path)
