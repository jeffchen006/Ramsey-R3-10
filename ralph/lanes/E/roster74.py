#!/usr/bin/env python3
"""Pilot a common top-degree induced signature on fused deletion windows."""

import argparse
from collections import Counter
from itertools import combinations, groupby
from pathlib import Path
from time import process_time

from fuse_shared74 import fuse
from involution_cores import bits, graph
from m11_prop import Prover, targets
from order_shared74 import OMISSIONS, decode, read
from shared74 import singles, surviving_counts


def signature(rows):
    colors = tuple(row.bit_count() for row in rows)
    second = tuple((colors[vertex], tuple(sorted(colors[other] for other in bits(row))))
                   for vertex, row in enumerate(rows))
    return tuple(sorted((second[vertex], tuple(sorted(second[other] for other in bits(row))))
                        for vertex, row in enumerate(rows)))


def induced(lower, roots, extras):
    labels = (*bits(roots), *extras)
    graph_rows = []
    for rank, vertex in enumerate(labels):
        row = sum(1 << other_rank for other_rank, other in enumerate(labels)
                  if lower[vertex] >> other & 1 or (vertex in extras and other in extras and other != vertex))
        assert not row >> rank & 1
        graph_rows.append(row)
    return tuple(graph_rows)


def window_types(lower, upper, wings, roots, window, outside_degree, count):
    omitted = wings[window]
    attached = {vertex: group for group, vertices in enumerate(wings) if group != window
                for vertex in bits(vertices)}
    required = count - roots.bit_count()
    if not 0 <= required <= 2:
        return set()
    mandatory = {vertex for vertex in attached if not upper[vertex] & omitted}
    allowed = {vertex for vertex in attached if not lower[vertex] & omitted
               and (upper[vertex] & ~omitted).bit_count() >= outside_degree}
    if not mandatory <= allowed or len(mandatory) > required:
        return set()
    types = set()
    for additional in combinations(sorted(allowed - mandatory), required - len(mandatory)):
        extras = (*sorted(mandatory), *additional)
        if len(extras) == 2:
            left, right = extras
            if attached[left] == attached[right] or not upper[left] >> right & 1:
                continue
        types.add(signature(induced(lower, roots, extras)))
    return types


def common(lower, upper, wings, roots, outside_degree, counts):
    for count in counts:
        shared = window_types(lower, upper, wings, roots[0], 0, outside_degree, count)
        for window in range(1, len(wings)):
            if not shared:
                break
            shared &= window_types(lower, upper, wings, roots[window], window, outside_degree, count)
        if shared:
            yield count


def calibrate():
    order = 13
    exact = graph(order, [(vertex, (vertex+shift) % order) for vertex in range(order) for shift in (1, 5)])
    assert all(row.bit_count() == 4 for row in exact)
    independent = [sum(1 << vertex for vertex in block) for block in combinations(range(order), 3)
                   if all(not exact[left] >> right & 1 for left, right in combinations(block, 2))]
    stats = Counter()
    universe = (1 << order) - 1
    for first in independent:
        translated = sorted({sum(1 << ((vertex+shift) % order) for vertex in bits(first))
                             for shift in range(order)})
        for second, third, fourth in combinations((mask for mask in translated if mask > first), 3):
            wings = (first, second, third, fourth)
            occupied = first | second | third | fourth
            if occupied.bit_count() != 12:
                continue
            core = universe ^ occupied
            roots = tuple(sum(1 << vertex for vertex in bits(core) if not exact[vertex] & omitted)
                          for omitted in wings)
            actual = [tuple(vertex for vertex in bits(occupied & ~omitted) if not exact[vertex] & omitted)
                      for omitted in wings]
            counts = tuple(len(extra) + root.bit_count() for extra, root in zip(actual, roots))
            assert len(set(counts)) == 1 and all(len(extra) <= 2 for extra in actual)
            lower = [row & core if not core >> vertex & 1 else row for vertex, row in enumerate(exact)]
            upper = [row | ((occupied ^ (1 << vertex)) if occupied >> vertex & 1 else 0)
                     for vertex, row in enumerate(exact)]
            count = counts[0]
            assert tuple(common(exact, exact, wings, roots, 4, (count,))) == (count,)
            assert tuple(common(lower, upper, wings, roots, 4, (count,))) == (count,)
            assert not tuple(common(exact, exact, wings, roots, 4, (count + 1,)))
            for window, extras in enumerate(actual):
                vertices = (*bits(roots[window]), *extras)
                reference = graph(len(vertices), [(left, right) for left, right in combinations(range(len(vertices)), 2)
                                                 if exact[vertices[left]] >> vertices[right] & 1])
                assert induced(exact, roots[window], extras) == tuple(reference)
            stats['exact positive'] += 1
            stats['partial positive'] += 1
            stats['wrong count rejected'] += 1
    assert stats['exact positive'] > 0
    print('C13(1,5), translated disjoint independent triples', dict(stats), flush=True)


def pilot(source, trace, library, prefilter):
    stats = Counter()
    times = Counter()
    prover = Prover(library)
    wings = tuple(sum(1 << vertex for vertex in omit) for omit in OMISSIONS)
    statuses = ('incompatible', 'open') if prefilter else ('open',)
    selected = iter(groupby(((index, lift, status) for index, lift, status, *_ in read(trace)
                             if status in statuses), key=lambda row: row[0]))
    pending = next(selected, None)
    for index, row in enumerate(read(source)):
        if pending is None:
            break
        if index != pending[0]:
            continue
        core, parts, omitted = decode(row)
        for _, lift, previous in pending[1]:
            groups = (*parts, omitted[lift])
            roots = tuple(singles(group, 8) for group in groups)
            lower, upper = targets(core, groups)
            result, lower, upper, _ = fuse(lower, upper, OMISSIONS, (8,) * 8 + (7,) * 24, 7, 74, prover)
            assert result == 'open'
            started = process_time()
            before = tuple(surviving_counts(core, groups, marked=True))
            marked_cpu = process_time() - started
            times['marked'] += marked_cpu
            assert bool(before) == (previous == 'open')
            started = process_time()
            candidates = tuple(common(lower, upper, wings, roots, 7, (6, 7, 8) if prefilter else before))
            times['roster'] += process_time() - started
            if candidates:
                times['marked if roster first'] += marked_cpu
            after = tuple(count for count in before if count in candidates)
            stats['inputs'] += 1
            stats['old rejection' if not before else 'old survivor'] += 1
            stats['roster survivor' if candidates else 'roster rejection'] += 1
            stats['counts before'] += len(before)
            stats['counts after'] += len(after)
            if before and not after:
                stats['rejected'] += 1
                print('roster contradiction', index, lift, before)
        pending = next(selected, None)
    assert pending is None
    print('pilot', dict(stats), {stage: round(cpu, 5) for stage, cpu in times.items()}, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest='action', required=True)
    modes.add_parser('calibrate')
    run = modes.add_parser('pilot')
    run.add_argument('source', type=Path)
    run.add_argument('trace', type=Path)
    run.add_argument('--library', type=Path, default=Path('../r6_e11/m11_prop.so'))
    run.add_argument('--prefilter', action='store_true')
    args = parser.parse_args()
    if args.action == 'calibrate':
        calibrate()
    else:
        pilot(args.source, args.trace, args.library, args.prefilter)
