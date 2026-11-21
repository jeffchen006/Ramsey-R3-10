"""Brute-force replay of the row-size filter on smaller residues."""

import itertools
from pathlib import Path
import subprocess

from cal_profile import controls, dual, to_graph6


def witness(rows, sizes):
    order = len(rows)
    full = (1 << order) - 1
    covered = set()
    for size in sizes:
        for choice in itertools.combinations(range(order), size):
            mask = sum(1 << vertex for vertex in choice)
            if any(rows[vertex] & mask for vertex in choice):
                continue
            union = mask
            for vertex in choice:
                union |= rows[vertex]
            if union != full:
                continue
            covered.update(1 << vertex for vertex in choice)
            covered.update((1 << first) | (1 << second) for first, second in itertools.combinations(choice, 2))
    for first, second in itertools.combinations(range(order), 2):
        mask = (1 << first) | (1 << second)
        if not (rows[first] & (1 << second) or rows[first] & rows[second]) and mask not in covered:
            return mask
    return next((1 << vertex for vertex in range(order) if 1 << vertex not in covered), 0)


def test():
    for index, (_, graph, root) in enumerate(itertools.islice(controls(Path('work/cal22_reference.g6')), 12)):
        rows = dual(graph, root)
        data = to_graph6(rows) + '\n'
        actual_sizes = {neighbors.bit_count()-1 for vertex, neighbors in enumerate(graph) if graph[root] >> vertex & 1}
        for sizes in (actual_sizes, {1}, {3, 4}, {4, 5, 6}):
            command = ['timeout', '10s', 'build/row_support', ''.join(map(str, sorted(sizes)))]
            generated = subprocess.run(command, input=data, text=True, capture_output=True, check=True)
            expected = witness(rows, sizes)
            assert int(generated.stdout.strip(), 16) == expected, (index, sizes)
            if sizes is actual_sizes:
                assert expected == 0
            if index == 0 and sizes == {1}:
                trace = Path('work/e162_r5/control.hex')
                trace.write_text(generated.stdout)
                assert subprocess.run(command + [trace], input=data, text=True, capture_output=True).returncode == 0
                trace.write_text('0\n')
                assert subprocess.run(command + [trace], input=data, text=True, capture_output=True).returncode == 1
    print('48 exact brute-force control witnesses; positive MTF roots, genuine replay and corrupt trace checked')


if __name__ == '__main__':
    test()
