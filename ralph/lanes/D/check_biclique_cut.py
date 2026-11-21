#!/usr/bin/env python3
"""Check the saturated K3,3 obstruction for each rooted kernel."""

import argparse
from collections import Counter
from csv import DictReader
from itertools import combinations
from pathlib import Path

from kernel_cnf import decode


def witness(line, width):
    edges = decode(line)
    assert ord(line[0]) == 63 + 2 * width and all(left < width <= right for left, right in edges)
    adj = [set() for _ in range(width)]
    for left, right in edges:
        adj[left].add(right)
    for left1, left2 in combinations(range(width), 2):
        shared = sorted(adj[left1] & adj[left2])
        if len(shared) >= 2:
            return (left1, left2, *shared[:2])
    return ()


def test_control(graph, n, degree):
    assert n < 6 * degree - 12 and ord(graph[0]) == 63 + n
    adj = [set() for _ in range(n)]
    for left, right in decode(graph):
        adj[left].add(right)
        adj[right].add(left)
    assert all(len(row) == degree for row in adj)
    assert all(not (adj[left] & adj[right]) for left, right in decode(graph))
    assert all(len(adj[left] & adj[right]) <= 3 for left, right in combinations(range(n), 2))
    assert all(len(adj[a] & adj[b] & adj[c]) < 3 for a, b, c in combinations(range(n), 3))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--controls', type=Path, required=True)
    parser.add_argument('--catalogue', type=Path, required=True)
    parser.add_argument('--orbits', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    controls = args.controls.read_text().splitlines()
    assert len(controls) == 5 and len(set(controls)) == 5
    for graph in controls:
        test_control(graph, 16, 5)
    assert witness('C]', 2) == (0, 1, 2, 3)
    assert witness('C?', 2) == ()
    assert 40 < 6 * 9 - 12
    kernels = args.catalogue.read_text().splitlines()
    assert len(set(kernels)) == len(kernels) == 238
    oriented = {index: cuts for index, line in enumerate(kernels) if (cuts := witness(line, 8))}
    with args.orbits.open() as file:
        orbits = list(DictReader(file, delimiter='\t'))
    assert len(orbits) == 166
    observed = set()
    closed = []
    remain = []
    surviving_count = 0
    for orbit in orbits:
        rep = int(orbit['representative'])
        group = [int(index) for index in orbit['oriented_indices'].split(',')]
        assert rep in group and orbit['kernel'] == kernels[rep] and not set(group) & observed
        observed.update(group)
        assert len({index in oriented for index in group}) == 1
        if not orbit['checked_excluded_by']:
            surviving_count += 1
            size = int(orbit['edges'])
            if rep in oriented:
                closed.append((rep, size, oriented[rep], kernels[rep]))
            else:
                remain.append((rep, size, kernels[rep]))
    assert observed == set(range(len(kernels))) and surviving_count == 110
    args.out.mkdir(exist_ok=True)
    (args.out / 'closed.tsv').write_text('representative\tedges\tcycle_left_left_right_right\tkernel\n' + ''.join(
        f'{rep}\t{size}\t{",".join(map(str,cycle))}\t{kernel}\n' for rep, size, cycle, kernel in closed))
    (args.out / 'remaining.tsv').write_text('representative\tedges\tkernel\n' + ''.join(
        f'{rep}\t{size}\t{kernel}\n' for rep, size, kernel in remain))
    print('Oriented kernel cycles:', len(oriented))
    print('Fresh rooted orbits excluded:', len(closed), sorted(Counter(size for _, size, _, _ in closed).items()))
    print('Remaining rooted orbits:', len(remain), sorted(Counter(size for _, size, _ in remain).items()))


if __name__ == '__main__':
    main()
