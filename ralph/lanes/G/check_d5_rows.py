#!/usr/bin/env python3
"""Check the residue degree and universal-vertex rows on smaller MTF graphs."""

from argparse import ArgumentParser
from collections import Counter
from pathlib import Path

from check_root_cover import graph, vertices
from check_rows import saturated


def test(adj, alpha):
    assert graph.triangle_free(adj) and graph.alpha(adj) == alpha
    order = len(adj)
    full = (1 << order) - 1
    degrees = list(map(int.bit_count, adj))
    stats = Counter()
    for root, neighbours in enumerate(adj):
        exterior = full & ~(neighbours | 1 << root)
        d = degrees[root]
        if not exterior:
            continue
        minimum = min((adj[v] & exterior).bit_count() for v in vertices(exterior))
        if minimum == 0:
            continue
        stats['roots'] += 1
        equates = 0
        for other in vertices(exterior):
            common = (neighbours & adj[other]).bit_count()
            residue_degree = degrees[other] - common
            assert residue_degree == (adj[other] & exterior).bit_count()
            assert 1 <= common <= degrees[other] - minimum
            equates += common == degrees[other] - minimum
        stats['cap_equality'] += equates
        peers = {v for v, degree in enumerate(degrees) if v != root and degree == minimum}
        assert all(neighbours & 1 << peer for peer in peers)
        stats['peer_pairs'] += len(peers)
        if d == minimum:
            stats['universal_roots'] += 1
            assert all(not adj[left] & 1 << right for left in peers for right in peers)
    return stats


def adjacent_peer_control():
    adj = [0] * 12
    pairs = [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 5), (3, 4)]
    pairs.extend((left, right) for left in range(6, 9) for right in range(9, 12))
    pairs.extend((wing, core) for wing, side in ((2, range(6, 9)), (4, range(6, 9)),
                                               (3, range(9, 12)), (5, range(9, 12))) for core in side)
    for left, right in pairs:
        adj[left] |= 1 << right
        adj[right] |= 1 << left
    assert adj == saturated(adj.copy())
    result = test(adj, graph.alpha(adj))
    assert result['universal_roots'] >= 2 and result['peer_pairs'] >= 2
    return result


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('exoo', type=Path)
    parser.add_argument('r37', type=Path)
    args = parser.parse_args()
    circ = lambda order, jumps: [sum(1 << ((v + offset) % order) for offset in jumps) for v in range(order)]
    complement = graph.parse_matrix(args.exoo.read_text().splitlines())
    exoo = [neighbours ^ ((1 << 39) - 1) ^ (1 << v) for v, neighbours in enumerate(complement)]
    for name, adj, alpha in [('C13', circ(13, (1, -1, 5, -5)), 4),
                             ('C35', circ(35, (1, -1, 7, -7, 11, -11, 16, -16)), 8),
                             ('Exoo39-MTF', saturated(exoo), 9)]:
        print(name, dict(test(adj, alpha)))
    stats = Counter()
    for line in args.r37.read_text().splitlines():
        stats.update(test(saturated(graph.parse_graph6(line)), 6))
    assert stats['roots'] > 0 and stats['cap_equality'] > 0
    print('All 191 order-22 inputs, saturated:', dict(stats))
    print('Adjacent degree-three peer control:', dict(adjacent_peer_control()))
