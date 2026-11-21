"""Equality windows for the isolated-pair e80 plus degree-three anchor."""

import argparse
from collections import Counter
from itertools import combinations, product
from pathlib import Path

from pysat.solvers import Solver

from kernel_projection import bits, decode
from p3_e63 import lex_order, twin_groups
from p3_minimal import formula_minimal
from p3_round4_index import has_independent
from p4_factor_proofs import cpu, digest, run
from pair_packages import restrict
from path_three_top import connect


def build_boundary(wing_size, cap, split, parts=None):
    widths = [wing_size, wing_size, cap - 2, 2, wing_size, 1, 1, 1]
    if parts is None:
        parts, offset = [], 0
        for width in widths:
            parts.append(list(range(offset, offset + width)))
            offset += width
    assert list(map(len, parts)) == widths
    left, right, used, unused, neighbours, [first], [second], [anchor] = parts
    assert 0 <= split <= len(neighbours)
    boundary = [0] * sum(widths)
    for root, group in ((first, left + used + unused), (second, right + used + unused),
                        (anchor, [left[0], right[0], *used, *neighbours])):
        for vertex in group:
            connect(boundary, root, vertex)
    for left_vertex, right_vertex in product(left, right):
        if (left_vertex, right_vertex) != (left[0], right[0]):
            connect(boundary, left_vertex, right_vertex)
    for index, vertex in enumerate(neighbours):
        for other in unused + (left[1:] if index < split else right[1:]):
            connect(boundary, vertex, other)
    return boundary


def formula(core, boundary, degree, cap):
    clauses, edges = formula_minimal(core, boundary, degree, cap, degree - 3, False,
                                     uncapped_roots=(len(boundary) - 1,))
    for group in twin_groups(boundary):
        for left, right in zip(group, group[1:]):
            lex_order(clauses, [edges[inner, left] for inner in range(len(core))],
                      [edges[inner, right] for inner in range(len(core))])
    return clauses, edges


def controls(path, observer=None):
    lines = path.read_text().splitlines()
    assert len(set(lines)) == len(lines) == 331
    totals = Counter()
    for index, line in enumerate(lines):
        graph = decode(line)
        order, degree = len(graph), 6
        all_vertices = (1 << order) - 1
        assert order == 21 and all(mask.bit_count() == degree for mask in graph)
        assert not has_independent(graph, all_vertices, degree + 1)
        pair_sets = {(left, right): graph[left] & graph[right] for left, right in combinations(range(order), 2)}
        assert all(not common for (left, right), common in pair_sets.items() if graph[left] >> right & 1)
        maximal = all(common or graph[left] >> right & 1 for (left, right), common in pair_sets.items())
        cap = max(mask.bit_count() for mask in pair_sets.values())
        partners = Counter(vertex for pair, common in pair_sets.items() if common.bit_count() == cap for vertex in pair)
        for (first, second), shared in pair_sets.items():
            if shared.bit_count() != cap or partners[first] != 1 or partners[second] != 1 or cap != 4:
                continue
            left, right = graph[first] ^ shared, graph[second] ^ shared
            holes = [(one, two) for one, two in product(bits(left), bits(right)) if not graph[one] >> two & 1]
            if len(holes) != 1:
                continue
            low_left, low_right = holes[0]
            residue = all_vertices & ~(graph[first] | graph[second] | 1 << first | 1 << second)
            for anchor in bits(residue):
                wing_size = degree - cap
                nearby = graph[anchor] & residue
                if nearby.bit_count() != wing_size:
                    continue
                totals['degree anchor'] += 1
                assert graph[anchor] >> low_left & graph[anchor] >> low_right & 1
                used, unused = shared & graph[anchor], shared & ~graph[anchor]
                assert used.bit_count() == cap - 2 and unused.bit_count() == 2
                inner = list(bits(residue & ~(1 << anchor | nearby)))
                assert len(inner) == 8
                core = restrict(graph, inner)
                degrees = [(graph[vertex] & residue).bit_count() for vertex in bits(nearby)]
                assert min(degrees) >= cap - 1
                before = sum((graph[vertex] & residue).bit_count() for vertex in bits(residue)) // 2
                after = sum(mask.bit_count() for mask in core) // 2
                assert before - after == sum(degrees)
                if observer is not None:
                    observer(graph, list(bits(unused)), list(bits(left ^ (1 << low_left))),
                             list(bits(right ^ (1 << low_right))), list(bits(nearby)), before, after)
                if any(value != cap - 1 for value in degrees):
                    continue
                totals['equality'] += 1
                y_order = [low_left, *bits(left ^ (1 << low_left))]
                z_order = [low_right, *bits(right ^ (1 << low_right))]
                a_type = [vertex for vertex in bits(nearby) if graph[vertex] & left]
                b_type = [vertex for vertex in bits(nearby) if graph[vertex] & right]
                assert len(a_type) + len(b_type) == wing_size
                ordered = y_order + z_order + [*bits(used), *bits(unused), *a_type, *b_type, first, second, anchor]
                outside = build_boundary(wing_size, cap, len(a_type))
                assert outside == restrict(graph, ordered)
                if not maximal:
                    continue
                for group in twin_groups(outside):
                    profile = sorted((ordered[outer] for outer in group), key=lambda vertex:
                                     tuple(int(graph[source] >> vertex & 1) for source in inner))
                    for outer, vertex in zip(group, profile):
                        ordered[outer] = vertex
                clauses, variables = formula(core, outside, degree, cap)
                assignment = [var if graph[inner[vertex]] >> ordered[outer] & 1 else -var
                              for (vertex, outer), var in variables.items()]
                with Solver(name='cadical195', bootstrap_with=clauses.clauses) as solver:
                    assert solver.solve(assumptions=assignment), (index, first, second, anchor)
                    assignment[0] *= -1
                    assert not solver.solve(assumptions=assignment)
                totals['SAT control + corruption'] += 1
    assert totals['degree anchor'] == 444 and totals['equality'] == 23
    assert totals['SAT control + corruption'] > 0
    print('PASS C21 regular complete control', dict(totals), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('census', type=Path)
    parser.add_argument('bin', type=Path)
    parser.add_argument('work', type=Path)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--split', type=int, choices=[0, 1])
    parser.add_argument('--row', type=int, action='append')
    parser.add_argument('--skip-row', type=int, action='append', default=[])
    parser.add_argument('--seconds', type=int, default=45)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.control:
        controls(args.census)
        return
    assert args.split is not None
    boundary = build_boundary(3, 6, args.split)
    rows = [(index, decode(line)) for index, line in enumerate(args.census.read_text().splitlines())]
    rows = [(index, core) for index, core in rows if sum(mask.bit_count() for mask in core) == 130]
    assert len(rows) == 25
    args.work.mkdir(exist_ok=True)
    temporary = args.work / f'p2anchor-{args.split}-tmp.cnf'
    counts = Counter()
    start = cpu()
    for row, core in rows:
        if row in args.skip_row or (args.row and row not in args.row):
            continue
        begin = cpu()
        proof = args.work / f'p2anchor-{args.split}-{row}.lrat'
        clauses, _ = formula(core, boundary, 9, 6)
        clauses.to_file(temporary)
        status = None
        if not args.verify:
            if proof.exists():
                raise FileExistsError(proof)
            solved = run(args.bin / 'cadical', ['-q', '--lrat', temporary, proof], args.seconds)
            if solved.returncode == 124:
                status = 'wall-cap'
            elif solved.returncode == 10:
                status = 'relaxation-sat'
            elif solved.returncode != 20 or 's UNSATISFIABLE' not in solved.stdout.splitlines():
                raise RuntimeError((row, solved.returncode, solved.stdout))
            if status:
                proof.unlink(missing_ok=True)
        if status is None:
            checked = run(args.bin / 'cake_lpr', [temporary, proof], 150)
            assert checked.returncode == 0 and 's VERIFIED UNSAT' in checked.stdout.splitlines(), checked.stdout
            status = 'checked'
            print('bound', row, digest(temporary), digest(proof), proof.stat().st_size, flush=True)
        counts[status] += 1
        print('row', row, status, 'CPU-s', round(cpu() - begin, 4), flush=True)
    temporary.unlink(missing_ok=True)
    print('TERMINAL', args.split, dict(counts), 'CPU-s', round(cpu() - start, 4), flush=True)


if __name__ == '__main__':
    main()
