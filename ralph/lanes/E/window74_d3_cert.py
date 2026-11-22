#!/usr/bin/env python3
"""Independent SAT relaxation and checker for the degree-three window cut."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path
import subprocess

from involution_sat import from_graph6


LANE = Path(__file__).resolve().parent
TOOLS = LANE.parents[2] / 'opt/bin'


def formula(rows, alpha, limit):
    order = len(rows)
    inputs = tuple(range(1, 3 * order + 1))
    clauses = []

    def variable(group, vertex):
        return 1 + group * order + vertex

    for left, right in combinations(range(order), 2):
        if rows[left] >> right & 1:
            clauses.extend((-variable(group, left), -variable(group, right)) for group in range(3))
    for subset in combinations(range(order), alpha - 1):
        if not any(rows[left] >> right & 1 for left, right in combinations(subset, 2)):
            for pair in combinations(range(3), 2):
                clauses.append(tuple(variable(group, vertex) for group in pair for vertex in subset))
    serial = len(inputs)
    previous = []
    for value in inputs:
        height = min(limit + 1, len(previous) + 1)
        current = tuple(range(serial + 1, serial + height + 1))
        serial += height
        clauses.append((-value, current[0]))
        clauses.extend((-old, new) for old, new in zip(previous, current))
        clauses.extend((-value, -old, new) for old, new in zip(previous, current[1:]))
        previous = current
    clauses.append((-previous[limit],))
    return (f'p cnf {serial} {len(clauses)}\n' +
            ''.join(' '.join(map(str, (*row, 0))) + '\n' for row in clauses)).encode('ascii')


def call(tool, wall, cpu, log, *args):
    with log.open('x', encoding='ascii') as out:
        return subprocess.run(['nice', '-n', '5', 'timeout', '-k', '2s', str(wall), 'bash',
                               str(LANE/'limited.sh'), str(cpu), str(TOOLS/tool), *map(str, args)],
                              stdout=out, stderr=subprocess.STDOUT).returncode


def check(cnf, proof, log):
    assert call('cake_lpr', 15, 6, log, cnf, proof) == 0
    assert 's VERIFIED UNSAT' in log.read_text(encoding='ascii').splitlines()


def solve(cnf, proof, log):
    return call('cadical', 20, 8, log, '-q', '--lrat', cnf, proof)


def calibrate(catalogue, folder):
    folder.mkdir()
    counts = Counter()
    for index, key in enumerate(catalogue.read_text(encoding='ascii').splitlines()):
        rows = tuple(from_graph6(key))
        for root, neighbors in enumerate(rows):
            if neighbors.bit_count() != 3:
                continue
            vertices = tuple(vertex for vertex in range(len(rows)) if vertex != root and not neighbors >> vertex & 1)
            core = tuple(sum(1 << mapped for mapped, right in enumerate(vertices) if rows[left] >> right & 1)
                         for left in vertices)
            budget = (sum(map(int.bit_count, rows)) - sum(map(int.bit_count, core))) // 2 - 3
            for maximum in (0, budget):
                prefix = folder / f'{index}_{root}_{maximum}'
                cnf, proof = prefix.with_suffix('.cnf'), prefix.with_suffix('.lrat')
                cnf.write_bytes(formula(core, 3, maximum))
                code = solve(cnf, proof, prefix.with_suffix('.solve.log'))
                assert budget > 0 and code == (20 if maximum == 0 else 10)
                if code == 20:
                    check(cnf, proof, prefix.with_suffix('.lrat.log'))
                    counts['negative'] += 1
                else:
                    counts['positive'] += 1
    assert counts['positive'] == counts['negative'] >= 3
    print('order-8 certificate controls', dict(counts), flush=True)


def census(catalogue, folder, indices, process, offset, stride):
    parents = catalogue.read_text(encoding='ascii').splitlines()
    assert len(parents) == len(set(parents)) == 191 and 0 <= offset < stride
    if process == 'produce':
        folder.mkdir(exist_ok=True)
    else:
        assert set(folder.glob('*.lrat')) == {folder / f'{index:03d}.lrat' for index in range(191)}
        assert set(folder.glob('*.cnf')) == {folder / f'{index:03d}.cnf' for index in range(191)}
    selected = (range(len(parents)) if indices is None else indices)[offset::stride]
    for index in selected:
        key = parents[index]
        rows = tuple(from_graph6(key))
        assert len(rows) == 22
        edges = sum(map(int.bit_count, rows)) // 2
        contents = formula(rows, 7, 71 - edges)
        prefix = folder / f'{index:03d}'
        cnf, proof = prefix.with_suffix('.cnf'), prefix.with_suffix('.lrat')
        if process == 'produce':
            with cnf.open('xb') as out:
                out.write(contents)
            code = solve(cnf, proof, prefix.with_suffix('.solve.log'))
            assert code == 20, (index, code)
            check(cnf, proof, prefix.with_suffix('.lrat.log'))
        else:
            assert cnf.read_bytes() == contents, index
            check(cnf, proof, prefix.with_suffix('.replay.log'))
        print(index, key, 'edges', edges, 'CHECKED', flush=True)
    print(process, 'checked', len(selected), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('process', choices=('calibrate', 'produce', 'replay'))
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('folder', type=Path)
    parser.add_argument('--indices', type=int, nargs='+')
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--stride', type=int, default=1)
    args = parser.parse_args()
    if args.process == 'calibrate':
        calibrate(args.catalogue, args.folder)
    else:
        census(args.catalogue, args.folder, args.indices, args.process, args.offset, args.stride)
