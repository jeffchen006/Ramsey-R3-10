#!/usr/bin/env python3
"""Test that each mode extends pinned known Ramsey graphs rooted at a minimum edge."""

from itertools import combinations
from pathlib import Path
import subprocess

from kernel_cnf import Cnf, MODES, ROOT, decode, write


def graph6(n, edges):
    bits = [int((left, right) in edges) for right in range(n) for left in range(right)]
    bits += [0] * (-len(bits) % 6)
    return chr(n + 63) + ''.join(chr(63 + sum(bit << shift for bit, shift in zip(bits[idx:idx + 6], range(5, -1, -1))))
                                 for idx in range(0, len(bits), 6))


def root_graph(n, edges, degree):
    neighbors = [{right if left == vertex else left for left, right in edges if vertex in (left, right)}
                 for vertex in range(n)]

    def rooted(left, right):
        a = sorted(neighbors[left] - {right})
        b = sorted(neighbors[right] - {left})
        return sum(tuple(sorted((i, j))) in edges for i in a for j in b), [left, right] + a + b

    _, first = min(rooted(left, right) for left, right in edges)
    order = first + sorted(set(range(n)) - set(first))
    relabeled = {(left, right) for left, right in combinations(range(n), 2)
                 if tuple(sorted((order[left], order[right]))) in edges}
    kernel = {(left - 2, right - 2) for left, right in relabeled if 2 <= left <= degree < right < 2 * degree}
    return relabeled, graph6(2 * degree - 2, kernel)


def test(cases):
    total = 0
    for name, n, degree, maximum, original in cases:
        relabeled, kernel = root_graph(n, original, degree)
        for mode in MODES:
            work = Path(name) / mode
            work.mkdir(exist_ok=True, parents=True)
            formula = work / 'pinned.cnf'
            write(n, degree, degree + 1, maximum, kernel, mode, formula)
            content = formula.read_text().splitlines()
            _, _, nv, nc = content[0].split()
            edge_vars = Cnf(n, {})
            units = [f'{edge_vars.edge(*edge) * (1 if edge in relabeled else -1)} 0'
                     for edge in combinations(range(n), 2)]
            content[0] = f'p cnf {nv} {int(nc) + len(units)}'
            formula.write_text('\n'.join(content + units) + '\n')
            cmd = ['nice', '-n', '5', 'timeout', '20', 'prlimit', '--cpu=10:11', '--as=17179869184',
                   ROOT / 'opt/bin/cadical', '-q', '-n', formula]
            with (work / 'pinned.log').open('w') as log:
                decision = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=False)
            assert decision.returncode == 10, (name, mode, decision.returncode)
            print(name, mode, 'PASS', flush=True)
            total += 1
    print('PASS pinned controls:', total)


if __name__ == '__main__':
    controls = [(f'C22_{idx}', 22, 6, 5, decode(line))
                for idx, line in enumerate((ROOT / 'duo/reg6_22.g6').read_text().splitlines())]
    edges = {tuple(sorted((left, (left + step) % 35))) for left in range(35) for step in (1, 7, 11, 16)}
    test(controls + [('C35', 35, 8, 4, edges)])
