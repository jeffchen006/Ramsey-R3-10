"""Bounded fixed- and table-boundary pilots for lower diagonal-five strata."""

import argparse
import ast
from collections import Counter
from pathlib import Path

from pysat.solvers import Solver

from kernel_projection import decode
from p3_e63 import boundary_masks, make_formula
from p3_flexible import formula_flexible, marked_control
from p4_factor_proofs import cpu, digest, run
from path_three_top import plant


def control():
    marked_control()
    core, boundary, known = plant()
    memberships = ((True, False, False), (False, False, True), (True, True, True),
                   (True, True, False), (False, True, True), (False, True, False))
    groups = [[] for _ in memberships]
    for vertex in range(len(boundary) - 3):
        membership = tuple(bool(boundary[vertex] >> root & 1) for root in range(len(boundary) - 3, len(boundary)))
        groups[memberships.index(membership)].append(vertex)
    groups[2].sort(key=lambda outer: tuple(known[inner] >> (len(core) + outer) & 1 for inner in range(len(core))))
    permutation = [vertex for group in groups for vertex in group] + list(range(len(boundary) - 3, len(boundary)))
    relabelled = [sum(1 << target for target, source in enumerate(permutation) if boundary[original] >> source & 1)
                  for original in permutation]
    cnf, across, _ = formula_flexible(core, 6, 4, 2, 5, 'guarded', orbit_table=[relabelled])
    assignment = [var if known[inner] >> (len(core) + permutation[outer]) & 1 else -var
                  for (inner, outer), var in across.items()]
    with Solver(name='cadical195', bootstrap_with=cnf.clauses) as solver:
        assert solver.solve(assumptions=assignment)
        assignment[0] *= -1
        assert not solver.solve(assumptions=assignment)
    print('CONTROL C21 table-boundary positive and corruption check', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('boundaries', type=Path)
    parser.add_argument('bin', type=Path)
    parser.add_argument('work', type=Path)
    parser.add_argument('--mode', choices=['fixed', 'table'], default='fixed')
    parser.add_argument('--seconds', type=int, default=30)
    parser.add_argument('--row', type=int, required=False)
    parser.add_argument('--layout', type=int, nargs='+')
    parser.add_argument('--skip-layout', type=int, nargs='+', default=[])
    parser.add_argument('--wing', type=int)
    parser.add_argument('--prove', action='store_true')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--control', action='store_true')
    args = parser.parse_args()
    if args.control:
        control()
        return
    assert args.row is not None and not (args.prove and args.verify)
    source = args.catalogue.read_text().splitlines()[args.row]
    row = decode(source)
    size = sum(mask.bit_count() for mask in row) // 2
    layouts = {}
    for line in args.boundaries.read_text().splitlines():
        if not line.startswith('key '):
            continue
        _, edges, index, result, key = line.split(' ', 4)
        if int(edges) == size and result == 'pass':
            key = ast.literal_eval(key)
            if args.wing is None or key[0] == args.wing:
                layouts[int(index)] = boundary_masks(key)
    assert layouts
    selected = [index for index in (args.layout if args.layout else sorted(layouts)) if index not in args.skip_layout]
    assert all(index in layouts for index in selected)
    args.work.mkdir(exist_ok=True)
    cases = [selected] if args.mode == 'table' else [[index] for index in selected]
    counts = Counter()
    start = cpu()
    for case in cases:
        caseid = f'{args.row}-{args.mode}-{case[0]}-{len(case)}'
        path = args.work / f'{caseid}.cnf'
        proof = args.work / f'{caseid}.lrat'
        if args.prove and proof.exists():
            raise FileExistsError(proof)
        begin = cpu()
        if args.mode == 'table':
            clauses, _, _ = formula_flexible(row, 9, 6, 5, 6, 'guarded',
                                             orbit_table=[layouts[index] for index in case])
        else:
            clauses, _ = make_formula(row, layouts[case[0]], 9, 6, 'lite6')
        clauses.to_file(path)
        print('generated', caseid, 'e', size, 'keys', ','.join(map(str, case)),
              clauses.nv, len(clauses.clauses), 'CPU-s', round(cpu() - begin, 4), flush=True)
        del clauses
        status = None
        if not args.verify:
            solved = run(args.bin / 'cadical', ['-q', '--lrat', path, proof] if args.prove else ['-q', path], args.seconds)
            if solved.returncode == 124:
                status = 'wall-cap'
            elif solved.returncode == 10:
                status = 'relaxation-sat'
            elif solved.returncode != 20 or 's UNSATISFIABLE' not in solved.stdout.splitlines():
                raise RuntimeError((caseid, solved.returncode, solved.stdout))
        if status is None:
            status = 'enum'
            if args.prove or args.verify:
                checked = run(args.bin / 'cake_lpr', [path, proof], 165)
                assert checked.returncode == 0 and 's VERIFIED UNSAT' in checked.stdout.splitlines(), checked.stdout
                status = 'checked'
                print('bound', caseid, digest(path), digest(proof), proof.stat().st_size, flush=True)
        if status in {'wall-cap', 'relaxation-sat'} and args.prove:
            proof.unlink(missing_ok=True)
        counts[status] += 1
        print('row', caseid, status, 'CPU-s', round(cpu() - begin, 4), flush=True)
        path.unlink()
    print('TERMINAL', args.row, args.mode, dict(counts), 'CPU-s', round(cpu() - start, 4), flush=True)


if __name__ == '__main__':
    main()
