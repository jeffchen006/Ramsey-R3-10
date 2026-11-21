"""Exact attachment formula for the fixed P3 diagonal-five boundaries."""

import argparse
from itertools import combinations, product
from pathlib import Path
import time

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

from kernel_projection import bits, decode, encode
from pair_packages import restrict
from path_four_factor import independent_sets


def connect(graph, left, right):
    graph[left] |= 1 << right
    graph[right] |= 1 << left


def boundary(edge_count):
    result = [0] * 18
    first, middle, last = 15, 16, 17
    left_wing, right_wing = range(3), range(3, 6)
    both, left_only, right_only = range(6, 11), 11, 12
    middle_left, middle_right = 13, 14
    for root, neighbours in ((first, [*left_wing, *both, left_only]),
                             (middle, range(6, 15)), (last, [*right_wing, *both, right_only])):
        for other in neighbours:
            connect(result, root, other)
    for left, right in product(left_wing, right_wing):
        if edge_count == 66 or left == 2 or right == 5:
            connect(result, left, right)
    for vertex in left_wing:
        connect(result, vertex, right_only)
        if edge_count == 66 or vertex != 2:
            connect(result, vertex, middle_left)
        if edge_count == 64 and vertex != 2:
            connect(result, vertex, middle_right)
    for vertex in right_wing:
        connect(result, vertex, left_only)
        if edge_count == 66 or vertex != 5:
            connect(result, vertex, middle_right)
        if edge_count == 64 and vertex != 5:
            connect(result, vertex, middle_left)
    return result


def plant():
    control = [sum(1 << ((index + step) % 21) for step in (-6, -4, -1, 1, 4, 6))
               for index in range(21)]
    roots = [0, 5, 10]
    neighbourhood = control[0] | control[5] | control[10]
    core = list(bits(((1 << 21) - 1) & ~neighbourhood & ~sum(1 << vertex for vertex in roots)))
    outer = [*bits(neighbourhood), *roots]
    return restrict(control, core), restrict(control, outer), restrict(control, core + outer)


def formula(core, boundary_adj, degree, cap):
    order, outside = len(core), len(boundary_adj)
    nonroots = outside - 3
    clauses = CNF()
    pool = IDPool()
    attachments = {(inner, outer): pool.id(('edge', inner, outer))
                   for inner, outer in product(range(order), range(nonroots))}

    def atmost(literals, target):
        literals = list(literals)
        if target < 0:
            clauses.append([])
        elif target < len(literals):
            clauses.extend(CardEnc.atmost(literals, target, vpool=pool, encoding=EncType.seqcounter))

    def exactly(literals, target):
        literals = list(literals)
        atmost(literals, target)
        atmost((-literal for literal in literals), len(literals) - target)

    def capped_common(adj, positions, count, side):
        for left, right in combinations(range(len(adj)), 2):
            common = (adj[left] & adj[right]).bit_count()
            if adj[left] >> right & 1:
                if common:
                    clauses.append([])
                for first, second in positions(left, right):
                    clauses.append([-first, -second])
                continue
            limits = []
            for first, second in positions(left, right):
                selector = pool.id((side, first, second))
                clauses.extend([[-selector, first], [-selector, second], [selector, -first, -second]])
                limits.append(selector)
            atmost(limits, count - common)
            if not common:
                clauses.append(limits)

    for inner, neighbours in enumerate(core):
        exactly((attachments[inner, outer] for outer in range(nonroots)), degree - neighbours.bit_count())
    for outer, neighbours in enumerate(boundary_adj):
        exactly((attachments[inner, outer] for inner in range(order) if outer < nonroots),
                degree - neighbours.bit_count())

    def across_outside(left, right):
        return ((attachments[left, outer], attachments[right, outer]) for outer in range(nonroots))

    def across_core(left, right):
        if right >= nonroots:
            return ()
        return ((attachments[inner, left], attachments[inner, right]) for inner in range(order))

    capped_common(core, across_outside, cap, 'from-outside')
    capped_common(boundary_adj, across_core, cap, 'from-core')
    for inner, outer in product(range(order), range(outside)):
        cross = [attachments[inner, neighbour] for neighbour in bits(boundary_adj[outer])
                 if neighbour < nonroots]
        if outer < nonroots:
            cross.extend(attachments[neighbour, outer] for neighbour in bits(core[inner]))
        atmost(cross, cap)
        direct = attachments.get((inner, outer))
        clauses.append(cross + ([direct] if direct else []))

    maximals = []
    for group in independent_sets(boundary_adj, (1 << outside) - 1):
        dominated = group
        for outer in bits(group):
            dominated |= boundary_adj[outer]
        if dominated.bit_count() == outside:
            maximals.append((tuple(outer for outer in bits(group) if outer < nonroots),
                             (group >> nonroots).bit_count()))
    for independent in independent_sets(core, (1 << order) - 1):
        max_available = degree - independent.bit_count()
        if all(max_available >= len(group) + roots for group, roots in maximals):
            continue
        choices = {}
        for group, roots in maximals:
            if max_available >= len(group) + roots:
                continue
            if not independent:
                clauses.append([])
                continue
            for outer in group:
                if outer in choices:
                    continue
                edges = [attachments[inner, outer] for inner in bits(independent)]
                if len(edges) == 1:
                    choices[outer] = -edges[0]
                else:
                    selector = pool.id(('available', independent, outer))
                    clauses.append([selector, *edges])
                    choices[outer] = selector
            atmost((choices[outer] for outer in group), max_available - roots)
    return clauses, attachments


def recover(core, boundary_adj, chosen):
    order = len(core)
    result = list(core) + [neighbours << order for neighbours in boundary_adj]
    for inner, outer in chosen:
        connect(result, inner, order + outer)
    return result


def calibrate():
    core, boundary_adj, known = plant()
    clauses, attachments = formula(core, boundary_adj, 6, 4)
    assignment = [variable if known[inner] >> (len(core) + outer) & 1 else -variable
                  for (inner, outer), variable in attachments.items()]
    with Solver(name='cadical195', bootstrap_with=clauses.clauses) as solver:
        assert solver.solve(assumptions=assignment)
        corrupted = assignment.copy()
        corrupted[0] *= -1
        assert not solver.solve(assumptions=corrupted)
    print('C21: planted exact completion accepted, one-edge corruption rejected', flush=True)
    print('CONTROL', encode(known), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--sample', type=int, default=0)
    parser.add_argument('--id', type=int, action='append')
    parser.add_argument('--cnf-dir', type=Path)
    parser.add_argument('--budget', type=int, default=20000)
    parser.add_argument('--edges', type=int, choices=[64, 66], default=66)
    args = parser.parse_args()
    if args.control:
        calibrate()
        return
    boundary_adj = boundary(args.edges)
    rows = [(index, decode(line)) for index, line in enumerate(args.catalogue.read_text().splitlines())]
    rows = [(index, core) for index, core in rows if sum(map(int.bit_count, core)) == 2 * args.edges]
    assert len(rows) == {64: 59, 66: 10}[args.edges]
    if args.id:
        rows = [(index, core) for index, core in rows if index in args.id]
    elif args.sample:
        rows = [rows[slot * len(rows) // args.sample] for slot in range(args.sample)]
    for index, core in rows:
        start = time.process_time()
        clauses, attachments = formula(core, boundary_adj, 9, 6)
        print('row', index, 'generated', clauses.nv, len(clauses.clauses), 'CPU-s',
              round(time.process_time() - start, 4), flush=True)
        if args.cnf_dir:
            clauses.to_file(args.cnf_dir / f'{index}.cnf')
            continue
        with Solver(name='cadical195', bootstrap_with=clauses.clauses) as solver:
            solver.conf_budget(args.budget)
            answer = solver.solve_limited()
            print('row', index, 'answer', answer, 'conflicts', solver.accum_stats()['conflicts'],
                  'CPU-s', round(time.process_time() - start, 4), flush=True)
            if answer:
                model = set(solver.get_model())
                print('UNVERIFIED CANDIDATE', encode(recover(core, boundary_adj, (edge for edge, variable
                                                       in attachments.items() if variable in model))), flush=True)


if __name__ == '__main__':
    main()
