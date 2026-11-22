#!/usr/bin/env python3
"""Measure exact labelled-window query reuse without changing the scanner."""

import argparse
from functools import lru_cache
from pathlib import Path

from fuse_shared74 import calibration as calibrate_fusion
from m11_prop import Prover, calibration as calibrate_window
from order_shared74 import scan


class MemoProver:
    def __init__(self, prover, capacity):
        self.cached = lru_cache(maxsize=capacity)(prover.prove)

    def prove(self, pinned, eligible, alpha, edges):
        return self.cached(tuple(pinned), tuple(eligible), alpha, edges)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lib', type=Path, default=Path('../r6_e11/m11_prop.so'))
    parser.add_argument('--capacity', type=int, default=65536)
    modes = parser.add_subparsers(dest='mode', required=True)
    modes.add_parser('calibrate')
    scanner = modes.add_parser('scan')
    scanner.add_argument('cover', type=Path)
    scanner.add_argument('receipt', type=Path)
    args = parser.parse_args()
    assert args.capacity > 0
    prover = MemoProver(Prover(args.lib), args.capacity)
    if args.mode == 'calibrate':
        calibrate_window(prover)
        calibrate_fusion(prover)
        misses = prover.cached.cache_info().misses
        calibrate_fusion(prover)
        assert misses == prover.cached.cache_info().misses
    else:
        scan(args.cover, args.receipt, prover, ('fused', 'marked'))
    print(prover.cached.cache_info(), flush=True)


if __name__ == '__main__':
    main()
