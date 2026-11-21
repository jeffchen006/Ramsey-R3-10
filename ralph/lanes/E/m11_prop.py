#!/usr/bin/env python3
"""Propagate forced graph edges; separately verify every witness trace."""

import argparse
from collections import Counter
import ctypes
from itertools import combinations, product
import json
from pathlib import Path

from cubic32 import pin_graph
from involution_cores import bits, graph
from involution_sat import from_graph6


def targets(core, groups):
    lower, parts = pin_graph(core, groups)
    upper = list(lower)
    for first, second in combinations(parts, 2):
        for left, right in product(first, second):
            if not lower[left] & lower[right]:
                upper[left] |= 1 << right
                upper[right] |= 1 << left
    return lower, upper


def proof_check(pinned, eligible, alpha, edge_target, result, terminal, steps):
    lower = list(pinned)
    upper = list(eligible)
    order = len(pinned)

    def update():
        degree = tuple(row.bit_count() for row in lower)
        low = sum(degree)//2
        if low > edge_target:
            return 2
        if any(lower[left] & lower[right] for left in range(order) for right in bits(lower[left])):
            return 3
        if max(degree) > alpha:
            return 4
        if low == edge_target:
            upper[:] = lower
        else:
            for left in range(order):
                for right in bits(upper[left] & ~lower[left] & ~((1 << (left+1))-1)):
                    if max(degree[left], degree[right]) == alpha or lower[left] & lower[right]:
                        upper[left] ^= 1 << right
                        upper[right] ^= 1 << left
        return 5 if sum(row.bit_count() for row in upper)//2 < edge_target else 0

    for step in steps:
        assert update() == 0
        right, left, witness = step & 31, step >> 5 & 31, step >> 10
        assert left < right < order and witness < 1 << order
        endpoints = (1 << left) | (1 << right)
        assert witness & endpoints == endpoints and witness.bit_count() == alpha+1
        assert upper[left] >> right & 1 and not lower[left] >> right & 1
        assert all(not upper[actor] & (witness & ~(endpoints if endpoints >> actor & 1 else 0))
                   for actor in bits(witness))
        lower[left] |= 1 << right
        lower[right] |= 1 << left
    bound = update()
    if result == 1:
        assert bound == 0 and 0 < terminal < 1 << order and terminal.bit_count() == alpha+1
        assert all(not upper[actor] & terminal for actor in bits(terminal))
    elif result:
        assert bound == result and terminal == 0
    else:
        assert bound == 0 and terminal == 0
    return lower, upper


class Prover:
    def __init__(self, library):
        self.lib = ctypes.CDLL(str(library.resolve()))
        self.func = self.lib.m11_prove
        bitset_ptr = ctypes.POINTER(ctypes.c_uint64)
        self.func.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, bitset_ptr, bitset_ptr,
                              bitset_ptr, ctypes.POINTER(ctypes.c_int), bitset_ptr]
        self.func.restype = ctypes.c_int

    def prove(self, pinned, eligible, alpha, edge_target):
        order = len(pinned)
        steps = (ctypes.c_uint64 * 496)()
        terminal = ctypes.c_uint64()
        length = ctypes.c_int()
        array = ctypes.c_uint64 * order
        result = self.func(order, alpha, edge_target, array(*pinned), array(*eligible), steps,
                           ctypes.byref(length), ctypes.byref(terminal))
        assert 0 <= result <= 5 and 0 <= length.value <= len(steps)
        return result, terminal.value, tuple(steps[:length.value])


def calibration(prover):
    core = graph(1, [])
    stats = Counter()
    for groups in (((1,), (0,), (0,)), ((1, 0), (0,), (0, 0)), ((1, 0), (1,), (0, 0)),
                   ((0,), (0, 0), (0, 0, 0))):
        lower, upper = targets(core, groups)
        order = len(lower)
        for alpha in (2, 3, 4):
            possible = [(left, right) for left, right in combinations(range(order), 2)
                        if upper[left] >> right & 1 and not lower[left] >> right & 1]
            pinned = [(left, right) for left, right in combinations(range(order), 2) if lower[left] >> right & 1]
            count = Counter()
            for picked in product((False, True), repeat=len(possible)):
                edges = set(pinned) | {edge for edge, use in zip(possible, picked) if use}
                if any(all(pair in edges for pair in combinations(subset, 2))
                       for subset in combinations(range(order), 3)):
                    continue
                if any(all(pair not in edges for pair in combinations(subset, 2))
                       for subset in combinations(range(order), alpha+1)):
                    continue
                count[len(edges)] += 1
            for limit in range(2, min(11, len(possible)+len(pinned)+2)):
                trace = prover.prove(lower, upper, alpha, limit)
                proof_check(lower, upper, alpha, limit, *trace)
                assert not trace[0] or not count[limit]
                stats['controls'] += 1
                stats['positive'] += bool(count[limit])
                stats['refuted'] += bool(trace[0])
    assert stats['positive'] and stats['refuted']
    print('independent exact small control:', dict(stats), flush=True)


def scan_file(prover, src, out, projection_only=False):
    stats = Counter()
    for index, text in enumerate(src.open(encoding='ascii')):
        key, profile, parts, lifts = json.loads(text)
        core = from_graph6(key)
        lower, upper = targets(core, parts)
        trace = prover.prove(lower, upper, 7, 74)
        proof_check(lower, upper, 7, 74, *trace)
        stats['projection'] += 1
        if trace[0]:
            stats[f'proof.{trace[0]}'] += 1
            stats['projection_refuted'] += 1
            print(json.dumps((index, -1, -1, trace), separators=(',', ':')), file=out)
            continue
        if projection_only:
            stats['open_projection'] += 1
            print(json.dumps((index, -1, -1, None), separators=(',', ':')), file=out)
            continue
        for lift, omitted in enumerate(lifts):
            stats['lift'] += 1
            full = tuple(parts) + (omitted,)
            for index_omit in range(3):
                subs = full[:index_omit] + full[index_omit+1:]
                lower, upper = targets(core, subs)
                trace = prover.prove(lower, upper, 7, 74)
                if trace[0]:
                    proof_check(lower, upper, 7, 74, *trace)
                    stats['lift_refuted'] += 1
                    stats[f'proof.{trace[0]}'] += 1
                    print(json.dumps((index, lift, index_omit, trace), separators=(',', ':')), file=out)
                    break
            else:
                stats['open'] += 1
                print(json.dumps((index, lift, -1, None), separators=(',', ':')), file=out)
    print('scan:', dict(stats), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('library', type=Path)
    sub = parser.add_subparsers(dest='mode', required=True)
    sub.add_parser('calibrate')
    scan = sub.add_parser('scan')
    scan.add_argument('src', type=Path)
    scan.add_argument('out', type=Path)
    scan.add_argument('--projection-only', action='store_true')
    args = parser.parse_args()
    prover = Prover(args.library)
    if args.mode == 'calibrate':
        calibration(prover)
    else:
        with args.out.open('w', encoding='ascii') as out:
            scan_file(prover, args.src, out, args.projection_only)


if __name__ == '__main__':
    main()
