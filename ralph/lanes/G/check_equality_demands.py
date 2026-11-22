#!/usr/bin/env python3
"""Independent bit-set replay and comparison to the old pinned core."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path

from check_root_cover import graph, induced, maximal_independent, vertices


def to_graph6(adj):
    edges = [((adj[left] >> right) & 1) for right in range(len(adj)) for left in range(right)]
    edges.extend([0] * (-len(edges) % 6))
    return chr(63 + len(adj)) + ''.join(chr(63 + sum(edges[index + bit] << (5 - bit) for bit in range(6)))
                                       for index in range(0, len(edges), 6))


def oracle(adj, alpha, root, minimum, mode, planted=()):
    all_rows = sorted(maximal_independent(adj, alpha - 1))
    maximum = [row for row in all_rows if row.bit_count() == alpha - 1]
    private = alpha + 1 - root
    rows = [row for row in all_rows if not mode or max(minimum - 1, private) <= row.bit_count() < root + private]
    assert set(planted) <= set(rows)
    capped = sum(1 << vertex for vertex, edges in enumerate(adj) if edges.bit_count() == alpha - 1)
    gaps = tuple((left, right) for left, right in combinations(range(len(adj)), 2)
                 if not (adj[left] >> right & 1 or adj[left] & adj[right]))
    neighbor_demands = [sum(1 << (right if vertex == left else left) for left, right in gaps
                            if vertex in (left, right)) for vertex in range(len(adj))]
    demands = [mask for vertex in range(len(adj)) for mask in
               [1 << vertex, *(1 << vertex | 1 << left for left, right in gaps if right == vertex)]]
    domains = [sum(1 << index for index, row in enumerate(rows) if row & demand == demand) for demand in demands]
    misses = [sum(1 << index for index, witness in enumerate(maximum) if not witness & row) for row in rows]
    partners = [0] * len(rows)
    site_rows = [sum(1 << index for index, row in enumerate(rows) if row >> site & 1) for site in range(len(adj))]
    for first, second in combinations(range(len(rows)), 2):
        shared = rows[first] & rows[second]
        if misses[first] & misses[second] or capped & shared or (mode and shared.bit_count() > 1):
            continue
        if mode == 2 and shared and neighbor_demands[shared.bit_length() - 1] & ~(rows[first] | rows[second]):
            continue
        partners[first] |= 1 << second
        partners[second] |= 1 << first
    living = (1 << len(rows)) - 1
    waves = 0
    while living:
        remain = 0
        for index in vertices(living):
            row = rows[index]
            support = partners[index] & living
            if any(not (support & domain) for demand, domain in zip(demands, domains) if row & demand != demand):
                continue
            if mode == 2:
                may_share = sum(bool(support & site_rows[site]) for site in vertices(row))
                must_share = sum(bool(neighbor_demands[site] & ~row) for site in vertices(row))
                if not must_share <= row.bit_count() - private <= may_share:
                    continue
            remain |= 1 << index
        if remain == living:
            break
        waves += 1
        living = remain
    assert all(living >> rows.index(row) & 1 for row in planted)
    first_gap = next((demand for demand, domain in zip(demands, domains) if not domain & living), 0)
    return len(rows), len(maximum), len(domains), waves, living.bit_count(), first_gap


def calibrate(directory):
    cyclic = [sum(1 << ((vertex + step) % 13) for step in (1, -1, 5, -5)) for vertex in range(13)]
    assert graph.alpha(cyclic) == 4 and graph.triangle_free(cyclic)
    with (directory / 'attach.control.g6').open('w') as output:
        for root, anchors in enumerate(cyclic):
            kept = ((1 << len(cyclic)) - 1) & ~(anchors | 1 << root)
            adj = induced(cyclic, kept)
            plant = tuple(sum(1 << index for index, vertex in enumerate(vertices(kept)) if cyclic[anchor] >> vertex & 1)
                          for anchor in vertices(anchors))
            assert sum(map(int.bit_count, plant)) == 2 * len(adj) - 4
            assert all(oracle(adj, 4, 4, 4, mode, plant)[-1] == 0 for mode in range(3))
            print(to_graph6(adj), file=output)
    print('C13: all 13 actual roots and their planted columns survive all modes')


def audit(directory, sample, prefix):
    sources = (directory / f'{prefix}.g6').read_text().splitlines()
    pick = sorted({index * len(sources) // sample for index in range(sample)})
    for mode in range(3):
        given = (directory / f'{prefix}.{mode}.tsv').read_text().splitlines()
        assert len(given) == len(sources)
        for index in pick:
            adj = graph.parse_graph6(sources[index])
            assert len(adj) == 33 and sum(map(int.bit_count, adj)) == 244
            assert graph.triangle_free(adj) and graph.alpha(adj) == 8
            *received, last = given[index].split('\t')
            assert (index + 1, *oracle(adj, 9, 6, 6, mode)) == (*map(int, received), int(last, 16))
    print(f'independent bit-set replay: all counts and obstruction IDs matched on {len(pick)} sources × 3 modes')


def core(directory, cap, prefix):
    from pysat.solvers import Cadical195
    from root_glue import encode

    sources = (directory / f'{prefix}.g6').read_text().splitlines()
    certified_cliques = {int(line.split()[0]) for line in (directory / f'{prefix}.clique.tsv').read_text().splitlines()}
    tally = Counter()
    print('index\tstatus', flush=True)
    for index, line in enumerate(sources, 1):
        if index in certified_cliques:
            status = 'clique'
        else:
            adj = graph.parse_graph6(line)
            assert len(adj) == 33 and sum(map(int.bit_count, adj)) == 244
            model, _ = encode(adj, 6, 9, 6, 170, False)
            with Cadical195(bootstrap_with=model.clauses) as solver:
                solver.conf_budget(cap)
                verdict = solver.solve_limited()
            status = 'relaxed-SAT' if verdict is True else 'unchecked-UNSAT' if verdict is False else 'cap'
        print(index, status, sep='\t', flush=True)
        tally[status] += 1
    print(f'old clique + pinned core cap={cap}: {dict(tally)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('cal', 'audit', 'core'))
    parser.add_argument('directory', type=Path)
    parser.add_argument('--count', type=int, default=8)
    parser.add_argument('--prefix', default='attach')
    args = parser.parse_args()
    if args.mode == 'cal':
        calibrate(args.directory)
    elif args.mode == 'audit':
        audit(args.directory, args.count, args.prefix)
    else:
        core(args.directory, args.count, args.prefix)
