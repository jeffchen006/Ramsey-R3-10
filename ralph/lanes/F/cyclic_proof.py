"""Find finite obstructions for cyclic unsigned quotients via projected independent sets."""

import argparse
from itertools import combinations, islice, product
from pathlib import Path
import subprocess

from pysat.solvers import Minisat22

from orbit_extend import ROOT, independent_sets, to_graph6
from relift_audit import decode, explicit_lift, pairs, walk_score


class Formula:
    def __init__(self, text, target):
        self.base = base = decode(text)
        self.size, self.target = len(base), target
        self.ident = {edge: index for index, edge in enumerate(
            (edge for edge in combinations(range(self.size), 2) if base[edge[0]][edge[1]] == 1), 1)}
        self.variables = len(self.ident)
        self.clauses, self.supports, self.memo = [], {}, {}
        self.trace = []
        components = [{vertex} for vertex in range(self.size)]
        for (left, right), ident in self.ident.items():
            if components[left] is not components[right]:
                joined = components[left] | components[right]
                for vertex in joined:
                    components[vertex] = joined
                self.clauses.append([-ident])
                self.trace.append(f'forest {ident}')
        for triple in combinations(range(self.size), 3):
            edges = list(combinations(triple, 2))
            if all(edge in self.ident for edge in edges):
                indices = [self.ident[edge] for edge in edges]
                self.trace.append('tri ' + ' '.join(map(str, indices)))
                for point in product((0, 1), repeat=3):
                    if sum(point) % 2:
                        self.clauses.append([-index if bit else index for index, bit in zip(indices, point)])

    def xor(self, terms):
        expr = tuple(sorted(terms))
        assert expr
        if len(expr) == 1:
            return expr[0]
        if expr not in self.memo:
            left, right = self.xor(expr[:-1]), expr[-1]
            self.variables += 1
            result = self.variables
            self.clauses.extend(([left, right, -result], [-left, -right, -result],
                                 [left, -right, result], [-left, right, result]))
            self.trace.append(f'xor {result} {left} {right}')
            self.memo[expr] = result
        return self.memo[expr]

    def cycles(self, full, single):
        assert 2 * len(full) + len(single) == self.target and not (set(full) & set(single))
        assert all(self.base[vertex][other] == 0 for vertex in full for other in full + single)
        parent, cycles = {}, []
        todo = set(single)
        while todo:
            root = min(todo)
            parent[root] = frozenset()
            queue = [root]
            todo.remove(root)
            while queue:
                left = queue.pop()
                for right in sorted(todo):
                    edge = tuple(sorted((left, right)))
                    if edge in self.ident:
                        parent[right] = parent[left] ^ {self.ident[edge]}
                        queue.append(right)
                        todo.remove(right)
        for edge in combinations(single, 2):
            left, right = edge
            assert self.base[left][right] != 2
            if edge in self.ident:
                cycle = parent[left] ^ parent[right] ^ {self.ident[edge]}
                if cycle:
                    cycles.append(cycle)
        return cycles

    def add(self, full, single):
        if (full, single) in self.supports:
            return
        cycles = self.cycles(full, single)
        clause = [self.xor(cycle) for cycle in cycles]
        self.supports[full, single] = len(cycles)
        masks = [sum(1 << vertex for vertex in seq) for seq in (full, single)]
        if clause:
            self.clauses.append(clause)
            self.trace.append('cut ' + ' '.join(map(str, masks + clause)))
        else:
            self.variables += 1
            self.clauses.extend(([self.variables], [-self.variables]))
            self.trace.append('forestcut ' + ' '.join(map(str, masks + [self.variables])))

    def add_orbit(self, full, single):
        for shift in range(self.size):
            def move(labels):
                return tuple(sorted((vertex + shift) % self.size for vertex in labels))
            self.add(move(full), move(single))

    def lift(self, model):
        positive = {lit for lit in model if lit > 0}
        return explicit_lift(self.base, iter(int(self.ident[left, right] not in positive)
            for left, right in pairs(self.size) if left < right and self.base[left][right] == 1))

    def subsets(self, graph):
        for witness in independent_sets(graph, (1 << len(graph)) - 1, self.target):
            full, single = [], []
            for vertex in range(self.size):
                count = ((witness >> (2 * vertex)) & 3).bit_count()
                if count:
                    (full if count == 2 else single).append(vertex)
            yield tuple(full), tuple(single)

    def search(self, rounds):
        with Minisat22(bootstrap_with=self.clauses) as solver:
            for turn in range(rounds + 1):
                solver.conf_budget(40000)
                status = solver.solve_limited()
                if status is False:
                    return 'no', turn, None
                if status is None or turn == rounds:
                    return 'cap', turn, None
                graph = self.lift(solver.get_model() or [])
                pool = set(islice(self.subsets(graph), 32))
                if not pool:
                    assert walk_score(graph, self.target) == 0
                    return 'yes', turn, graph
                added = len(self.clauses)
                pool = sorted(pool, key=lambda support: (len(self.cycles(*support)), support))
                assert all(support not in self.supports for support in pool)
                for support in pool[:2]:
                    self.add_orbit(*support)
                    if self.supports[support] == 0:
                        break
                for clause in self.clauses[added:]:
                    solver.add_clause(clause)
        raise AssertionError('unreachable')

    def serialize(self, name):
        name.with_suffix('.cnf').write_text(f'p cnf {self.variables} {len(self.clauses)}\n' +
            ''.join(' '.join(map(str, clause + [0])) + '\n' for clause in self.clauses))
        name.with_suffix('.trace').write_text(''.join(row + '\n' for row in self.trace))


def proof(name):
    cnf, lrat = name.with_suffix('.cnf'), name.with_suffix('.lrat')
    for command, expected, line in ((['cadical', '-q', '-n', '--lrat', '--no-binary'], 20, 's UNSATISFIABLE'),
                                    (['lrat-check'], 0, 'c VERIFIED'),
                                    (['cake_lpr', '--CML_HEAP_SIZE=256', '--CML_STACK_SIZE=32'], 0, 's VERIFIED UNSAT')):
        args = [ROOT / 'opt/bin' / command[0], *command[1:], cnf, lrat]
        run = subprocess.run(['timeout', '30', 'prlimit', '--cpu=22:24', '--', *args], capture_output=True, text=True)
        name.with_suffix('.' + command[0] + '.log').write_text(run.stdout + run.stderr)
        if run.returncode != expected or line not in run.stdout.splitlines():
            return f'{command[0]}_nonterminal_{run.returncode}'
    return 'dual'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('out', type=Path)
    parser.add_argument('target', type=int)
    parser.add_argument('--first', type=int, default=0)
    parser.add_argument('--end', type=int)
    parser.add_argument('--rounds', type=int, default=35)
    args = parser.parse_args()
    args.out.mkdir(exist_ok=True)
    inputs = args.source.read_text().splitlines()
    for index in range(args.first, len(inputs) if args.end is None else args.end):
        formula = Formula(inputs[index], args.target)
        status, rounds, witness = formula.search(args.rounds)
        name = args.out / f'{index:03}'
        checked = '-'
        if status == 'no':
            formula.serialize(name)
            checked = proof(name)
        if status == 'yes':
            name.with_suffix('.g6').write_text(to_graph6(witness) + '\n')
        print(f'row={index} status={status} rounds={rounds} supports={len(formula.supports)} '
              f'vars={formula.variables} clauses={len(formula.clauses)} proof={checked}', flush=True)


if __name__ == '__main__':
    main()
