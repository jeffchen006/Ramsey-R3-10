#!/usr/bin/env python3
"""Dependency-free necessary CNF for extending a fixed residue at an MTF root."""

import argparse
from itertools import combinations
from pathlib import Path

from check_root_cover import graph, induced, vertices


def clauses_for(adj, root_degree, alpha):
    size = len(adj)
    assert graph.triangle_free(adj) and graph.alpha(adj) < alpha
    columns = [tuple(range(index * size + 1, (index + 1) * size + 1)) for index in range(root_degree)]
    clauses = []
    last = root_degree * size
    for column in columns:
        for vertex, nbrs in enumerate(adj):
            clauses.append([column[vertex], *(column[other] for other in vertices(nbrs))])
            clauses.extend((-column[vertex], -column[other]) for other in vertices(nbrs) if vertex < other)
    for vertex, nbrs in enumerate(adj):
        attachment = tuple(column[vertex] for column in columns)
        clauses.append(attachment)
        cap = alpha - nbrs.bit_count()
        if cap < 0:
            clauses.append(())
        else:
            clauses.extend(tuple(-literal for literal in combo) for combo in combinations(attachment, cap + 1))
    for first, second in combinations(range(size), 2):
        if (adj[first] & (1 << second)) or adj[first] & adj[second]:
            continue
        common = []
        for column in columns:
            last += 1
            common.append(last)
            clauses.append((-last, column[first]))
            clauses.append((-last, column[second]))
        clauses.append(common)
    return last, clauses


def dimacs(variables, clauses):
    yield f'p cnf {variables} {len(clauses)}\n'
    for clause in clauses:
        yield ' '.join(map(str, (*clause, 0))) + '\n'


def check_witness(adj, root, alpha):
    neighbours = tuple(vertices(adj[root]))
    exterior_mask = ((1 << len(adj)) - 1) & ~(adj[root] | (1 << root))
    exterior = tuple(vertices(exterior_mask))
    residual = induced(adj, exterior_mask)
    size = len(exterior)
    variables, clauses = clauses_for(residual, len(neighbours), alpha)
    values = [False] + [bool(adj[neighbour] & (1 << vertex)) for neighbour in neighbours for vertex in exterior]
    for first, second in combinations(range(size), 2):
        if not (residual[first] & (1 << second) or residual[first] & residual[second]):
            values.extend(bool(adj[neighbour] & (1 << exterior[first])) and
                          bool(adj[neighbour] & (1 << exterior[second])) for neighbour in neighbours)
    assert len(values) == variables + 1
    assert all(any(values[abs(lit)] == (lit > 0) for lit in clause) for clause in clauses)


def calibrate(exoo_path):
    complement = graph.parse_matrix(exoo_path.read_text().splitlines())
    exoo = [neighbours ^ ((1 << 39) - 1) ^ (1 << vertex) for vertex, neighbours in enumerate(complement)]
    for first, second in combinations(range(39), 2):
        if not (exoo[first] & (1 << second) or exoo[first] & exoo[second]):
            exoo[first] |= 1 << second
            exoo[second] |= 1 << first
    c35 = [sum(1 << ((vertex + step) % 35) for step in (1, -1, 7, -7, 11, -11, 16, -16))
           for vertex in range(35)]
    order22 = Path(__file__).resolve().parents[3] / 'gluing/val/r3_7_22.g6'
    controls = [(c35, 8), (exoo, 9)]
    for row in order22.read_text().splitlines():
        adj = graph.parse_graph6(row)
        if all(neighbours.bit_count() == 6 for neighbours in adj):
            controls.append((adj, 6))
    assert len(controls) == 12
    count = 0
    for adj, alpha in controls:
        assert graph.triangle_free(adj) and graph.alpha(adj) == alpha
        for root in range(len(adj)):
            check_witness(adj, root, alpha)
            count += 1
    print(f'{count} actual rooted MTF completions satisfy every clause')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('out', type=Path)
    parser.add_argument('--root', type=int, default=6)
    parser.add_argument('--alpha', type=int, default=9)
    parser.add_argument('--controls', type=Path)
    args = parser.parse_args()
    if args.controls:
        calibrate(args.controls)
    for index, row in enumerate(args.catalogue.read_text().splitlines(), 1):
        variables, clauses = clauses_for(graph.parse_graph6(row), args.root, args.alpha)
        with (args.out / f'{index:04d}.cnf').open('w') as stream:
            stream.writelines(dimacs(variables, clauses))
        print(index, variables, len(clauses))


if __name__ == '__main__':
    main()
