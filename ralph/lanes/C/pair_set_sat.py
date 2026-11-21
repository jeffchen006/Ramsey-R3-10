"""SAT with unlabelled common-neighbour sets for a fixed K2,2 pair residue."""

import argparse
from itertools import combinations
from pathlib import Path
import time

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

from kernel_projection import bits, decode, encode, independent_masks
from pair_packages import restrict


class FixedResidue:
    def __init__(self, adj, degree, cap):
        self.adj = adj
        self.degree = degree
        self.cap = cap
        self.order = len(adj)
        self.indeps = sorted(independent_masks(adj, (1 << self.order) - 1), key=int.bit_count, reverse=True)
        assert self.indeps[0].bit_count() <= degree - 2
        self.pool = IDPool()
        self.sat = CNF()
        self.colours = [(mask, self.pool.id(('C', mask))) for mask in self.indeps if mask.bit_count() == degree - 2]
        self.sides = [[self.pool.id(('exclusive', side, x)) for x in range(self.order)] for side in range(4)]
        self.side_intersections = {}
        self.side_misses = {}
        self.inserted = set()

        self.card([var for _, var in self.colours], degree - 2, 'eq')
        for (mask, var), (other, var_other) in combinations(self.colours, 2):
            if (mask & other).bit_count() > cap - 2:
                self.sat.append([-var, -var_other])
        for side in self.sides:
            self.card(side, degree - 3, 'eq')
            for left, neighbors in enumerate(adj):
                for right in bits(neighbors >> (left + 1)):
                    self.sat.append([-side[left], -side[right + left + 1]])
            for vertex, neighbors in enumerate(adj):
                opposite = self.sides[2:] if side in self.sides[:2] else self.sides[:2]
                self.sat.append([side[vertex]] + [side[other] for other in bits(neighbors)] +
                                [row[vertex] for row in opposite])
        for vertex, neighbors in enumerate(adj):
            for left in self.sides[:2]:
                for right in self.sides[2:]:
                    self.sat.append([-left[vertex], -right[vertex]])
            colour_vars = [var for mask, var in self.colours if mask >> vertex & 1]
            self.sat.append(colour_vars)
            self.card(colour_vars + [side[vertex] for side in self.sides], degree - neighbors.bit_count(), 'eq')
        for left, right in combinations(range(self.order), 2):
            if adj[left] >> right & 1:
                continue
            fixed = (adj[left] & adj[right]).bit_count()
            both = (1 << left) | (1 << right)
            common = [var for mask, var in self.colours if mask & both == both]
            common += [self.conjunction(side[left], side[right]) for side in self.sides]
            self.card(common, cap - fixed, 'max')
            if not fixed:
                self.sat.append(common)
        for left, right in ((0, 1), (2, 3)):
            self.lex(self.sides[left], self.sides[right])
            both_side = [self.conjunction(var_left, var_right)
                         for var_left, var_right in zip(self.sides[left], self.sides[right])]
            self.card(both_side, cap - 3, 'max')
        self.lex(self.sides[0], self.sides[2])
        for indep in self.indeps:
            if indep.bit_count() != degree - 2:
                break
            for pair in ((0, 1), (2, 3)):
                self.sat.append([-self.miss(side, indep) for side in pair])

    def card(self, terms, bound, kind):
        if bound < 0 or kind == 'eq' and bound > len(terms):
            self.sat.append([])
        elif kind == 'eq':
            self.sat.extend(CardEnc.equals(terms, bound=bound, vpool=self.pool, encoding=EncType.seqcounter).clauses)
        elif bound < len(terms):
            self.sat.extend(CardEnc.atmost(terms, bound=bound, vpool=self.pool, encoding=EncType.seqcounter).clauses)

    def conjunction(self, first, second):
        key = (first, second)
        if key not in self.side_intersections:
            var = self.pool.id(('both', first, second))
            self.side_intersections[key] = var
            self.sat.extend([[-var, first], [-var, second], [var, -first, -second]])
        return self.side_intersections[key]

    def lex(self, left, right):
        prefix = self.pool.id()
        self.sat.append([prefix])
        for first, second in zip(reversed(left), reversed(right)):
            self.sat.append([-prefix, first, -second])
            new_prefix = self.pool.id()
            self.sat.extend([[-prefix, first, second, new_prefix], [-prefix, -first, -second, new_prefix]])
            prefix = new_prefix

    def miss(self, side, indep):
        key = (side, indep)
        if key not in self.side_misses:
            var = self.pool.id(('miss', side, indep))
            terms = [self.sides[side][x] for x in bits(indep)]
            self.side_misses[key] = var
            self.sat.append([var] + terms)
            self.sat.extend([[-var, -term] for term in terms])
        return self.side_misses[key]

    def cut(self, indep, parity):
        key = (indep, parity)
        assert key not in self.inserted
        self.inserted.add(key)
        terms = [var for mask, var in self.colours if not mask & indep]
        terms += [self.miss(side, indep) for side in range(2 * parity, 2 * parity + 2)]
        self.card(terms, self.degree - indep.bit_count(), 'max')

    def extension(self, commons, sides):
        outside = self.order
        right = outside + 1
        adj = self.adj[:] + [0] * (self.degree + 4)

        def edge(first, second):
            adj[first] |= 1 << second
            adj[second] |= 1 << first

        start = right + 1
        for index, mask in enumerate(commons + sides, start=start):
            for vertex in bits(mask):
                edge(index, vertex)
        boundary = start + len(commons)
        for index in range(start, boundary):
            edge(outside, index)
            edge(right, index)
        for index in range(boundary, boundary + 2):
            edge(outside, index)
            for other in range(boundary + 2, boundary + 4):
                edge(index, other)
        for index in range(boundary + 2, boundary + 4):
            edge(right, index)
        assert all(mask.bit_count() == self.degree for mask in adj)
        assert all(not adj[left] & adj[right] for left, neighbors in enumerate(adj) for right in bits(neighbors))
        return adj

    def solve(self, outfile, eager):
        for indep in self.indeps:
            if indep.bit_count() < eager:
                break
            for parity in (0, 1):
                self.cut(indep, parity)
        start = time.process_time()
        print('base', len(self.sat.clauses), self.sat.nv, 'colours', len(self.colours), flush=True)
        with Solver(name='cadical195', bootstrap_with=self.sat.clauses) as solver:
            iterations = 0
            while solver.solve():
                iterations += 1
                model = {var for var in solver.get_model() if var > 0}
                commons = [mask for mask, var in self.colours if var in model]
                sides = [sum(1 << vertex for vertex, var in enumerate(side) if var in model) for side in self.sides]
                nrows = len(self.sat.clauses)
                for indep in self.indeps:
                    if indep.bit_count() < 2:
                        break
                    missed = sum(not mask & indep for mask in commons)
                    for parity in (0, 1):
                        count = missed + sum(not mask & indep for mask in sides[2 * parity:2 * parity + 2])
                        if count + indep.bit_count() > self.degree:
                            self.cut(indep, parity)
                if nrows == len(self.sat.clauses):
                    graph = encode(self.extension(commons, sides))
                    print('SAT candidate', graph, f'iterations={iterations} cpu={time.process_time()-start:.3f}', flush=True)
                    if outfile is not None:
                        Path(outfile + '.g6').write_text(graph + '\n')
                    return graph
                solver.append_formula(self.sat.clauses[nrows:])
                if iterations % 20 == 0:
                    print('progress', iterations, len(self.inserted), len(self.sat.clauses), flush=True)
            print('UNSAT unchecked', f'iterations={iterations} clauses={len(self.sat.clauses)} cpu={time.process_time()-start:.3f}',
                  flush=True)
            if outfile is not None:
                self.sat.to_file(outfile + '.cnf')
            return None


def calibration(path):
    checked = 0
    for line in Path(path).read_text().splitlines():
        adj = decode(line)
        degree = adj[0].bit_count()
        cap = max((adj[left] & adj[right]).bit_count() for left, right in combinations(range(len(adj)), 2))
        for left, right in combinations(range(len(adj)), 2):
            common = adj[left] & adj[right]
            if common.bit_count() != degree - 2:
                continue
            exclusive = adj[left] ^ common, adj[right] ^ common
            if not all(adj[vertex] & exclusive[1] == exclusive[1] for vertex in bits(exclusive[0])):
                continue
            outside = list(bits(((1 << len(adj)) - 1) & ~(adj[left] | adj[right] | (1 << left) | (1 << right))))
            found = FixedResidue(restrict(adj, outside), degree, cap).solve(None, degree - 2)
            assert found is not None
            extension = decode(found)
            assert max(mask.bit_count() for mask in independent_masks(extension, (1 << len(adj)) - 1)) == degree
            checked += 1
    assert checked == 7
    print('calibration passed:', checked)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('scan', 'calibrate'))
    parser.add_argument('file')
    parser.add_argument('--index', type=int, default=0)
    parser.add_argument('--eager', type=int, default=7)
    parser.add_argument('--out')
    args = parser.parse_args()
    if args.mode == 'calibrate':
        calibration(args.file)
        return
    adj = decode(Path(args.file).read_text().splitlines()[args.index])
    FixedResidue(adj, 9, 7).solve(args.out, args.eager)


if __name__ == '__main__':
    main()
