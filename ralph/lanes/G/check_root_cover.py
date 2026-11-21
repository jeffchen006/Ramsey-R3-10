#!/usr/bin/env python3
"""Independent exact column-cover obstruction; no SAT solver or third-party imports."""

import argparse
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
import check_graph as graph


def vertices(mask):
    while mask:
        bit = mask & -mask
        mask ^= bit
        yield bit.bit_length() - 1


def maximal_independent(adj, limit):
    """Bron–Kerbosch in the complement, with a size limit."""
    universe = (1 << len(adj)) - 1
    complement = [universe ^ (1 << vertex) ^ nbrs for vertex, nbrs in enumerate(adj)]

    def search(selected, possible, done, size):
        if not (possible | done):
            yield selected
        elif size < limit:
            pivot = max(vertices(possible | done), key=lambda vertex: (possible & complement[vertex]).bit_count())
            todo = possible & ~complement[pivot]
            while todo:
                bit = todo & -todo
                todo ^= bit
                nbrs = complement[bit.bit_length() - 1]
                yield from search(selected | bit, possible & nbrs, done & nbrs, size + 1)
                possible ^= bit
                done |= bit

    yield from search(0, universe, 0, 0)


def obstruction(adj, root_degree, alpha, minimum, total_edges, crosscheck=False):
    order = len(adj)
    universe = (1 << order) - 1
    cross = total_edges - sum(map(int.bit_count, adj)) // 2 - root_degree
    budget = min(alpha - 1, cross - (root_degree - 1) * (minimum - 1))
    columns = list(maximal_independent(adj, budget))
    if crosscheck:
        brute = set()
        for size in range(minimum - 1, budget + 1):
            for choice in combinations(range(order), size):
                mask = sum(1 << vertex for vertex in choice)
                dominated = mask
                for vertex in choice:
                    if adj[vertex] & mask:
                        break
                    dominated |= adj[vertex]
                else:
                    if dominated == universe:
                        brute.add(mask)
        assert {column for column in columns if column.bit_count() >= minimum - 1} == brute
    eligible = [column for column in columns if column.bit_count() >= minimum - 1]
    if not eligible:
        return 'no eligible column', 0, 0
    smallest = min(map(int.bit_count, eligible))
    slack = cross - root_degree * smallest
    if slack < 0:
        return 'column sizes exceed budget', smallest, 0
    small = [column for column in eligible if column.bit_count() == smallest]
    unavailable = universe
    pairs_needed = [(first, second) for first, second in combinations(range(order), 2)
                    if not (adj[first] & (1 << second) or adj[first] & adj[second])]
    for column in small:
        unavailable &= ~column
    if slack == 0:
        if unavailable:
            return 'uncovered vertex', smallest, len(small)
        for first, second in pairs_needed:
            pair = (1 << first) | (1 << second)
            if all(column & pair != pair for column in small):
                return 'uncovered MTF pair', smallest, len(small)
    if slack == 1 and any(adj[vertex] & unavailable for vertex in vertices(unavailable)):
        return 'adjacent uncovered vertices', smallest, len(small)
    return None, smallest, len(small)


def induced(adj, mask):
    rows = tuple(vertices(mask))
    return [sum(((adj[vertex] >> other) & 1) << pos for pos, other in enumerate(rows)) for vertex in rows]


def controls(exoo_file):
    complement = graph.parse_matrix(exoo_file.read_text().splitlines())
    exoo = [nbrs ^ ((1 << 39) - 1) ^ (1 << v) for v, nbrs in enumerate(complement)]
    for first, second in combinations(range(39), 2):
        if not (exoo[first] & (1 << second) or exoo[first] & exoo[second]):
            exoo[first] |= 1 << second
            exoo[second] |= 1 << first
    c35 = [sum(1 << ((v + step) % 35) for step in (1, -1, 7, -7, 11, -11, 16, -16)) for v in range(35)]
    order22 = Path(__file__).resolve().parents[3] / 'gluing/val/r3_7_22.g6'
    parsed = map(graph.parse_graph6, order22.read_text().splitlines())
    regular22 = [adj for adj in parsed if all(nbrs.bit_count() == 6 for nbrs in adj)]
    count = 0
    for adj, alpha in [(c35, 8), (exoo, 9), *((adj, 6) for adj in regular22)]:
        assert graph.triangle_free(adj) and graph.alpha(adj) == alpha
        degrees = list(map(int.bit_count, adj))
        for root, nbrs in enumerate(adj):
            exterior = ((1 << len(adj)) - 1) & ~(nbrs | (1 << root))
            result, _, _ = obstruction(induced(adj, exterior), degrees[root], alpha,
                                       min(degrees), sum(degrees) // 2)
            assert result is None, (len(adj), root, result)
            count += 1
    assert count == 294
    print(f'Positive controls: {count} actual rooted MTF completions retain feasibility')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('--controls', type=Path)
    parser.add_argument('--edges', type=int, required=True)
    parser.add_argument('--crosscheck', action='store_true')
    args = parser.parse_args()
    if args.controls:
        controls(args.controls)
    checked = 0
    for index, row in enumerate(args.catalogue.read_text().splitlines(), 1):
        adj = graph.parse_graph6(row)
        assert len(adj) == 33 and graph.triangle_free(adj) and graph.alpha(adj) == 8
        edge_count = sum(map(int.bit_count, adj)) // 2
        why, smallest, candidates = obstruction(adj, 6, 9, 6, args.edges, args.crosscheck)
        print(index, edge_count, smallest, candidates, why or 'not excluded')
        checked += bool(why)
    print(f'{checked}/{index} excluded')


if __name__ == '__main__':
    main()
