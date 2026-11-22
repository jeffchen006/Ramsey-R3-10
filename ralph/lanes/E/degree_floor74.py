#!/usr/bin/env python3
"""Optional measured degree-floor propagation on mixed 74-edge residues."""

import argparse
from collections import Counter
from itertools import groupby
from pathlib import Path
from time import process_time

from fuse_shared74 import fuse
from involution_cores import bits, graph
from m11_prop import Prover, targets
from order_shared74 import OMISSIONS, decode, read


def floor_round(lower, upper, omissions, minimum):
    universe = (1 << len(lower)) - 1
    forced = 0
    for omitted in omissions:
        active = universe ^ sum(1 << vertex for vertex in omitted)
        for vertex in bits(active):
            possible = upper[vertex] & active
            if possible.bit_count() < minimum:
                return None
            if possible.bit_count() == minimum:
                for neighbor in bits(possible & ~lower[vertex]):
                    lower[vertex] |= 1 << neighbor
                    lower[neighbor] |= 1 << vertex
                    forced += 1
    return forced


def calibrate():
    order = 13
    exact = graph(order, [(vertex, (vertex+shift) % order) for vertex in range(order) for shift in (1, 5)])
    counts = Counter()
    for shift in range(order):
        omissions = (tuple((shift + vertex) % order for vertex in (0, 3, 10)),
                     tuple((shift + vertex) % order for vertex in (2, 8, 12)))
        minimum = min(sum((row >> other) & 1 for other in range(order) if other not in omission)
                      for omission in omissions for vertex, row in enumerate(exact) if vertex not in omission)
        lower = [0] * order
        upper = list(exact)
        for vertex in range(order):
            neighbor = (vertex+2) % order
            upper[vertex] |= 1 << neighbor
            upper[neighbor] |= 1 << vertex
            affected = floor_round(lower, upper, omissions, minimum)
            assert affected is not None and all(not new & ~prev for new, prev in zip(lower, exact))
            counts['partial cards'] += 1
            counts['lower-edge insertions'] += affected
        assert floor_round(list(exact), exact, omissions, minimum+1) is None
        counts['planted bad floors'] += 1
    assert counts['lower-edge insertions']
    print('C13(1,5) floor controls', dict(counts), flush=True)


def pilot(source, trace, library):
    stats = Counter()
    prover = Prover(library)
    started = process_time()
    selected = iter(groupby(((index, lift) for index, lift, status, *_ in read(trace) if status == 'open'),
                            key=lambda row: row[0]))
    pending = next(selected, None)
    for index, row in enumerate(read(source)):
        if pending is None:
            break
        if index != pending[0]:
            continue
        core, parts, omitted = decode(row)
        for _, lift in pending[1]:
            lower, upper = targets(core, (*parts, omitted[lift]))
            degrees = (8,) * 8 + (7,) * 24
            status, lower, upper, _ = fuse(lower, upper, OMISSIONS, degrees, 7, 74, prover)
            assert status == 'open'
            stats['input residues'] += 1
            for _ in range(1 + 32**2):
                forced = floor_round(lower, upper, OMISSIONS, 4)
                if forced is None:
                    status = 'degree-floor conflict'
                    break
                if not forced:
                    break
                stats['floor-induced edges'] += forced
                status, lower, upper, _ = fuse(lower, upper, OMISSIONS, degrees, 7, 74, prover)
                if status != 'open':
                    break
            else:
                raise AssertionError('degree-floor propagation is monotone')
            stats[status] += 1
            print(index, lift, status, flush=True)
        pending = next(selected, None)
    assert pending is None and stats['input residues']
    print(dict(stats), f'cpu={process_time()-started:.3f}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    commands.add_parser('calibrate')
    sample = commands.add_parser('pilot')
    sample.add_argument('source', type=Path)
    sample.add_argument('trace', type=Path)
    sample.add_argument('--library', type=Path, default=Path('../r6_e11/m11_prop.so'))
    args = parser.parse_args()
    if args.action == 'calibrate':
        calibrate()
    else:
        pilot(args.source, args.trace, args.library)
