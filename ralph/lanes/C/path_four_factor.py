"""P4 factor pilot: eager exact one-side Ramsey rows, then a joined model."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import time

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

from kernel_projection import bits, decode, encode
from path_four_forced import bounds, Conflict, propagate
from path_four_sat import independent_witnesses


def independent_sets(adj, remaining):
    yield 0
    while remaining:
        low = remaining & -remaining
        remaining ^= low
        for tail in independent_sets(adj, remaining & ~adj[low.bit_length() - 1]):
            yield low | tail


def projection_rows(seed, alpha, block, side):
    core = len(seed) - 2 * block
    wing = block - 1
    endpoint = len(seed) - 2 + side
    remaining = ((1 << len(seed)) - 1) ^ (1 << endpoint)
    permitted = ((1 << core) - 1) | (((1 << wing) - 1) << (core + side * wing))
    rows = ({}, {})
    for independent in independent_sets(seed, remaining):
        size = independent.bit_count()
        projection = independent & permitted
        for table, limit, extra in zip(rows, (2 * block, block), (0, 1)):
            allowed = alpha - size - extra
            if allowed < limit:
                table[projection] = min(allowed, table.get(projection, limit))
    for table in rows:
        for projection, allowed in sorted(table.items(), key=lambda item: item[0].bit_count()):
            if not projection:
                continue
            subset = projection
            while subset:
                subset = (subset - 1) & projection
                if table.get(subset, allowed + 1) <= allowed:
                    del table[projection]
                    break
    return rows


class Factor:
    def __init__(self, seed, degree, alpha, block, cap):
        self.fixed, self.possible, self.cross = bounds(seed, block)
        propagate(self.fixed, self.possible, degree, cap)
        self.seed = seed
        self.degree = degree
        self.alpha = alpha
        self.block = block
        self.cap = cap
        self.order = len(self.fixed)
        self.length = len(seed)
        self.cross_target = sum(map(int.bit_count, seed)) // 2 - degree * (self.order - 8 * block) // 2
        self.sides = (tuple(range(self.length, self.length + 2 * block)),
                      tuple(range(self.length + 2 * block, self.length + 4 * block)))

    def formula(self, sides, eager=True):
        active = set().union(*(self.sides[side] for side in sides))
        external = set().union(*self.sides) - active
        pool = IDPool()
        yes = pool.id('true')
        no = -yes
        cnf = CNF(from_clauses=[[yes]])
        literals = [[no] * self.order for _ in range(self.order)]
        edges = {}
        cross = set(self.cross)
        for left, right in combinations(range(self.order), 2):
            if self.fixed[left] >> right & 1:
                value = yes
            elif not (self.possible[left] >> right & 1):
                value = no
            elif (left in external or right in external) and (left, right) not in cross:
                value = None
            else:
                value = pool.id(('edge', left, right))
                edges[left, right] = value
            literals[left][right] = literals[right][left] = value

        def clause(values):
            values = list(values)
            if yes not in values:
                cnf.append([value for value in values if value != no])

        def at_most(values, limit):
            values = list(values)
            limit -= values.count(yes)
            variables = [value for value in values if value not in (yes, no)]
            if limit < 0:
                cnf.append([])
            elif limit < len(variables):
                cnf.extend(CardEnc.atmost(variables, limit, vpool=pool, encoding=EncType.seqcounter))

        def degree_row(values, target):
            known = [value for value in values if value is not None]
            at_most(known, target)
            at_most([-value for value in known], len(values) - target)

        for row in literals:
            degree_row(row, self.degree)
        degree_row([literals[left][right] for left, right in self.cross], self.cross_target)

        for left, mid, right in combinations(range(self.order), 3):
            triple = [literals[left][mid], literals[left][right], literals[mid][right]]
            if None not in triple:
                clause(-value for value in triple)

        both_cache = {}
        for left, right in combinations(range(self.order), 2):
            open_pair = literals[left][right]
            if open_pair == yes:
                continue
            pairs = []
            unknown = False
            for third in bits(self.possible[left] & self.possible[right]):
                first, second = literals[left][third], literals[right][third]
                if first is None or second is None:
                    unknown = True
                else:
                    pairs.append((first, second))
            threshold = len(pairs) > self.cap
            needs_support = open_pair is not None and not unknown and (yes, yes) not in pairs
            if not threshold and not needs_support:
                continue
            shared = []
            for first, second in pairs:
                if first == yes or second == yes:
                    shared.append(second if first == yes else first)
                    continue
                key = tuple(sorted((first, second)))
                value = both_cache.get(key)
                if value is None:
                    value = both_cache[key] = pool.id(('both', *key))
                    cnf.extend([[-value, first], [-value, second], [value, -first, -second]])
                shared.append(value)
            if threshold:
                at_most(shared, self.cap)
            if needs_support:
                clause([open_pair, *shared])

        available = {}

        def availability(vertex, independent):
            hits = tuple(literals[vertex][other] for other in bits(independent)
                         if literals[vertex][other] != no)
            if yes in hits:
                return no
            if not hits:
                return yes
            if len(hits) == 1:
                return -hits[0]
            value = available.get(hits)
            if value is None:
                value = available[hits] = pool.id(('available', hits))
                clause([value, *hits])
            return value

        if eager:
            for side in sides:
                all_boundary = self.sides[side]
                external_block = all_boundary[:self.block] if side == 0 else all_boundary[-self.block:]
                for table, group in zip(projection_rows(self.seed, self.alpha, self.block, side),
                                        (all_boundary, external_block)):
                    for independent, limit in sorted(table.items()):
                        at_most((availability(vertex, independent) for vertex in group), limit)
        return cnf, literals, edges

    def solve(self, sides, solver_name, budget, rounds, eager=True):
        cnf, literals, edges = self.formula(sides, eager)
        cuts = 0
        with Solver(name=solver_name, bootstrap_with=cnf.clauses) as solver:
            for iteration in range(1, rounds + 1):
                if budget:
                    solver.conf_budget(budget)
                    result = solver.solve_limited()
                else:
                    result = solver.solve()
                conflicts = solver.accum_stats()['conflicts']
                stats = (iteration, conflicts, cuts, cnf.nv, len(cnf.clauses))
                if result is not True:
                    return ('unsat' if result is False else 'conflict-limit'), stats, None
                if len(sides) == 1:
                    return 'feasible', stats, None
                model = set(solver.get_model())
                adj = list(self.fixed)
                for (left, right), variable in edges.items():
                    if variable in model:
                        adj[left] |= 1 << right
                        adj[right] |= 1 << left
                assert all(mask.bit_count() == self.degree for mask in adj)
                for left, right in combinations(range(self.order), 2):
                    neighbours = (adj[left] & adj[right]).bit_count()
                    assert neighbours == 0 if adj[left] >> right & 1 else 1 <= neighbours <= self.cap
                witnesses = independent_witnesses(adj, self.alpha + 1, 16)
                if not witnesses:
                    return 'found', stats, encode(adj)
                for witness in witnesses:
                    solver.add_clause([literals[left][right] for left, right in combinations(bits(witness), 2)
                                       if literals[left][right] != -1])
                    cuts += 1
        return 'iteration-limit', stats, None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('--mode', choices=['side', 'join', 'both'], default='both')
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--sample', type=int, default=0, help='spread sample per e(A) stratum')
    parser.add_argument('--row', type=int, action='append')
    parser.add_argument('--budget', type=int, default=7000)
    parser.add_argument('--rounds', type=int, default=24)
    parser.add_argument('--solver', default='cadical195')
    args = parser.parse_args()
    params = (6, 6, 2, 4) if args.control else (9, 9, 3, 6)
    strata = defaultdict(list)
    for index, line in enumerate(args.catalogue.read_text().splitlines()):
        if args.row and index not in args.row:
            continue
        seed = decode(line)
        strata[sum(map(int.bit_count, seed)) // 2].append((index, seed))
    counts = Counter()
    for edge, rows in sorted(strata.items(), reverse=True):
        samples = rows if not args.sample else [rows[idx * len(rows) // args.sample]
                                                for idx in range(min(len(rows), args.sample))]
        for index, seed in samples:
            try:
                factored = Factor(seed, *params)
            except Conflict:
                counts['propagation'] += 1
                print('row', index, 'e', edge, 'propagation', flush=True)
                continue
            for sides in {'side': [(0,), (1,)], 'join': [(0, 1)],
                          'both': [(0,), (1,), (0, 1)]}[args.mode]:
                start = time.process_time()
                status, stats, graph = factored.solve(sides, args.solver, args.budget, args.rounds)
                counts[(sides, status)] += 1
                print('row', index, 'e', edge, 'side', ''.join(map(str, sides)), status, *stats,
                      'CPU-s', round(time.process_time() - start, 4), flush=True)
                if graph:
                    print('CONTROL' if args.control else 'UNVERIFIED CANDIDATE', graph, flush=True)
    print('totals', dict(counts), flush=True)


if __name__ == '__main__':
    main()
