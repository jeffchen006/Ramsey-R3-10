#!/usr/bin/env python3
"""Exact necessary high-degree residue projection of the e10 small groups."""

import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, permutations
import json
from pathlib import Path
from time import process_time

from cubic32 import automorphisms, invert, neighborhoods
from deficit73 import mask
from involution_cores import bits, graph
from involution_sat import from_graph6
from m11_support import Supports, image, triples


def degree_vector(group, length):
    return tuple(sum(col >> vertex & 1 for col in group) for vertex in range(length))


@lru_cache(maxsize=2048)
def canon(core, selection):
    sites = tuple(bits(selection))
    return min(tuple(core[left] >> right & 1 for left, right in combinations(order, 2))
               for order in permutations(sites))


def roster_cells(core, small_rows, residue):
    tripled = residue.count(2)
    assert sum(residue) == 6 and min(residue) >= 0 and max(residue) <= 2
    if tripled < 2:
        return ()
    high = [mask(vertex for vertex, inc in enumerate(row) if inc == 1) for row in small_rows]
    assert all(word.bit_count() == 6 for word in high)
    permits_six = len({canon(core, word) for word in high}) == 1
    return (*((6,) if permits_six else ()), *((7,) if tripled == 3 else ()))


def cover(key, independent, stream):
    core = tuple(from_graph6(key))
    cap = tuple(4 - row.bit_count() for row in core)
    assert len(core) == 8 and sum(cap) == 12 and min(cap) >= 0 and max(cap) == 2
    support = Supports(core, 6)
    small = support.catalog(10, cap)
    autos = tuple(automorphisms(core))
    if independent:
        pairs = [pair for pair in combinations(range(8), 2) if all(cap[vertex] for vertex in pair)]
        direct = {tuple(sorted(invert(rows))) for pair in pairs for rows in neighborhoods(core, pair)}
        assert set(small) == direct and len(small) == len(direct)
    row_degrees = {group: degree_vector(group, 8) for group in small}
    tally = Counter()
    start = process_time()

    def labelled():
        for groups in combinations_with_replacement(small, 3):
            remainder = tuple(7 - core[vertex].bit_count() - sum(row_degrees[group][vertex] for group in groups)
                              for vertex in range(len(core)))
            if min(remainder) < 0 or remainder.count(2) < 2:
                continue
            images = {tuple(sorted(image(group, perm) for group in groups)) for perm in autos}
            if groups == min(images):
                yield groups, remainder, None

    incoming = labelled() if independent else triples(core, support, (10, 10, 10, 14), cap, {10: small}, autos)
    for parts, remainder, _ in incoming:
        tally['raw'] += 1
        rows = [row_degrees[group] for group in parts]
        for total in roster_cells(core, rows, remainder):
            print(json.dumps((key, parts, remainder, total), separators=(',', ':')), file=stream)
            tally[f'K{total}'] += 1
    print(key, 'local', len(small), 'auto', len(autos), dict(tally), f'cpu={process_time()-start:.4f}', flush=True)


def control():
    core = graph(8, [(vertex, (vertex+1) % 8) for vertex in range(8)])

    def rows(placed):
        return tuple(2 if vertex in placed else 1 for vertex in range(8))

    for offsets in (0, 2, 4):
        first = rows((offsets, offsets+1))
        second = rows((0, 1))
        options = ((first, second, rows((4, 5))), (first, second, rows((4, 6))))
        assert roster_cells(core, options[0], (2, 2, 1, 1, 0, 0, 0, 0)) == (6,)
        assert roster_cells(core, options[1], (2, 2, 1, 1, 0, 0, 0, 0)) == ()
        assert roster_cells(core, options[1], (2, 2, 2, 0, 0, 0, 0, 0)) == (7,)
    print('degree-roster invariants accept three relabels, reject changed induced shape only at K=6', flush=True)


def verify_cores(path):
    import pynauty

    def certificate(adjacency):
        return pynauty.certificate(pynauty.Graph(8, adjacency_dict={site: list(bits(row)) for site, row in enumerate(adjacency)}))

    keys = path.read_text(encoding='ascii').splitlines()
    got = {certificate(from_graph6(key)) for key in keys}
    assert len(got) == len(keys) == 20
    edge_pool = [(left, right) for left, right in combinations(range(1, 8), 2) if (left, right) != (1, 2)]
    seen = set()
    labelled = 0
    for choice in combinations(edge_pool, 8):
        core = graph(8, ((0, 1), (0, 2), *choice))
        if not all(2 <= row.bit_count() <= 4 for row in core):
            continue
        if any(row & core[peer] for row in core for peer in bits(row)):
            continue
        labelled += 1
        seen.add(certificate(core))
    assert got == seen and labelled
    print('complete e10 W cover', len(seen), 'normalized labelled', labelled, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core')
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--verify-cores', type=Path)
    parser.add_argument('--independent', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.control:
        control()
    elif args.verify_cores:
        verify_cores(args.verify_cores)
    else:
        with args.output.open('x', encoding='ascii') as stream:
            cover(args.core, args.independent, stream)
