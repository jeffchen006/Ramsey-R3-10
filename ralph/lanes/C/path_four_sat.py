"""Fixed-residue P4 SAT pilot with exact cardinalities and lazy Ramsey rows."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import time

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

from kernel_projection import bits, decode, encode
from path_four_forced import Conflict, bounds, propagate


def independent_witnesses(adj, size, count):
    full = (1 << len(adj)) - 1
    output = []

    def visit(available, chosen, remaining):
        if remaining == 0:
            output.append(chosen)
            return len(output) >= count
        if available.bit_count() < remaining:
            return False
        uncoloured = available
        colour = 0
        ordered = []
        while uncoloured:
            colour += 1
            options = uncoloured
            while options:
                low = options & -options
                vertex = low.bit_length() - 1
                uncoloured ^= low
                options &= adj[vertex]
                ordered.append((low, vertex, colour))
        for low, vertex, colour in reversed(ordered):
            if colour < remaining:
                break
            available ^= low
            if visit(available & ~adj[vertex], chosen | low, remaining - 1):
                return True
        return False

    visit(full, 0, size)
    return output


def formula(seed, degree, block, cap):
    fixed, possible, cross = bounds(seed, block)
    propagate(fixed, possible, degree, cap)
    pool = IDPool()
    cnf = CNF()
    order = len(fixed)
    cross_target = sum(map(int.bit_count, seed)) // 2 - degree * (order - 8 * block) // 2
    cnf.append([pool.id('true')])
    yes = 1
    no = -1
    literals = [[no] * order for _ in range(order)]
    edges = {}
    for left, right in combinations(range(order), 2):
        if fixed[left] >> right & 1:
            value = yes
        elif possible[left] >> right & 1:
            value = pool.id(('edge', left, right))
            edges[left, right] = value
        else:
            value = no
        literals[left][right] = value
        literals[right][left] = value

    def exactly(sequence, target):
        demand = target - sum(value == yes for value in sequence)
        variables = [value for value in sequence if value not in (yes, no)]
        if not 0 <= demand <= len(variables):
            cnf.append([])
        else:
            cnf.extend(CardEnc.equals(variables, demand, vpool=pool, encoding=EncType.seqcounter))

    def clause(values):
        if yes not in values:
            cnf.append([value for value in values if value != no])

    for row in literals:
        exactly(row, degree)
    exactly([literals[left][right] for left, right in cross], cross_target)
    for left, mid, right in combinations(range(order), 3):
        clause([-literals[left][mid], -literals[left][right], -literals[mid][right]])

    for left, right in combinations(range(order), 2):
        if fixed[left] >> right & 1 or fixed[left] & fixed[right]:
            continue
        support = [literals[left][right]]
        for third in bits(possible[left] & possible[right]):
            first, second = literals[left][third], literals[right][third]
            if first == yes or second == yes:
                support.append(second if first == yes else first)
            else:
                shared = pool.id(('both', left, right, third))
                cnf.extend([[-shared, first], [-shared, second]])
                support.append(shared)
        clause(support)

    return fixed, literals, edges, cnf


def search(seed, degree, alpha, block, cap, budget, max_iterations, solver_name):
    try:
        fixed, literals, edges, cnf = formula(seed, degree, block, cap)
    except Conflict:
        return 'propagation', 0, 0, 0, None
    total_cuts = 0
    with Solver(name=solver_name, bootstrap_with=cnf.clauses) as solver:
        for iteration in range(1, max_iterations + 1):
            if budget:
                solver.conf_budget(budget)
                result = solver.solve_limited()
            else:
                result = solver.solve()
            if result is not True:
                return ('unsat' if result is False else 'conflict-limit', iteration, total_cuts,
                        solver.accum_stats()['conflicts'], None)
            model = set(solver.get_model())
            adj = list(fixed)
            for (left, right), variable in edges.items():
                if variable in model:
                    adj[left] |= 1 << right
                    adj[right] |= 1 << left
            assert all(mask.bit_count() == degree for mask in adj)
            assert all(not adj[left] & adj[right] for left in range(len(adj)) for right in bits(adj[left]))
            for left, right in combinations(range(len(adj)), 2):
                shared = adj[left] & adj[right]
                assert shared or adj[left] >> right & 1
                if shared.bit_count() > cap:
                    rejected = list(bits(shared))[:cap + 1]
                    solver.add_clause(sorted({-literals[vertex][third] for vertex in (left, right)
                                              for third in rejected if literals[vertex][third] != 1}))
                    total_cuts += 1
            forbidden = independent_witnesses(adj, alpha + 1, 40)
            for witness in forbidden:
                solver.add_clause([literals[left][right] for left, right in combinations(bits(witness), 2)
                                   if literals[left][right] != -1])
                total_cuts += 1
            if not forbidden and all((adj[left] & adj[right]).bit_count() <= cap
                                     for left, right in combinations(range(len(adj)), 2)):
                return 'found', iteration, total_cuts, solver.accum_stats()['conflicts'], encode(adj)
        return 'iteration-limit', max_iterations, total_cuts, solver.accum_stats()['conflicts'], None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('--sample', type=int, default=0, help='number per A edge stratum')
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--solver', default='cadical195')
    parser.add_argument('--iters', type=int, default=30)
    parser.add_argument('--budget', type=int, default=7000, help='conflicts per incremental call, 0 disables')
    args = parser.parse_args()
    params = (6, 6, 2, 4) if args.control else (9, 9, 3, 6)
    strata = defaultdict(list)
    for index, line in enumerate(args.catalogue.read_text().splitlines()):
        seed = decode(line)
        strata[sum(map(int.bit_count, seed)) // 2].append((index, seed))
    results = Counter()
    for edge, rows in sorted(strata.items(), reverse=True):
        sample = rows if not args.sample else [rows[idx * len(rows) // args.sample]
                                               for idx in range(min(len(rows), args.sample))]
        for index, seed in sample:
            start = time.process_time()
            status, iterations, cuts, conflicts, found = search(seed, *params, args.budget, args.iters, args.solver)
            results[status] += 1
            print('row', index, 'e', edge, status, 'iterations', iterations, 'cuts', cuts,
                  'conflicts', conflicts, 'CPU-s', round(time.process_time() - start, 4), flush=True)
            if found:
                print('CONTROL' if args.control else 'UNVERIFIED CANDIDATE', found, flush=True)
    if args.control:
        assert results['found'] > 0
    print('totals', dict(results), flush=True)


if __name__ == '__main__':
    main()
