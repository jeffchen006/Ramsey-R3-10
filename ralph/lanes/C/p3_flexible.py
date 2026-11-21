"""A common fixed-X relaxation for an entire P3 diagonal and edge stratum."""

import argparse
from collections import Counter
from itertools import combinations, product
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

from kernel_projection import bits, decode
from p3_e63 import lex_order, boundary_masks, boundary_keys
from p4_factor_proofs import cpu, digest, run
from path_four_factor import independent_sets
from path_three_top import plant


def parts(degree, overlap, diagonal):
    sizes = (degree - overlap, degree - overlap, diagonal, overlap - diagonal,
             overlap - diagonal, degree - 2 * overlap + diagonal, 1, 1, 1)
    assert min(sizes) >= 0, sizes
    blocks, used = [], 0
    for size in sizes:
        blocks.append(list(range(used, used + size)))
        used += size
    return blocks


def formula_flexible(core, degree, overlap, diagonal, cap, mode, orbit_table=None):
    blocks = parts(degree, overlap, diagonal)
    left, right, common, only_left, only_right, only_middle, [first], [middle], [last] = blocks
    nonroots = first
    order, outside = len(core), last + 1
    fixed = {tuple(sorted((root, vertex))) for root, neighbours in (
        (first, left + common + only_left), (middle, common + only_left + only_right + only_middle),
        (last, right + common + only_right)) for vertex in neighbours}
    eligible = {tuple(sorted(pair)) for a_side, b_side in ((left, right), (left, only_right), (right, only_left),
                                                           (left, only_middle), (right, only_middle))
                for pair in product(a_side, b_side)}
    pool, clauses = IDPool(), CNF()
    outer_edges = {edge: pool.id(('outer', edge)) for edge in sorted(eligible)}
    across = {(inner, outer): pool.id(('across', inner, outer))
              for inner, outer in product(range(order), range(nonroots))}
    pos = [dict() for _ in range(order + outside)]

    def edge(left_vertex, right_vertex, variable):
        pos[left_vertex][right_vertex] = variable
        pos[right_vertex][left_vertex] = variable

    for vertex, mask in enumerate(core):
        for other in bits(mask):
            edge(vertex, other, True)
    for vertex, other in fixed:
        edge(order + vertex, order + other, True)
    for (vertex, other), literal in outer_edges.items():
        edge(order + vertex, order + other, literal)
    for (vertex, other), literal in across.items():
        edge(vertex, order + other, literal)

    def atmost(literals, target):
        literals = list(literals)
        if target < 0:
            clauses.append([])
        elif target == 0:
            clauses.extend([[-literal] for literal in literals])
        elif target < len(literals):
            clauses.extend(CardEnc.atmost(literals, target, vpool=pool, encoding=EncType.seqcounter))

    def exactly(literals, target):
        literals = list(literals)
        atmost(literals, target)
        atmost((-literal for literal in literals), len(literals) - target)

    for adjacent in pos:
        exactly((value for value in adjacent.values() if value is not True),
                degree - sum(value is True for value in adjacent.values()))
    boundary_edges = sum(mask.bit_count() for mask in core) // 2 + degree * outside - (degree * (order + outside)) // 2
    exactly(outer_edges.values(), boundary_edges - len(fixed))

    root_pairs = {(order + first, order + middle), (order + middle, order + last)}
    for start, stop in combinations(range(len(pos)), 2):
        common_literals, common_fixed = [], 0
        for neighbour in sorted(pos[start].keys() & pos[stop].keys()):
            local_left, local_right = pos[start][neighbour], pos[stop][neighbour]
            if local_left is True and local_right is True:
                common_fixed += 1
            elif local_left is True or local_right is True:
                common_literals.append(local_right if local_left is True else local_left)
            else:
                both = pool.id(('wedge', start, neighbour, stop))
                clauses.extend([[-both, local_left], [-both, local_right], [both, -local_left, -local_right]])
                common_literals.append(both)
        adjacent = pos[start].get(stop)
        if adjacent is True:
            if common_fixed:
                clauses.append([])
            atmost(common_literals, 0)
            continue
        cap_pair = cap
        if (start, stop) not in root_pairs and (start >= order + nonroots or stop >= order + nonroots):
            cap_pair -= 1
        atmost(common_literals, cap_pair - common_fixed)
        if adjacent is not None:
            if common_fixed:
                clauses.append([-adjacent])
            clauses.extend([[-adjacent, -literal] for literal in common_literals])
        if not common_fixed:
            clauses.append(common_literals + ([adjacent] if adjacent is not None else []))

    if orbit_table is not None:
        choices = [pool.id(('boundary-choice', index)) for index in range(len(orbit_table))]
        clauses.append(choices)
        for choice, boundary in zip(choices, orbit_table):
            clauses.extend([-choice, literal if boundary[left] >> right & 1 else -literal]
                           for (left, right), literal in outer_edges.items())

    for block in (blocks[:-3] if orbit_table is None else [common]):
        for first_column, second_column in zip(block, block[1:]):
            lex_order(clauses, [across[inner, first_column] for inner in range(order)],
                      [across[inner, second_column] for inner in range(order)])
    if clauses.nv > pool.top:
        pool.occupy(pool.top + 1, clauses.nv)

    neighbourhoods = [list(pos[order + root]) for root in (first, middle, last)]
    for inner, group in product(range(order), neighbourhoods):
        clauses.append([across[inner, outer - order] for outer in group])

    cut = 4
    groups = []
    for group in combinations(range(outside), cut):
        pairs = list(combinations(group, 2))
        if any(pair in fixed for pair in pairs):
            continue
        guards = [outer_edges[pair] for pair in pairs if pair in outer_edges]
        if guards and mode == 'universal':
            continue
        groups.append((tuple(outer for outer in group if outer < nonroots), guards))
    for independent in independent_sets(core, (1 << order) - 1):
        if independent.bit_count() != degree - 3:
            continue
        available = [pool.id(('available', independent, outer)) for outer in range(nonroots)]
        for outer, literal in enumerate(available):
            clauses.append([literal, *(across[inner, outer] for inner in bits(independent))])
        clauses.extend([*guards, *(-available[outer] for outer in group)] for group, guards in groups)
    return clauses, across, outer_edges


def marked_control():
    core, boundary, known = plant()
    classify = {(True, False, False): 0, (False, False, True): 1, (True, True, True): 2,
                (True, True, False): 3, (False, True, True): 4, (False, True, False): 5}
    order = len(core)
    groups = [[] for _ in range(9)]
    for vertex in range(len(boundary) - 3):
        membership = tuple(bool(boundary[vertex] >> root & 1) for root in range(len(boundary) - 3, len(boundary)))
        groups[classify[membership]].append(vertex)
    for index in range(3):
        groups[6 + index] = [len(boundary) - 3 + index]
    mapping = [vertex for group in groups for vertex in sorted(group, key=lambda outer:
               tuple((known[inner] >> (order + outer)) & 1 for inner in range(order)))]
    for mode in ('universal', 'guarded'):
        clauses, across, outer_edges = formula_flexible(core, 6, 4, 2, 5, mode)
        edges = [value if known[inner] >> (order + mapping[outer]) & 1 else -value
                 for (inner, outer), value in across.items()]
        edges.extend(value if boundary[mapping[left]] >> mapping[right] & 1 else -value
                     for (left, right), value in outer_edges.items())
        with Solver(name='cadical195', bootstrap_with=clauses.clauses) as solver:
            assert solver.solve(assumptions=edges)
            edges[0] *= -1
            assert not solver.solve(assumptions=edges)
        print('CONTROL C21', mode, 'planted partition and boundary accepted; one-edge corruption rejected')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('bin', type=Path)
    parser.add_argument('work', type=Path)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--mode', choices=['universal', 'guarded'], default='guarded')
    parser.add_argument('--diagonal', type=int, choices=(3, 4, 5), default=5)
    parser.add_argument('--row', type=int, action='append')
    parser.add_argument('--edges', type=int, action='append')
    parser.add_argument('--skip-row', type=int, action='append', default=[])
    parser.add_argument('--shards', type=int, default=1)
    parser.add_argument('--shard', type=int, default=0)
    parser.add_argument('--pin-e63', type=int)
    parser.add_argument('--seconds', type=int, default=50)
    parser.add_argument('--produce', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.control:
        marked_control()
        return
    rows = args.catalogue.read_text().splitlines()
    assert (args.row or args.edges) and not (args.produce and args.verify)
    assert 0 <= args.shard < args.shards
    selected_rows = [(index, decode(line)) for index, line in enumerate(rows)
                     if index % args.shards == args.shard and index not in args.skip_row
                     and (not args.row or index in args.row)]
    selected_rows = [(index, core, sum(mask.bit_count() for mask in core) // 2) for index, core in selected_rows]
    selected_rows = [(index, core, size) for index, core, size in selected_rows if not args.edges or size in args.edges]
    assert selected_rows
    args.work.mkdir(parents=True, exist_ok=True)
    temporary = args.work / f'{args.diagonal}-{args.mode}-{selected_rows[0][0]}-tmp.cnf'
    counts = Counter()
    start = cpu()
    for index, core, row_edges in selected_rows:
        begin = cpu()
        cnf, _, outer = formula_flexible(core, 9, 6, args.diagonal, 6, args.mode)
        if args.pin_e63 is not None:
            assert args.diagonal == 5
            boundary = boundary_masks(boundary_keys()[args.pin_e63])
            cnf.extend([literal if boundary[left] >> right & 1 else -literal]
                       for (left, right), literal in outer.items())
        cnf.to_file(temporary)
        print('generated', args.diagonal, args.mode, index, row_edges, cnf.nv, len(cnf.clauses),
              'CPU-s', round(cpu() - begin, 4), flush=True)
        del cnf
        proof = args.work / f'{args.diagonal}-{args.mode}-{index:03d}.lrat'
        if args.produce and proof.exists():
            raise FileExistsError(proof)
        status = None
        if not args.verify:
            solved = run(args.bin / 'cadical', ['-q', '--lrat', temporary, proof] if args.produce
                         else ['-q', temporary], args.seconds)
            if solved.returncode == 124:
                status = 'wall-cap'
            elif solved.returncode == 10:
                status = 'relaxation-sat'
            elif solved.returncode != 20 or 's UNSATISFIABLE' not in solved.stdout.splitlines():
                raise RuntimeError((index, solved.returncode, solved.stdout))
            if status is not None and args.produce:
                proof.unlink(missing_ok=True)
        if status is None:
            status = 'enum'
            if args.produce or args.verify:
                checked = run(args.bin / 'cake_lpr', [temporary, proof], 180)
                if checked.returncode != 0 or 's VERIFIED UNSAT' not in checked.stdout.splitlines():
                    raise RuntimeError((index, checked.returncode, checked.stdout))
                status = 'checked'
                print('bound', index, digest(temporary), digest(proof), proof.stat().st_size, flush=True)
        counts[status] += 1
        print('row', index, status, 'CPU-s', round(cpu() - begin, 4), flush=True)
    temporary.unlink(missing_ok=True)
    print('TERMINAL', args.diagonal, args.mode, dict(counts), 'CPU-s', round(cpu() - start, 4), flush=True)


if __name__ == '__main__':
    main()
