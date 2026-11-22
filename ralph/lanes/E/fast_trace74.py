#!/usr/bin/env python3
"""Pilot a native receipt checker without changing frozen producers or replays."""

import argparse
from collections import Counter
import ctypes
from itertools import combinations, product
from pathlib import Path

import fuse_shared74
from involution_cores import graph
import m11_prop
import order_shared74
import shared74_scan


class Checker:
    def __init__(self, path):
        self.library = ctypes.CDLL(str(path.resolve()))
        self.function = self.library.check_trace74
        pointer = ctypes.POINTER(ctypes.c_uint64)
        self.function.argtypes = [ctypes.c_int]*4 + [ctypes.c_uint64, pointer, ctypes.c_int, pointer, pointer]
        self.function.restype = ctypes.c_int

    def __call__(self, pinned, eligible, alpha, edges, result, terminal, steps):
        size = len(pinned)
        assert size == len(eligible) and 1 <= size <= 32 and 0 <= alpha <= 32 and 0 <= edges <= 496
        assert 0 <= result <= 5 and 0 <= terminal < 1 << 64 and len(steps) <= 496
        ranges = ((pinned, 1 << size), (eligible, 1 << size), (steps, 1 << 64))
        assert all(0 <= value < limit for rows, limit in ranges for value in rows)
        array = ctypes.c_uint64*size
        lower, upper = array(*pinned), array(*eligible)
        trace = (ctypes.c_uint64*len(steps))(*steps)
        assert self.function(size, alpha, edges, result, terminal, trace, len(steps), lower, upper)
        return list(lower), list(upper)


def check_controls(checker, prover):
    stats = Counter()
    original = m11_prop.proof_check
    def compare(lower, upper, alpha, edges, result, terminal, steps):
        def run(function):
            try:
                return function(lower, upper, alpha, edges, result, terminal, steps)
            except AssertionError:
                return None
        received = run(checker)
        assert received == run(original), (lower, upper, alpha, edges, result, terminal, steps)
        stats['accept' if received is not None else 'reject'] += 1
        return received

    for order in range(2, 5):
        pairs = tuple(combinations(range(order), 2))
        for states in product((0, 1, 2), repeat=len(pairs)):
            lower = graph(order, [pair for pair, state in zip(pairs, states) if state == 2])
            upper = graph(order, [pair for pair, state in zip(pairs, states) if state != 0])
            for alpha, edges in product(range(2, order+1), range(len(pairs)+1)):
                result, terminal, steps = prover.prove(lower, upper, alpha, edges)
                assert compare(lower, upper, alpha, edges, result, terminal, steps) is not None
                stats[f'verdict_{result}'] += 1
                compare(lower, upper, alpha, edges, (result+1)%6, terminal, steps)
                compare(lower, upper, alpha, edges, result, terminal^1, steps)
                if steps:
                    stats['nonempty'] += 1
                    compare(lower, upper, alpha, edges, result, terminal, (steps[0]^1024, *steps[1:]))
    assert all(stats[f'verdict_{code}'] for code in range(6)) and stats['nonempty'] and stats['reject']
    print('exhaustive native/Python comparison (symmetric bounds through order four):', dict(stats), flush=True)
    order_shared74.calibrate_marked()
    order_shared74.calibrate_fusion(prover)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lib', type=Path, default=Path('../r6_e11/m11_prop.so'))
    parser.add_argument('--checker', type=Path, default=Path('check_trace74.so'))
    sub = parser.add_subparsers(dest='mode', required=True)
    sub.add_parser('calibrate')
    for action in ('scan', 'replay'):
        command = sub.add_parser(action)
        command.add_argument('cover', type=Path)
        command.add_argument('receipt', type=Path)
    args = parser.parse_args()
    proof = Checker(args.checker)
    prover = m11_prop.Prover(args.lib)
    for module in (fuse_shared74, shared74_scan, order_shared74):
        assert module.proof_check is m11_prop.proof_check
        module.proof_check = proof
    if args.mode == 'calibrate':
        check_controls(proof, prover)
    elif args.mode == 'scan':
        order_shared74.scan(args.cover, args.receipt, prover, ('fused', 'marked'))
    else:
        order_shared74.replay(args.cover, args.receipt, prover)


if __name__ == '__main__':
    main()
