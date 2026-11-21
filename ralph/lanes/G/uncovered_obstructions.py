#!/usr/bin/env python3
"""Necessary MTF tests: clique of incompatible demands or local degree cap."""

import argparse
from collections import Counter
from pathlib import Path
from time import process_time

from check_root_cover import graph, induced, vertices
from root_core import check_witness


def partners(rows):
    universe = (1 << len(rows)) - 1
    for vertex, neighbors in enumerate(rows):
        covered = neighbors | (1 << vertex)
        for middle in vertices(neighbors):
            covered |= rows[middle]
        yield universe ^ covered


def odd_cycle(rows, tail):
    color = {}
    for root in vertices(tail):
        if root in color:
            continue
        color[root] = 0
        pending = [root]
        for vertex in pending:
            for nxt in vertices(rows[vertex] & tail):
                if nxt in color:
                    if color[nxt] == color[vertex]:
                        return True
                else:
                    color[nxt] = 1 - color[vertex]
                    pending.append(nxt)
    return False


def clique_of_size(neighbors, count):
    def search(allowed, count):
        if not count:
            return ()
        while allowed.bit_count() >= count:
            filtered = (vertex for vertex in vertices(allowed)
                        if (neighbors[vertex] & allowed).bit_count() >= count - 1)
            kept = sum(1 << vertex for vertex in filtered)
            if kept == allowed:
                break
            allowed = kept
        while allowed.bit_count() >= count:
            best = max(vertices(allowed), key=lambda vertex: (neighbors[vertex] & allowed).bit_count())
            allowed ^= 1 << best
            branch = search(allowed & neighbors[best], count - 1)
            if branch is not None:
                return (best, *branch)
        return None

    return search((1 << len(neighbors)) - 1, count)


def obstruction(rows, degree, alpha):
    distant = tuple(partners(rows))
    for vertex, tail in enumerate(distant):
        cap = alpha - rows[vertex].bit_count()
        if cap <= 0 or (cap == 1 and any(rows[other] & tail for other in vertices(tail))):
            return 'cap1', ()
        if cap == 2 and odd_cycle(rows, tail):
            return 'cap2', ()

    demands = []
    for first, tail in enumerate(distant):
        if not tail:
            demands.append((1 << first, rows[first]))
        for second in vertices(tail & ~((1 << first) - 1)):
            demands.append(((1 << first) | (1 << second), rows[first] | rows[second]))
    incompatible = [0] * len(demands)
    for first, (mask, _) in enumerate(demands):
        for second in range(first):
            if mask & demands[second][1]:
                incompatible[first] |= 1 << second
                incompatible[second] |= 1 << first
    clique = clique_of_size(incompatible, degree + 1)
    if clique is not None:
        return 'clique', tuple(demands[index][0] for index in clique)
    return 'none', ()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--degree', type=int, required=True)
    parser.add_argument('--alpha', type=int, default=9)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--trace', type=Path)
    parser.add_argument('--unproved', type=Path)
    args = parser.parse_args()
    started = process_time()
    stats = Counter()
    certificates, unproved = [], []
    for index, line in enumerate(args.source.read_text().splitlines(), 1):
        rows = graph.parse_graph6(line)
        if args.control:
            assert graph.triangle_free(rows) and graph.alpha(rows) <= args.alpha
            for root, nbrs in enumerate(rows):
                root_degree = nbrs.bit_count()
                assert args.degree in (0, root_degree)
                check_witness(rows, root, args.alpha)
                residue = induced(rows, ((1 << len(rows)) - 1) & ~(nbrs | (1 << root)))
                assert obstruction(residue, root_degree, args.alpha)[0] == 'none'
                stats['witness'] += 1
        else:
            label, witness = obstruction(rows, args.degree, args.alpha)
            stats[label] += 1
            if witness:
                certificates.append(str(index) + '\t' + ' '.join(format(mask, 'x') for mask in witness) + '\n')
            else:
                unproved.append(f'{index}\t{line}\n')
    if args.trace:
        args.trace.write_text(''.join(certificates))
    if args.unproved:
        args.unproved.write_text(''.join(unproved))
    print(f'{dict(stats)} CPU={process_time()-started:.4f}s')


if __name__ == '__main__':
    main()
