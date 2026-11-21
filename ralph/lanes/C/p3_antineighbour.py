"""Small CNFs for vertices of X anticomplete to the triple intersection."""

import argparse
from collections import Counter
from itertools import combinations, product
from pathlib import Path

from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

from kernel_projection import bits
from p3_high_f import classify, filter_target, layouts
from p4_factor_proofs import cpu, digest, run
from path_four_factor import independent_sets
from path_three_top import plant


def formula(boundary, degree, deficit):
    size = len(boundary)
    common = boundary[-3] & boundary[-2] & boundary[-1]
    eligible = list(bits(((1 << (size - 3)) - 1) & ~common))
    pool = IDPool()
    cnf = CNF()
    cross = {(vertex, outer): pool.id(('cross', vertex, outer))
             for vertex, outer in product(range(deficit), eligible)}
    within = {(first, second): pool.id(('within', first, second))
              for first, second in combinations(range(deficit), 2)}
    for first, second in combinations(eligible, 2):
        if boundary[first] >> second & 1:
            cnf.extend([[-cross[vertex, first], -cross[vertex, second]] for vertex in range(deficit)])
    for (first, second), edge in within.items():
        cnf.extend([[-edge, -cross[first, outer], -cross[second, outer]] for outer in eligible])
    for first, second, third in combinations(range(deficit), 3):
        cnf.append([-within[first, second], -within[first, third], -within[second, third]])
    for independent in independent_sets(boundary, (1 << size) - 1):
        require = degree + 1 - independent.bit_count()
        if not 0 <= require <= deficit:
            continue
        for chosen in combinations(range(deficit), require):
            cnf.append([within[pair] for pair in combinations(chosen, 2)] +
                       [cross[vertex, outer] for vertex in chosen for outer in eligible if independent >> outer & 1])
    return cnf, cross, within


def control():
    core, boundary, known = plant()
    order = len(core)
    common = (boundary[-3] & boundary[-2] & boundary[-1]) << order
    deficit = max(0, order - common.bit_count() * (6 - 3))
    eligible = [vertex for vertex in range(order) if not known[vertex] & common]
    assert len(eligible) >= deficit > 0
    cnf, cross, within = formula(boundary, 6, deficit)
    positive = {edge: bool(known[eligible[vertex]] >> (order + outer) & 1)
                for (vertex, outer), edge in cross.items()}
    positive.update({edge: bool(known[eligible[first]] >> eligible[second] & 1)
                     for (first, second), edge in within.items()})
    assignments = [edge if selected else -edge for edge, selected in positive.items()]
    with Solver(name='cadical195', bootstrap_with=cnf.clauses) as solver:
        assert solver.solve(assumptions=assignments)
        assert not solver.solve(assumptions=[-edge for edge in positive])
    print('PASS C21 actual antineighbours', len(eligible), 'required', deficit, 'and empty attachment corruption')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bin', type=Path)
    parser.add_argument('work', type=Path)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--layout', type=int, action='append')
    args = parser.parse_args()
    if args.control:
        control()
        return
    args.work.mkdir(exist_ok=True)
    counts = Counter()
    for index, (size, key) in enumerate(layouts(9, 6, 3, 8, 16, 18)):
        if args.layout and index not in args.layout:
            continue
        boundary = classify(9, 6, 3, key)
        if filter_target(boundary) != 'pass':
            continue
        begin = cpu()
        cnf, _, _ = formula(boundary, 9, 4)
        cnf_path = args.work / f'{index}.cnf'
        proof = args.work / f'{index}.lrat'
        cnf.to_file(cnf_path)
        if not args.verify:
            assert not proof.exists()
            solved = run(args.bin / 'cadical', ['-q', '--lrat', cnf_path, proof], 10)
            if solved.returncode != 20:
                status = {10: 'relaxation-sat', 124: 'wall-cap'}[solved.returncode]
                proof.unlink(missing_ok=True)
                counts[status] += 1
                print('row', index, size + 45, status, key, 'CPU-s', round(cpu() - begin, 4), flush=True)
                continue
        checked = run(args.bin / 'cake_lpr', [cnf_path, proof], 30)
        assert checked.returncode == 0 and 's VERIFIED UNSAT' in checked.stdout.splitlines()
        counts['checked'] += 1
        print('row', index, size + 45, 'checked', key, 'CPU-s', round(cpu() - begin, 4), flush=True)
        print('bound', index, digest(cnf_path), digest(proof), proof.stat().st_size, flush=True)
    print('TERMINAL', dict(counts), flush=True)


if __name__ == '__main__':
    main()
